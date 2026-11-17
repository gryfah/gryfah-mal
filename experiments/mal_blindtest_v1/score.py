#!/usr/bin/env python3
"""Score MAL blindtest v1 only AFTER predictions are sealed.
Stdlib only. Do not expose the frozen answer key to the predicting model.
"""
import argparse
import hashlib
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def clip(x, lo=1.0, hi=10.0):
    return max(lo, min(hi, float(x)))


def mean(values):
    return statistics.fmean(values) if values else None


def metrics(ys, ps):
    n = len(ys)
    if not n:
        return {"n": 0}
    errors = [abs(y - p) for y, p in zip(ys, ps)]
    squares = [(y - p) ** 2 for y, p in zip(ys, ps)]
    return {
        "n": n,
        "mae": round(mean(errors), 6),
        "rmse": round(math.sqrt(mean(squares)), 6),
        "within_1": round(sum(e <= 1.0 for e in errors) / n, 6),
        "within_0_5": round(sum(e <= 0.5 for e in errors) / n, 6),
    }


def rounded_class(x):
    # nearest integer; 6.5 rounds to 7, 7.5 rounds to 8
    return min(10, max(1, math.floor(x + 0.5)))


def precision_recall_f1(ys, ps, target):
    if target == "high_8_to_10":
        truth = [y >= 8 for y in ys]
        positive = [rounded_class(p) >= 8 for p in ps]
    else:
        truth = [y <= 6 for y in ys]
        positive = [rounded_class(p) <= 6 for p in ps]
    tp = sum(t and p for t, p in zip(truth, positive))
    fp = sum(not t and p for t, p in zip(truth, positive))
    fn = sum(t and not p for t, p in zip(truth, positive))
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "n_positive": sum(truth),
        "tp": tp, "fp": fp, "fn": fn,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
    }


def bootstrap_improvement(ys, model, baseline, iterations=2000):
    # Positive means model has *lower* absolute error than baseline.
    deltas = [abs(y - b) - abs(y - m) for y, m, b in zip(ys, model, baseline)]
    rng = random.Random(20261117)
    n = len(deltas)
    samples = []
    for _ in range(iterations):
        samples.append(sum(deltas[rng.randrange(n)] for _ in range(n)) / n)
    samples.sort()
    low = samples[math.floor(0.025 * (iterations - 1))]
    high = samples[math.ceil(0.975 * (iterations - 1))]
    return {
        "mean_improvement": round(mean(deltas), 6),
        "bootstrap_95pct": [round(low, 6), round(high, 6)],
        "n": n,
        "bootstrap_reps": iterations,
    }


def verify_git_blob_sha(raw, expected):
    header = f"blob {len(raw)}\0".encode("ascii")
    actual = hashlib.sha1(header + raw).hexdigest()
    if actual != expected:
        raise ValueError(f"Source mismatch: expected Git blob {expected}, got {actual}")


def build_baselines(training_rows, cases):
    scores = [float(x["user_score"]) for x in training_rows]
    global_median = statistics.median(scores)
    differences = [
        float(x["user_score"]) - float(x["mal_mean_score"])
        for x in training_rows
    ]
    offset = statistics.median(differences)

    tag_residuals = defaultdict(list)
    for x in training_rows:
        baseline = clip(float(x["mal_mean_score"]) + offset)
        residual = float(x["user_score"]) - baseline
        for genre in set(x.get("genres") or []):
            tag_residuals[genre].append(residual)
    corrections = {
        genre: sum(deltas) / (len(deltas) + 20.0)
        for genre, deltas in tag_residuals.items()
    }
    b0 = []
    b1 = []
    b2 = []
    for x in cases:
        val = float(x["mal_mean_score"])
        base = clip(val + offset)
        vals = [corrections[g] for g in set(x.get("genres") or [])
                if g in corrections]
        genre_correction = clip(mean(vals) or 0, -0.75, 0.75)
        b0.append(float(global_median))
        b1.append(base)
        b2.append(clip(base + genre_correction))
    return {
        "median": b0, "mal_calibrated": b1, "mal_genre_shrunk": b2,
    }, {"train_global_median": global_median,
        "train_mal_median_offset": offset,
        "genres_seen": len(corrections)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("predictions", help="Locked model predictions JSON")
    parser.add_argument("source", help="Frozen raw anime.json at pinned Git blob")
    parser.add_argument("--out", default=None, help="Optional results JSON path")
    parser.add_argument("--expected-predictions-sha256", default=None)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    manifest = read_json(root / "manifest.json")
    train = read_json(root / "training.json")
    blind = read_json(root / "blind_cases.json")
    prediction_path = Path(args.predictions)
    prediction_raw = prediction_path.read_bytes()
    prediction_sha = hashlib.sha256(prediction_raw).hexdigest()
    if args.expected_predictions_sha256 and args.expected_predictions_sha256.lower() != prediction_sha:
        raise ValueError("Predictions were modified after locking")

    prediction_file = json.loads(prediction_raw)
    expected_id = "mal_blindtest_v1"
    for item in (manifest, train, blind, prediction_file):
        if item.get("experiment_id") != expected_id:
            raise ValueError("Experiment ID mismatch")

    cases = blind["cases"]
    train_rows = train["rows"]
    case_ids = [int(x["mal_id"]) for x in cases]
    train_ids = [int(x["mal_id"]) for x in train_rows]
    if (len(cases) != manifest["counts"]["test_n"] or
            len(train_rows) != manifest["counts"]["train_n"] or
            len(case_ids) != len(set(case_ids)) or
            len(train_ids) != len(set(train_ids)) or
            set(case_ids).intersection(train_ids)):
        raise ValueError("Dataset validation failed")
    if case_ids != manifest["holdout_mal_ids"]:
        raise ValueError("Manifest/case order mismatch")
    if any("user_score" in x or "score_minus_mal" in x or
           "consensus_residual" in x for x in cases):
        raise ValueError("Blind cases contain score leakage")

    pred_rows = prediction_file.get("predictions")
    if not isinstance(pred_rows, list) or len(pred_rows) != len(cases):
        raise ValueError("Model must predict all blind cases exactly once")
    predictions = {}
    for x in pred_rows:
        mid = int(x["mal_id"])
        val = x.get("predicted_score")
        if mid in predictions or type(val) not in (int, float) or not math.isfinite(val) or not 1 <= val <= 10:
            raise ValueError(f"Invalid or duplicated prediction for {mid}")
        if x.get("confidence") not in ("low", "medium", "high"):
            raise ValueError(f"Invalid confidence for {mid}")
        if not isinstance(x.get("reason"), str) or not x["reason"].strip():
            raise ValueError(f"Missing pre-facit explanation for {mid}")
        predictions[mid] = x
    if set(predictions) != set(case_ids):
        raise ValueError("Missing/unexpected test IDs")

    source_raw = Path(args.source).read_bytes()
    verify_git_blob_sha(source_raw, manifest["source_git_blob_shas"]["anime_json"])
    source = json.loads(source_raw)
    scores = {
        int(x["mal_id"]): x for x in source["anime"]
        if x.get("status") == "completed"
    }
    if any(mid not in scores or not (1 <= scores[mid]["score"] <= 10)
           for mid in case_ids):
        raise ValueError("Missing completed labels in pinned source")

    ys = [float(scores[mid]["score"]) for mid in case_ids]
    model = [float(predictions[mid]["predicted_score"]) for mid in case_ids]
    baselines, params = build_baselines(train_rows, cases)
    evaluated = {"model": metrics(ys, model)}
    for name, vals in baselines.items():
        evaluated[name] = metrics(ys, vals)

    classifications = {
        name: {
            "high_8_to_10": precision_recall_f1(ys, vals, "high_8_to_10"),
            "low_1_to_6": precision_recall_f1(ys, vals, "low_1_to_6"),
        }
        for name, vals in [("model", model), *baselines.items()]
    }
    comparisons = {
        name: bootstrap_improvement(ys, model, vals)
        for name, vals in baselines.items()
    }

    confidence_summary = {}
    for label in ("low", "medium", "high"):
        idx = [i for i, mid in enumerate(case_ids)
               if predictions[mid]["confidence"] == label]
        confidence_summary[label] = metrics([ys[i] for i in idx],
                                            [model[i] for i in idx])
    calibrated_offset = params["train_mal_median_offset"]
    surprises = [
        i for i, x in enumerate(cases)
        if abs(ys[i] - float(x["mal_mean_score"]) - calibrated_offset) >= 1.5
    ]
    surprise_metrics = {
        name: metrics([ys[i] for i in surprises], [vals[i] for i in surprises])
        for name, vals in [("model", model), *baselines.items()]
    }

    missed = sorted([
        {"mal_id": mid, "title": cases[i]["title"], "actual": ys[i],
         "model": model[i], "calibrated_mal": baselines["mal_calibrated"][i],
         "abs_error": round(abs(ys[i] - model[i]), 4),
         "confidence": predictions[mid]["confidence"]}
        for i, mid in enumerate(case_ids)
    ], key=lambda x: -x["abs_error"])

    result = {
        "experiment_id": expected_id,
        "model_id": prediction_file.get("model_id"),
        "prediction_sha256": prediction_sha,
        "source_git_blob_sha": manifest["source_git_blob_shas"]["anime_json"],
        "count": len(cases),
        "training_calibration": params,
        "metrics": evaluated,
        "classification": classifications,
        "paired_improvement": comparisons,
        "confidence_calibration": confidence_summary,
        "consensus_surprises": {"n": len(surprises),
                                "threshold": 1.5, "metrics": surprise_metrics},
        "largest_model_errors": missed[:15],
        "warning": "Reason quality requires a separate blinded qualitative review."
    }
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
