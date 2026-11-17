#!/usr/bin/env python3
"""Evaluate a tagged evidence model on the 424 training titles from MAL v1."""
import argparse
from collections import defaultdict
from hashlib import sha1, sha256
import json
import math
from pathlib import Path
import random
import re
from statistics import fmean
import sys
import unicodedata

ROOT = Path(__file__).resolve().parent
V1 = ROOT.parent / "mal_blindtest_v1"
sys.path.insert(0, str(V1))
from score import build_baselines, clip, metrics  # noqa: E402


# These are observable description cues. Presence is not a quality judgment.
CUES = {
    "progression": r"progression|framåtdriv|upprep|stillastå|långsam|lågmäld|stegvis|utvecklingsbåg",
    "relationship": r"relations?|förhålland|vänskap|förtroende|familjeband|gruppdynamik",
    "consequences": r"konsekvens|upplösning|slutpunkt|uppoffring|återställ|oåterkalle|moraliska val",
    "premise": r"premiss|absurd|vardagsrealism|realistisk|förankr|grepp som",
    "tone": r"tonal|tonväxl|tonskift|satir|melankol|komedi.{0,36}allvar|växlar mellan",
    "perspective": r"subjektiv|perspektiv|utsatt|omsorg|gemenskap|sårbar|anförtror",
    "style": r"stiliser|visuell|bildspråk|animation|dialogtung|språklig|snabba klipp",
    "format": r"episodisk|fristående|block|bågar|sidohistor|bonusavsnitt|jubileum",
}
BRIEF_FIELDS = (
    "synopsis", "themes", "tone", "pacing_and_structure", "character_dynamics",
    "distinctive_features", "comparison_cues",
)
BASELINES = {"median": "B0", "mal_calibrated": "B1", "mal_genre_shrunk": "B2"}
FORECASTS = (*BASELINES.values(), "B2_brief", "B2_brief_evidence")
FOLDS = 5


def load(path):
    return json.loads(path.read_bytes())


def blob_sha(path):
    raw = path.read_bytes()
    return sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def evidence_records(source, mapping, retired_ids):
    items = source["questions"]["items"]
    items = {item["question_id"]: item for item in (
        items.values() if isinstance(items, dict) else items
    )}
    saved_statements = source["insights"]["explicit_user_qualitative_evidence"]
    statements = {item["id"]: item for item in (
        saved_statements.values() if isinstance(saved_statements, dict) else saved_statements
    )}
    qualifications = mapping["qualifications"]
    records = []
    for key, dimensions in mapping["questions"].items():
        item = items[key]
        answer = item["answer"]
        if item["status"] != "answered" or not answer:
            raise ValueError(f"Missing answer for {key}")
        if isinstance(answer, str):
            raw = item.get("raw_answer") or answer
            selected = [item.get("selected_option") or answer]
            free_text = None
        else:
            raw = answer.get("raw_response")
            selected = answer.get("selected_options") or []
            free_text = answer.get("free_text")
        kind = "dropped" if key.startswith("dropped-") else "completed"
        records.append(dict(id=key, ids=[item["mal_id"]], kind=kind,
                            raw=raw, selected=selected, free_text=free_text,
                            dimensions=dimensions, qualification=qualifications.get(key)))
    for key, dimensions in mapping["statements"].items():
        item = statements[key]
        records.append(dict(id=key, ids=item["mal_ids"], kind="statement",
                            raw=item["verbatim"], dimensions=dimensions,
                            qualification=qualifications.get(key)))
    if any(set(item["ids"]) & retired_ids for item in records):
        raise ValueError("Evidence references the retired holdout")
    if any(not set(item["dimensions"]) <= CUES.keys() for item in records):
        raise ValueError("Evidence mapping has an unknown dimension")
    return records


def factual_features(row):
    brief = row.get("brief") or {}
    # Keep factual descriptions separate from raw reactions, scores and MAL tags.
    values = [brief.get(key) for key in BRIEF_FIELDS]
    description = " ".join(
        " ".join(value) if isinstance(value, list) else value or ""
        for value in values
    ).casefold()
    return {dimension for dimension, cue in CUES.items() if re.search(cue, description)}


def title_tokens(title):
    normalized = unicodedata.normalize("NFKD", title.casefold())
    without_accents = "".join(c for c in normalized if not unicodedata.combining(c))
    return tuple(re.findall(r"[a-z0-9]+", without_accents))


def franchise_groups(rows):
    """Group exact three-word prefixes and full title prefixes transitively."""
    tokens = [title_tokens(row["title"]) for row in rows]
    parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            i = parent[i]
        return i

    for i, left in enumerate(tokens):
        if not left:
            continue
        for j in range(i):
            right = tokens[j]
            if not right:
                continue
            shared_length = min(3, len(left), len(right))
            if left[:shared_length] == right[:shared_length]:
                parent[find(i)] = find(j)
    return {row["mal_id"]: rows[find(i)]["mal_id"] for i, row in enumerate(rows)}


def grouped_folds(rows, groups, seed):
    siblings = defaultdict(list)
    for row in rows:
        siblings[groups[row["mal_id"]]].append(row)
    batches = list(siblings.values())
    random.Random(seed).shuffle(batches)
    folds = [[] for _ in range(FOLDS)]
    for batch in sorted(batches, key=len, reverse=True):
        min(folds, key=len).extend(batch)
    for i, test in enumerate(folds):
        train = [row for j, fold in enumerate(folds) if j != i for row in fold]
        yield train, test


def evidence_weights(records, training_ids):
    weights = {}
    for item in records:
        if item["kind"] == "dropped" or item["qualification"] or not set(item["ids"]) <= training_ids:
            continue
        # Multiple statements on one title should not multiply its influence.
        for mal_id in item["ids"]:
            for dimension in item["dimensions"]:
                weight = 3 if item["kind"] == "statement" else 2
                key = (mal_id, dimension)
                weights[key] = max(weights.get(key, 1), weight)
    return weights


def corrections(train, baselines, features, weights):
    sums = defaultdict(float)
    denominators = defaultdict(float)
    for row, baseline in zip(train, baselines):
        mal_id = row["mal_id"]
        residual = row["user_score"] - baseline
        for dimension in features[mal_id]:
            weight = weights.get((mal_id, dimension), 1)
            sums[dimension] += weight * residual
            denominators[dimension] += weight
    return {key: sums[key] / (denominators[key] + 20) for key in sums}


def fit_predict(train, cases, features, records):
    joined_baselines, _ = build_baselines(train, train + cases)
    split = len(train)
    train_b2 = joined_baselines["mal_genre_shrunk"][:split]
    predictions = {BASELINES[key]: values[split:] for key, values in joined_baselines.items()}
    weights = evidence_weights(records, {row["mal_id"] for row in train})
    for model, active_weights in (("B2_brief", {}), ("B2_brief_evidence", weights)):
        effects = corrections(train, train_b2, features, active_weights)
        adjusted = []
        for row, b2 in zip(cases, predictions["B2"]):
            selected = [effects.get(key, 0) for key in sorted(features[row["mal_id"]])]
            adjustment = clip(fmean(selected), -0.5, 0.5) if selected else 0
            adjusted.append(clip(b2 + adjustment))
        predictions[model] = adjusted
    return predictions, len(weights)


def score_distribution(point, residuals):
    """Return a PMF on integer ratings from training-fold residuals."""
    counts = [0] * 10
    for residual in residuals:
        bucket = math.floor(clip(point + residual) + 0.5)
        counts[bucket - 1] += 1
    return [count / len(residuals) for count in counts]


def ranked_probability_score(actual, pmf):
    cumulative = 0
    errors = []
    for cutoff, probability in enumerate(pmf[:-1], start=1):
        cumulative += probability
        errors.append((cumulative - (actual <= cutoff)) ** 2)
    return fmean(errors)


def paired_group_interval(held_out, groups, baseline, model):
    errors = defaultdict(list)
    for row in held_out:
        actual = row["actual"]
        delta = abs(actual - row[baseline]) - abs(actual - row[model])
        errors[groups[row["mal_id"]]].append(delta)
    buckets = [(sum(values), len(values)) for values in errors.values()]
    rng = random.Random(20261117)
    replicates = []
    for _ in range(2000):
        sample = rng.choices(buckets, k=len(buckets))
        replicates.append(sum(total for total, _ in sample) / sum(n for _, n in sample))
    replicates.sort()
    return {
        "mean": fmean(delta for values in errors.values() for delta in values),
        "interval_95": [replicates[49], replicates[1950]],
    }


def cross_validate(rows, evidence):
    groups = franchise_groups(rows)
    features = {row["mal_id"]: factual_features(row) for row in rows}
    held_out = []
    fold_sizes = []
    calibrated = ("B2", "B2_brief_evidence")
    for fold, (train, test) in enumerate(grouped_folds(rows, groups, 20261117)):
        assert {groups[row["mal_id"]] for row in train}.isdisjoint(
            groups[row["mal_id"]] for row in test
        )
        predictions, anchors = fit_predict(train, test, features, evidence)
        residuals = defaultdict(list)
        for inner_train, inner_test in grouped_folds(train, groups, 20261118 + fold):
            inner_predictions, _ = fit_predict(inner_train, inner_test, features, evidence)
            for model in calibrated:
                residuals[model].extend(row["user_score"] - prediction
                                        for row, prediction in zip(inner_test, inner_predictions[model]))
        for i, row in enumerate(test):
            result = {"mal_id": row["mal_id"], "actual": row["user_score"]}
            result.update({model: values[i] for model, values in predictions.items()})
            for model in calibrated:
                pmf = score_distribution(result[model], residuals[model])
                result[f"{model}_pmf"] = pmf
                result[f"{model}_rps"] = ranked_probability_score(row["user_score"], pmf)
            held_out.append(result)
        fold_sizes.append({"train": len(train), "test": len(test), "active_title_dimension_weights": anchors})

    assert len({row["mal_id"] for row in held_out}) == len(rows) == len(held_out)
    slices = {
        "all": held_out,
        "high_9_10": [row for row in held_out if row["actual"] >= 9],
        "low_1_6": [row for row in held_out if row["actual"] <= 6],
        "mal_surprise": [row for row in held_out if abs(row["actual"] - row["B1"]) >= 1.5],
    }
    return {
        "experiment": "retrospective_grouped_training_cv",
        "groups": len(set(groups.values())),
        "folds": fold_sizes,
        "metrics": {label: {
            model: metrics([row["actual"] for row in sample], [row[model] for row in sample])
            for model in FORECASTS
        } for label, sample in slices.items()},
        "rps": {model: fmean(row[f"{model}_rps"] for row in held_out) for model in calibrated},
        "paired_b2_improvement": {
            model: paired_group_interval(held_out, groups, "B2", model)
            for model in ("B2_brief", "B2_brief_evidence")
        },
        "paired_evidence_increment": paired_group_interval(
            held_out, groups, "B2_brief", "B2_brief_evidence"
        ),
        "largest_errors": sorted(
            ({"mal_id": row["mal_id"], "actual": row["actual"], "B2": row["B2"],
              "prediction": row["B2_brief_evidence"]} for row in held_out),
            key=lambda row: abs(row["actual"] - row["prediction"]), reverse=True,
        )[:8],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training", type=Path, default=V1 / "training.json")
    parser.add_argument("--manifest", type=Path, default=V1 / "manifest.json")
    parser.add_argument("--evidence", type=Path, default=ROOT.parent.parent / "anime_preference_learning.json")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    mapping = load(ROOT / "evidence_map.json")
    manifest = load(args.manifest)
    retired_ids = set(manifest["holdout_mal_ids"])
    if sha256(args.training.read_bytes()).hexdigest() != mapping["training_sha256"]:
        raise ValueError("Training file differs from the reviewed v1 export")
    if blob_sha(args.evidence) != mapping["preference_git_blob_sha"]:
        raise ValueError("Use the pinned preference evidence blob")
    training = load(args.training)
    rows = training["rows"]
    ids = {row["mal_id"] for row in rows}
    if (len(ids) != len(rows) or len(ids) != manifest["counts"]["train_n"]
            or ids & retired_ids or any(not 1 <= row["user_score"] <= 10 for row in rows)):
        raise ValueError("Invalid completed-only training set")
    evidence = evidence_records(load(args.evidence), mapping, retired_ids)
    report = cross_validate(rows, evidence)
    report["evidence_inventory"] = {
        kind: sum(row["kind"] == kind for row in evidence)
        for kind in ("completed", "dropped", "statement")
    }
    # Abandonment clues are descriptive. Their reasons carry no point-rating weight.
    report["drop_evidence"] = {
        row["id"]: {"dimensions": row["dimensions"], "qualification": row["qualification"]}
        for row in evidence if row["kind"] == "dropped"
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
