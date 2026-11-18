#!/usr/bin/env python3
"""Score the locked narrative annotation pilot against the MAL + genre baseline."""
import argparse
import json
from pathlib import Path
from statistics import fmean

from evaluate import ROOT, V1, blob_sha, build_baselines, clip, franchise_groups, load


AXES = ("choice_with_consequence", "cumulative_development", "reset_erases_consequence")
STATES = {"evidenced", "counterevidenced", "unknown"}


def run(training_path, annotations_path):
    sealed = load(annotations_path)
    if blob_sha(training_path) != sealed["training_source_sha"]:
        raise ValueError("Use the training export frozen in the annotation protocol")
    rows = load(training_path)["rows"]
    by_id = {row["mal_id"]: row for row in rows}
    annotations = sealed["rows"]
    ids = [row["mal_id"] for row in annotations]
    if len(ids) != 8 or len(set(ids)) != 8 or not set(ids) <= by_id.keys():
        raise ValueError("Unexpected pilot cohort")
    groups = franchise_groups(rows)
    # Hold out all pilot families together to avoid sharing fitted baselines
    # between pilot rows or connected seasons.
    blocked = {groups[mal_id] for mal_id in ids}
    training = [row for row in rows if groups[row["mal_id"]] not in blocked]
    cases = [by_id[mal_id] for mal_id in ids]
    baseline, _ = build_baselines(training, cases)
    model = []
    counts = dict.fromkeys(AXES, 0)
    for case, annotation, base in zip(cases, annotations, baseline["mal_genre_shrunk"]):
        delta = 0
        for axis in AXES:
            evidence = annotation[axis]
            state = evidence["state"]
            if state not in STATES:
                raise ValueError(f"Unknown annotation state for {case['mal_id']}")
            if state != "unknown" and not (evidence.get("description") and evidence.get("sources")):
                raise ValueError(f"Missing traceable evidence for {case['mal_id']}")
            if state == "evidenced":
                delta += sealed["adjustment"][axis]
                counts[axis] += 1
        prediction = clip(base + delta)
        actual = case["user_score"]
        model.append({
            "mal_id": case["mal_id"], "title": case["title"], "actual": actual,
            "B2": base, "event_pilot": prediction, "delta": delta,
            "B2_absolute_error": abs(actual - base),
            "event_absolute_error": abs(actual - prediction),
        })
    base_mae = fmean(row["B2_absolute_error"] for row in model)
    event_mae = fmean(row["event_absolute_error"] for row in model)
    return {
        "experiment": sealed["experiment"],
        "n": len(model),
        "n_baseline_training": len(training),
        "B2_MAE": base_mae,
        "event_MAE": event_mae,
        "improvement": base_mae - event_mae,
        "evidenced_by_axis": counts,
        "rows": model,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training", type=Path, default=V1 / "training.json")
    parser.add_argument("--annotations", type=Path, default=ROOT / "event_pilot_annotations.json")
    args = parser.parse_args()
    print(json.dumps(run(args.training, args.annotations), ensure_ascii=False, indent=2))
