#!/usr/bin/env python3
"""Forecast rating and viewing completion separately from versioned MAL data."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import re
from hashlib import sha256
from statistics import fmean

from evaluate import (
    ROOT, V1, blob_sha, build_baselines, clip, evidence_records, evidence_weights,
    factual_features, fit_predict, franchise_groups, grouped_folds, load, metrics,
    paired_group_interval, ranked_probability_score, score_distribution,
)


# Each mechanism requires two cues within one brief passage. Broad genre tags,
# studio names and the viewer's recorded reaction are deliberately absent.
MECHANISMS = {
    "relationship_changes_options": (
        r"relation|vänskap|förtroende|partnerskap|kärlek|familjeband|bandet",
        r"påverkar|omförhandl|ompröv|förändrar|förskjuter|tvingar|komplicerar|handlingsutrymme",
        "relationship",
    ),
    "choice_has_consequences": (
        r"beslut|valet|valen|vägval|relationsval|offra|uppoffr|romantiska val|tvingas välja",
        r"konsekvens|förändr|pris|förlust|lojalitet|ansvar|svika|offra",
        "consequences",
    ),
    "bond_collides_with_world": (
        r"gemenskap|tillhörighet|trygghet|beroende|förtrolighet|vänskap|familjeband",
        r"hot|utanförskap|utsatt|kontroll|fördom|omvärld|förbjud|hemlig|villkor",
        "perspective",
    ),
    "episodes_accumulate": (
        r"episodisk|fristående|enskilda fall|olika fall|avsnitt",
        r"sammanhängande|gradvis|stegvis|successivt|kontinuitet|växande",
        "progression",
    ),
    "episodic_without_central_arc": (
        r"episodisk|fristående|veckans fall|separata episoder",
        r"utan (en |någon )?(central|övergripande|fortlöpande)|snarare än en (längre |enda )?sammanhängande",
        "format",
    ),
    "premise_changes_relationship": (
        r"magi|övernaturlig|premiss|förmåga|regel|förvandl|identitetsbyte|minnesförlust",
        r"relation|vänskap|tillit|närhet|familj|känslor|förtroende",
        "premise",
    ),
    "narrative_reset": (
        r"återställ|börjar om|återvänder till.{0,24}utgångspunkt|nollställ|alternativa rutt",
        r"tidsloop|episod|konsekvens|minne|minnes|relation|berättels|routes",
        "consequences",
    ),
}
SOURCE_FIELDS = ("synopsis", "character_dynamics", "pacing_and_structure", "distinctive_features")
LABELS = ("B0", "B1", "B2", "v1_evidence", "mechanisms", "mechanisms_evidence")
PINNED = {
    "anime": "c8a39c53c2e39d6107cdcdbf8f45c01c59490520",
    "profiles": "65ee46c5d708cb696fa1378977d4c15f02258f55",
}


def feature_passages(brief):
    hits = {}
    if not brief:
        return hits
    for field in SOURCE_FIELDS:
        for passage in re.split(r"(?<=[.!?;])\s+", brief.get(field) or ""):
            for name, (first, second, _) in MECHANISMS.items():
                if name not in hits and re.search(first, passage, re.I) and re.search(second, passage, re.I):
                    hits[name] = {"field": field, "passage": passage}
    return hits


def fit_rating(training, cases, features, broad_features, evidence):
    previous, _ = fit_predict(training, cases, broad_features, evidence)
    train_baseline, _ = build_baselines(training, training)
    residuals = [row["user_score"] - value
                 for row, value in zip(training, train_baseline["mal_genre_shrunk"])]
    training_ids = {row["mal_id"] for row in training}
    anchors = evidence_weights(evidence, training_ids)
    output = {key: previous[key] for key in ("B0", "B1", "B2")}
    output["v1_evidence"] = previous["B2_brief_evidence"]
    for name, active in (("mechanisms", {}), ("mechanisms_evidence", anchors)):
        # Fit jointly so common mechanisms cannot add their full marginal
        # effects twice. Shrink the coefficient towards zero.
        effects = dict.fromkeys(MECHANISMS, 0.0)
        remaining = residuals.copy()
        observations = defaultdict(list)
        for index, row in enumerate(training):
            mal_id = row["mal_id"]
            matches = features[mal_id]
            weight = max((active.get((mal_id, MECHANISMS[key][2]), 1)
                          for key in matches), default=1)
            for mechanism in matches:
                observations[mechanism].append((index, weight))
        for _ in range(12):
            for mechanism in MECHANISMS:
                observed = observations[mechanism]
                weighted_error = sum(weight * (remaining[index] + effects[mechanism])
                                     for index, weight in observed)
                estimate = weighted_error / (60 + sum(weight for _, weight in observed))
                change = estimate - effects[mechanism]
                effects[mechanism] = estimate
                for index, _ in observed:
                    remaining[index] -= change
        output[name] = [
            clip(base + clip(sum(effects[k] for k in features[row["mal_id"]]), -0.5, 0.5))
            for row, base in zip(cases, output["B2"])
        ]
    return output


def finish_bucket(row):
    if row["media_type"] != "tv":
        return "non_tv"
    count = row.get("num_episodes") or 0
    if count <= 0:
        return "tv_unknown"
    if count <= 13:
        return "tv_up_to_13"
    if count <= 26:
        return "tv_14_to_26"
    return "tv_over_26"


def logit(p):
    return math.log(p / (1 - p))


def finish_predictions(training, cases, features):
    """Estimate completed vs dropped in the observed, previously started cohort."""
    prior = (sum(row["finished"] for row in training) + 1) / (len(training) + 2)
    totals = defaultdict(list)
    for row in training:
        totals[finish_bucket(row)].append(row["finished"])
    probabilities = {key: (sum(values) + 24 * prior) / (len(values) + 24)
                     for key, values in totals.items()}

    def baseline(row):
        return probabilities.get(finish_bucket(row), prior)

    sums = defaultdict(float)
    counts = defaultdict(int)
    for row in training:
        for key in features[row["mal_id"]]:
            sums[key] += row["finished"] - baseline(row)
            counts[key] += 1
    result = {"format_baseline": [], "format_and_mechanisms": []}
    for row in cases:
        base = baseline(row)
        bumps = [sums[key] / (counts[key] + 30) for key in features[row["mal_id"]]]
        # A small correction in probability space converted to log odds
        # at the local baseline. Strong shrinkage reflects few observed drops.
        bump = fmean(bumps) if bumps else 0
        adjustment = bump / (base * (1 - base))
        result["format_baseline"].append(base)
        result["format_and_mechanisms"].append(1 / (1 + math.exp(-logit(base) - adjustment)))
    return result


def rating_cv(training, features, broad_features, evidence):
    groups = franchise_groups(training)
    held_out = []
    for train, test in grouped_folds(training, groups, 20261117):
        predictions = fit_rating(train, test, features, broad_features, evidence)
        inner = rating_residuals(train, features, broad_features, evidence)
        calibrated = ("B2", "mechanisms_evidence")
        for i, row in enumerate(test):
            outcome = {"mal_id": row["mal_id"], "actual": row["user_score"]}
            outcome.update({name: values[i] for name, values in predictions.items()})
            for name in calibrated:
                pmf = score_distribution(outcome[name], inner[name])
                outcome[f"rps_{name}"] = ranked_probability_score(outcome["actual"], pmf)
            held_out.append(outcome)
    assert len({row["mal_id"] for row in held_out}) == len(training)
    subsets = {
        "all": held_out,
        "high_9_10": [row for row in held_out if row["actual"] >= 9],
        "low_1_6": [row for row in held_out if row["actual"] <= 6],
    }
    return {
        "metrics": {key: {
            name: metrics([row["actual"] for row in subset], [row[name] for row in subset])
            for name in LABELS
        } for key, subset in subsets.items()},
        "rps": {name: fmean(row[f"rps_{name}"] for row in held_out)
                for name in ("B2", "mechanisms_evidence")},
        "paired_improvement_over_b2": {
            name: paired_group_interval(held_out, groups, "B2", name)
            for name in ("v1_evidence", "mechanisms", "mechanisms_evidence")
        },
        "mechanism_coverage": {
            key: sum(key in features[row["mal_id"]] for row in training) for key in MECHANISMS
        },
    }


def rating_residuals(training, features, broad_features, evidence):
    groups = franchise_groups(training)
    result = defaultdict(list)
    for train, held_out in grouped_folds(training, groups, 20261118):
        predicts = fit_rating(train, held_out, features, broad_features, evidence)
        for name, values in predicts.items():
            result[name].extend(row["user_score"] - value for row, value in zip(held_out, values))
    return result


def completion_cv(training, features):
    groups = franchise_groups(training)
    held_out = defaultdict(list)
    for train, test in grouped_folds(training, groups, 20261117):
        for name, forecast in finish_predictions(train, test, features).items():
            held_out[name].extend((row["finished"], value) for row, value in zip(test, forecast))
    assert all(len(rows) == len(training) for rows in held_out.values())
    return {
        "n": len(training),
        "n_dropped": sum(not row["finished"] for row in training),
        "metrics": {
            name: {
                "brier": fmean((y - p) ** 2 for y, p in rows),
                "log_loss": -fmean(math.log(p if y else 1 - p) for y, p in rows),
            } for name, rows in held_out.items()
        },
    }


def build_data(args):
    rubric = load(ROOT / "evidence_map.json")
    manifest = load(args.manifest)
    excluded = set(manifest["holdout_mal_ids"])
    if sha256(args.training.read_bytes()).hexdigest() != rubric["training_sha256"]:
        raise ValueError("Training must use the reviewed v1 export")
    if blob_sha(args.evidence) != rubric["preference_git_blob_sha"]:
        raise ValueError("Preference evidence must use the reviewed blob")
    for key, digest in PINNED.items():
        if blob_sha(getattr(args, key)) != digest:
            raise ValueError(f"Use the pinned {key} snapshot for training")
    evidence = evidence_records(load(args.evidence), rubric, excluded)
    training = load(args.training)["rows"]
    anime = {row["mal_id"]: row for row in load(args.anime)["anime"]}
    profiles = load(args.profiles)["profiles"]
    ids = {row["mal_id"] for row in training}
    if ids & excluded or len(ids) != len(training):
        raise ValueError("Unexpected training IDs")
    # External or uncertain starts must not influence the abandonment target.
    ambiguous_drop = {mal_id for record in evidence
                      if record["kind"] == "dropped" and record["qualification"]
                      for mal_id in record["ids"]}
    completion = [
        dict(row, finished=row["status"] == "completed")
        for mal_id, row in anime.items()
        if mal_id in ids or (
            mal_id not in excluded and mal_id not in ambiguous_drop
            and row["status"] == "dropped" and (row.get("episodes_watched") or 0) > 0
        )
    ]
    # Use the exact v1 rating brief for its cases. New briefs, dropped titles
    # and the live PTW target are not added to the rating training labels.
    training_briefs = {row["mal_id"]: row["brief"] for row in training}
    relevant = ids | {row["mal_id"] for row in completion}
    features = {mal_id: feature_passages(training_briefs.get(mal_id, profiles.get(str(mal_id))))
                for mal_id in relevant}
    broad_features = {row["mal_id"]: factual_features(row) for row in training}
    return training, completion, evidence, features, broad_features


def forecast(case, training, completion, evidence, features, broad_features):
    mal_id = case["mal_id"]
    passages = feature_passages(case.get("brief"))
    features = {**features, mal_id: passages}
    output = {
        "mal_id": mal_id, "title": case["title"], "observed_mechanism_cues": passages,
        "completion_if_started": {
            name: values[0] for name, values in finish_predictions(completion, [case], features).items()
        },
        "rating_given_completed": None,
        "qualification": "Exploratory. Completion uses previously started, resolved list entries.",
    }
    if not isinstance(case.get("mal_mean_score"), (float, int)):
        return output
    broad_features = {**broad_features, mal_id: factual_features(case)}
    points = fit_rating(training, [case], features, broad_features, evidence)
    residuals = rating_residuals(training, features, broad_features, evidence)
    output["rating_given_completed"] = {
        name: {"point": points[name][0], "probabilities_1_to_10": score_distribution(points[name][0], residuals[name])}
        for name in ("B2", "mechanisms_evidence")
    }
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training", type=Path, default=V1 / "training.json")
    parser.add_argument("--manifest", type=Path, default=V1 / "manifest.json")
    for key in ("anime", "profiles", "evidence"):
        parser.add_argument(f"--{key}", type=Path, required=True)
    parser.add_argument("--target-id", type=int)
    parser.add_argument("--current-anime", type=Path)
    parser.add_argument("--current-profiles", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if (args.current_anime is None) != (args.current_profiles is None):
        parser.error("Supply both current anime and current profiles, or use the pinned snapshots")
    training, completion, evidence, features, broad_features = build_data(args)
    if args.target_id is None:
        result = {
            "type": "retrospective_training_only_cv",
            "rating_given_completed": rating_cv(training, features, broad_features, evidence),
            "completion_if_started": completion_cv(completion, features),
        }
    else:
        catalog = load(args.current_anime or args.anime)["anime"]
        targets = [row for row in catalog if row["mal_id"] == args.target_id and row["status"] == "plan_to_watch"]
        if len(targets) != 1 or any(row["mal_id"] == args.target_id for row in completion):
            parser.error("Target must be a unique PTW entry outside both training cohorts")
        if args.target_id in load(args.manifest)["holdout_mal_ids"]:
            parser.error("The v1 holdout is retired")
        brief = load(args.current_profiles or args.profiles)["profiles"].get(str(args.target_id))
        if brief and brief["mal_id"] != args.target_id:
            parser.error("Brief MAL ID differs from target")
        result = forecast(dict(targets[0], brief=brief), training, completion, evidence, features, broad_features)

    data = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.write_text(data, encoding="utf-8")
    else:
        print(data)


if __name__ == "__main__":
    main()
