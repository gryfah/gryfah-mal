#!/usr/bin/env python3
"""Retrospective, MAL-mean-free experiment for personal MAL taste modelling.

The rating model sees only factual prose fields from anime_profiles.json.
It never reads scores/statuses as predictors, MAL averages, genres, studios,
titles, or comparison_cues. The drop model is a separate, exploratory task.
"""
from __future__ import annotations

import json
from hashlib import sha1
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from statistics import median

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, brier_score_loss,
                             mean_absolute_error, roc_auc_score)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
ALPHAS = (0.5, 1, 2, 4, 8, 16, 32)
TEXT_FIELDS = ("synopsis", "themes", "tone", "pacing_and_structure",
               "character_dynamics", "distinctive_features")
SEED = 20261118


def load_data():
    anime = json.loads((ROOT / "anime.json").read_text(encoding="utf-8"))["anime"]
    profiles = json.loads((ROOT / "anime_profiles.json").read_text(encoding="utf-8"))["profiles"]
    by_id = {int(k): v for k, v in profiles.items()}
    joined = []
    for row in anime:
        p = by_id.get(row["mal_id"])
        if p and p.get("profile_status") == "complete":
            text = "\n".join(" ".join(p.get(field, [])) if isinstance(p.get(field), list)
                             else p.get(field, "") for field in TEXT_FIELDS)
            joined.append({**row, "profile": p, "text": text})
    return joined


def git_blob_sha(path):
    raw = path.read_bytes()
    return sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def franchise_key(title):
    normalized = unicodedata.normalize("NFKD", title.casefold())
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    tokens = re.findall(r"[a-z0-9]+", normalized)
    return " ".join(tokens[:2]) if len(tokens) >= 2 else " ".join(tokens)


def pipeline(alpha):
    return make_pipeline(
        TfidfVectorizer(strip_accents="unicode", lowercase=True,
                        ngram_range=(1, 2), min_df=3, max_df=0.85,
                        sublinear_tf=True, token_pattern=r"(?u)\b[\w'-]+\b"),
        Ridge(alpha=alpha),
    )


def split_indices(groups, n_splits=5):
    x = np.zeros((len(groups), 1))
    y = np.zeros(len(groups))
    yield from GroupKFold(n_splits=n_splits).split(x, y, groups)


def select_alpha(texts, y, groups):
    scores = {}
    for alpha in ALPHAS:
        errs = []
        for tr, te in split_indices(groups):
            model = pipeline(alpha).fit([texts[i] for i in tr], y[tr])
            errs.extend(np.abs(y[te] - model.predict([texts[i] for i in te])))
        scores[alpha] = float(np.mean(errs))
    return min(ALPHAS, key=lambda a: (scores[a], a)), scores


def rating_experiment(rows):
    rated = [r for r in rows if r["status"] == "completed" and r.get("score", 0) > 0]
    texts = [r["text"] for r in rated]
    y = np.array([r["score"] for r in rated], dtype=float)
    groups = np.array([franchise_key(r["title"]) for r in rated])
    oof, medians, alphas = np.zeros(len(rated)), np.zeros(len(rated)), []
    for tr, te in split_indices(groups):
        a, _ = select_alpha([texts[i] for i in tr], y[tr], groups[tr])
        alphas.append(a)
        medians[te] = median(y[tr])
        oof[te] = pipeline(a).fit([texts[i] for i in tr], y[tr]).predict([texts[i] for i in te])
    chosen_alpha = float(median(alphas))
    final = pipeline(chosen_alpha).fit(texts, y)
    resid = np.abs(y - oof)
    grouped_delta = defaultdict(list)
    season_rows = defaultdict(list)
    for i, row in enumerate(rated):
        grouped_delta[groups[i]].append(float(abs(y[i]-medians[i]) - abs(y[i]-oof[i])))
        season_rows[row.get("release_season") or "unknown"].append(i)
    group_means = np.array([np.mean(v) for v in grouped_delta.values()])
    rng = np.random.default_rng(SEED)
    bootstrap = np.sort(np.mean(rng.choice(group_means, size=(5000, len(group_means)), replace=True), axis=1))
    season_metrics = {season: {
        "n": len(indices),
        "text_mae": round(float(np.mean(np.abs(y[indices]-oof[indices]))), 4),
        "median_mae": round(float(np.mean(np.abs(y[indices]-medians[indices]))), 4),
    } for season, indices in sorted(season_rows.items())}
    terms = final.named_steps["ridge"].coef_
    names = final.named_steps["tfidfvectorizer"].get_feature_names_out()
    order = np.argsort(terms)
    effects = {
        "most_negative_terms": [{"term": str(names[i]), "weight": round(float(terms[i]), 4)} for i in order[:25]],
        "most_positive_terms": [{"term": str(names[i]), "weight": round(float(terms[i]), 4)} for i in order[-25:][::-1]],
    }
    predictions = []
    for r in rows:
        if r["status"] == "completed" and r.get("score", 0) > 0:
            continue
        point = float(final.predict([r["text"]])[0])
        predictions.append({"mal_id": r["mal_id"], "title": r["title"], "status": r["status"],
                            "release_year": r.get("release_year"), "release_season": r.get("release_season"),
                            "predicted_score_if_completed": round(point, 2),
                            "approx_abs_error_p80": round(float(np.quantile(resid, .8)), 2)})
    return {
        "n": len(rated), "median_baseline": round(mean_absolute_error(y, medians), 4),
        "text_model": round(mean_absolute_error(y, oof), 4),
        "text_model_rmse": round(float(np.sqrt(np.mean((y-oof)**2))), 4),
        "improvement_mae": round(mean_absolute_error(y, medians)-mean_absolute_error(y, oof), 4),
        "franchise_grouped_improvement_bootstrap_95pct": [round(float(bootstrap[124]), 4), round(float(bootstrap[4874]), 4)],
        "release_season_slices": season_metrics,
        "within_one_point": round(float(np.mean(np.abs(y-oof) <= 1)), 4),
        "outer_fold_alphas": alphas, "final_alpha": chosen_alpha,
        "approx_abs_error_p80": round(float(np.quantile(resid, .8)), 2),
        "oof": [{"mal_id": r["mal_id"], "title": r["title"], "year": r.get("release_year"),
                 "season": r.get("release_season"), "actual": int(y[i]),
                 "predicted": round(float(oof[i]), 2), "median_prediction": round(float(medians[i]), 2),
                 "residual": round(float(y[i]-oof[i]), 2)} for i, r in enumerate(rated)],
        "coefficients": effects, "unrated_predictions": predictions,
    }


def drop_experiment(rows):
    started = [r for r in rows if r["status"] in ("completed", "dropped")]
    texts = [r["text"] for r in started]
    y = np.array([int(r["status"] == "dropped") for r in started])
    groups = np.array([franchise_key(r["title"]) for r in started])
    probs = np.zeros(len(y)); majority = np.zeros(len(y), dtype=int); pred = np.zeros(len(y), dtype=int)
    for tr, te in split_indices(groups):
        prevalence = float(y[tr].mean())
        majority[te] = int(prevalence >= .5)
        model = make_pipeline(TfidfVectorizer(strip_accents="unicode", ngram_range=(1, 2),
                                              min_df=3, max_df=.85, sublinear_tf=True),
                              LogisticRegression(C=.1, max_iter=2000))
        model.fit([texts[i] for i in tr], y[tr])
        probs[te] = model.predict_proba([texts[i] for i in te])[:, 1]
        pred[te] = (probs[te] >= .5).astype(int)
    # A proper base-rate predictor is the fold's training prevalence.
    base_prob = np.zeros(len(y))
    for tr, te in split_indices(groups): base_prob[te] = y[tr].mean()
    return {
        "n": len(y), "drop_count": int(y.sum()), "drop_rate": round(float(y.mean()), 4),
        "roc_auc": round(float(roc_auc_score(y, probs)), 4),
        "brier_model": round(float(brier_score_loss(y, probs)), 4),
        "brier_base_rate": round(float(brier_score_loss(y, base_prob)), 4),
        "accuracy": round(float(accuracy_score(y, pred)), 4),
        "balanced_accuracy": round(float(balanced_accuracy_score(y, pred)), 4),
        "majority_accuracy": round(float(accuracy_score(y, majority)), 4),
        "note": "Drop/completion is not a dislike score; this only tests whether factual brief text predicts observed MAL status.",
        "predictions": [{"mal_id": r["mal_id"], "title": r["title"], "status": r["status"],
                         "drop_probability": round(float(probs[i]), 3)}
                        for i, r in enumerate(started)],
    }


def main():
    rows = load_data()
    result = {"schema_version": 1, "protocol": {
        "snapshot": "main anime.json as of 2026-11-18; descriptions from anime_profiles.json",
        "input_git_blob_shas": {
            "anime.json": git_blob_sha(ROOT / "anime.json"),
            "anime_profiles.json": git_blob_sha(ROOT / "anime_profiles.json"),
        },
        "predictors": list(TEXT_FIELDS), "excluded_predictors": ["MAL mean", "MAL genres", "studios", "title", "user rating", "status", "comparison_cues"],
        "validation": "nested-in-spirit grouped five-fold retrospective CV; hyperparameter selected inside each outer training fold; franchise-like title groups kept together",
        "limits": ["Retrospective CV, not a new blind test.", "Curated prose can encode selection/editorial bias.", "Predictions are uncertain and do not replace explicit work-specific reasons.", "Drop model predicts observed status, not dislike."],
    }, "profile_count": len(rows), "rating": rating_experiment(rows), "drop": drop_experiment(rows)}
    (OUT / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    with (OUT / "score_predictions.csv").open("w", encoding="utf-8", newline="") as f:
        import csv
        w=csv.DictWriter(f, fieldnames=["mal_id","title","status","release_year","release_season","predicted_score_if_completed","approx_abs_error_p80"])
        w.writeheader(); w.writerows(result["rating"]["unrated_predictions"])
    with (OUT / "rating_oof.csv").open("w", encoding="utf-8", newline="") as f:
        import csv
        w=csv.DictWriter(f, fieldnames=["mal_id","title","year","season","actual","predicted","median_prediction","residual"])
        w.writeheader(); w.writerows(result["rating"]["oof"])
    with (OUT / "drop_predictions.csv").open("w", encoding="utf-8", newline="") as f:
        import csv
        w=csv.DictWriter(f, fieldnames=["mal_id","title","status","drop_probability"])
        w.writeheader(); w.writerows(result["drop"]["predictions"])
    print(json.dumps({"profiles":len(rows), "rated_n":result["rating"]["n"],
                      "rating_baseline_mae":result["rating"]["median_baseline"],
                      "rating_text_mae":result["rating"]["text_model"],
                      "drop":{k:v for k,v in result["drop"].items() if k!="predictions"}}, ensure_ascii=False, indent=2))


if __name__ == "__main__": main()
