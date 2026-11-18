#!/usr/bin/env python3
"""Interpretable axis prototype and season-by-season MAL evidence audit.

All preference statements remain title-scoped unless repeated cross-title evidence
supports a tentative hypothesis. Work-side cues are descriptive, not evaluations.
MAL means, genres, studios, titles, ratings, and status are never model predictors.
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SEED = 20261118
ALPHAS = (0.1, 0.5, 1, 2, 4, 8, 16)
TEXT_FIELDS = ("synopsis", "themes", "tone", "pacing_and_structure", "character_dynamics", "distinctive_features")

AXES = {
    "progression_memory": {
        "label": "Progression, repetition and narrative memory",
        "question": "Do relationships, world state and consequences accumulate, or does the story loop/reset?",
        "cue_1": [r"gradually.{0,30}(develop|change|evolv)", r"cumulative", r"progression", r"develops over", r"consequences", r"stegvis", r"successivt", r"utvecklas", r"utveckling", r"förändras", r"konsekvenser", r"båge", r"ackumuler"],
        "cue_2": [r"repetitive", r"repeatedly returns", r"reset", r"loop", r"same conflict", r"samma konflikt", r"upprepar", r"upprepning", r"återställ", r"står still", r"utan progression", r"stagn"],
    },
    "premise_logic": {
        "label": "Premise logic and follow-through",
        "question": "Are rules established, questioned where appropriate, and used consistently?",
        "cue_1": [r"rules.{0,40}(consistent|consequence|followed)", r"consistent.{0,30}rules", r"regler.{0,40}(konsekvens|följs|etableras)", r"premiss.{0,40}(utforskas|konsekvens|påverkar|följs)", r"world reacts", r"världen reagerar", r"consequences of"],
        "cue_2": [r"unquestioned premise", r"premiss.{0,35}(ifrågasätts inte|tas för given|ignoreras)", r"handwave", r"plot convenience", r"premise.{0,20}(thin|contrived|forced)", r"premiss.{0,20}(tunn|krystad|påtvingad)", r"premise is ignored"],
    },
    "relationship_agency": {
        "label": "Relationship agency and mutual change",
        "question": "Do characters initiate change and respond to each other with reciprocal vulnerability?",
        "cue_1": [r"relationship.{0,35}(develop|change|evolv)", r"mutual.{0,20}(vulnerab|trust|growth)", r"takes initiative", r"relationship changes", r"relation.{0,35}(utveckl|förändr|växer)", r"ömsesidig", r"sårbarhet", r"tar egna initiativ", r"dynamik.{0,25}(förändr|utveckl)"],
        "cue_2": [r"relationship loop", r"static relationship", r"miscommunication loop", r"same romantic conflict", r"relation.{0,30}(loop|står still|upprepas)", r"samma.{0,20}(missförstånd|konflikt)", r"karikatyr", r"pastisch"],
    },
    "emotional_framing": {
        "label": "Earned emotion and emotional framing",
        "question": "Does emotion grow from accumulated story and character, or is a reaction prescribed through suffering?",
        "cue_1": [r"earned emotional", r"emotional payoff", r"emotional resolution", r"nuanced grief", r"careful portrayal", r"känslomässig.{0,25}(upplösning|utveckling|tyngd)", r"förtjänad", r"varsam skildring", r"bygger upp.{0,20}känslor"],
        "cue_2": [r"manipulative tragedy", r"suffering for suffering", r"cheap trick", r"melodrama", r"prescribes.{0,20}reaction", r"instruerar.{0,20}känna", r"lidande för lidandets", r"billigt trick", r"påklistrad sorg", r"retcon.{0,30}(grief|sorg)"],
    },
    "tone_texture": {
        "label": "Tone, humor, curiosity and melancholy",
        "question": "What emotional texture emerges from the mix of humor, curiosity, melancholy, anxiety and warmth?",
        "cue_1": [r"humor.{0,35}(melancholy|serious|tender|curious)", r"melancholy.{0,35}(humor|curiosity|warmth)", r"torrt humor", r"melankol.{0,35}(humor|nyfikenhet|värme)", r"humor.{0,35}(allvar|melankoli)", r"nyfikenhet", r"varm.{0,20}melankoli"],
        "cue_2": [r"overly angsty", r"excessive angst", r"tonal whiplash", r"constant despair", r"alltför angst", r"skrikig", r"ton.{0,25}(spretig|ojämn)", r"misery porn"],
    },
    "format_accumulation": {
        "label": "Episodic form, accumulation and repetition",
        "question": "Does episodic or fragmented form preserve state and build an arc, or repeat without payoff?",
        "cue_1": [r"episodic.{0,45}(arc|continuity|accumulat|develop)", r"fragmented.{0,35}(arc|timeline|continuity)", r"each episode.{0,35}(build|advance|change)", r"episodisk.{0,35}(båge|sammanhäng|utveckl|kontinuitet)", r"fullständig arc", r"save states", r"inga resets", r"tidslinje.{0,30}(utvecklas|består)"],
        "cue_2": [r"episodic.{0,40}(reset|formula|repetit)", r"slot.?filling", r"same thing every episode", r"episode after episode", r"episod.{0,30}(samma|upprepar|fyller slots)", r"återkommande loop", r"utan.{0,20}sammanhang"],
    },
    "craft_intent": {
        "label": "Craft, coherence and creative intent",
        "question": "Does confident execution or deliberate experimentation make the work cohere despite flaws?",
        "cue_1": [r"deliberate experiment", r"distinctive visual language", r"carefully constructed", r"strong craft", r"clear authorial intent", r"väl utförd", r"genomtänkt", r"medvetet grepp", r"craft", r"hantverk", r"experiment", r"visuellt.{0,25}(särpräglat|genomtänkt)"],
        "cue_2": [r"production problems", r"inconsistent writing", r"underdeveloped execution", r"svag produktion", r"ojämnt manus", r"tappar fokus", r"håller inte ihop", r"out of focus"],
    },
    "content_cost": {
        "label": "Content cost and tolerance",
        "question": "How much fanservice, explicit suffering, violence, angst or premise friction does the work demand?",
        "cue_1": [r"ecchi", r"fan.?service", r"sexualized", r"graphic violence", r"body horror", r"mörker", r"angst", r"lidande", r"mord", r"död", r"svält"],
        "cue_2": [],
    },
}

# A controlled lexicon converts prose into observable cue presence, not quality.
# Values are raw cue counts clipped to 2; downstream fitting is regularized.

def fold(text):
    text = unicodedata.normalize("NFKD", (text or "").casefold())
    return "".join(c for c in text if not unicodedata.combining(c))


def passage(profile):
    return fold(" ".join(" ".join(profile.get(k, [])) if isinstance(profile.get(k), list)
                           else profile.get(k, "") for k in TEXT_FIELDS))


def cues(text):
    out = {}
    for key, spec in AXES.items():
        for side in ("cue_1", "cue_2"):
            hits = sum(len(re.findall(fold(pattern), text)) for pattern in spec[side])
            out[f"{key}__{side}"] = min(2, hits)
    return out


def map_axes(text):
    x = fold(text)
    axes=[]
    for key,spec in AXES.items():
        if any(re.search(fold(p),x) for side in ("cue_1","cue_2") for p in spec[side]):
            axes.append(key)
    # Some factors are broader than the work-description lexicon.
    manual = {
        "progression_memory": r"progress|progression|utveckl|steg fram|upprep|repetition|loop|stillast|tempo|arc|filler|save state|reset",
        "premise_logic": r"premiss|premise|regler|regel|frågan|ifrågasätt|logik|konsekvens|utgångspunkt|setup",
        "relationship_agency": r"relation|dynamik|par |paret|vulnerability|sårbar|initiativ|karaktär|kärlek|romans|vänskap|grupp",
        "emotional_framing": r"känsl|sorg|lidande|drama|traged|död|svält|grief|emotion|tårar|reaktion|retcon",
        "tone_texture": r"ton|humor|komedi|melank|nyfiken|stämning|angst|fånig|trams|vibe",
        "format_accumulation": r"episod|fragment|båge|canon|loop|filler|slot|save state|reset|säsong|format",
        "craft_intent": r"hantverk|craft|utför|produktion|animation|visuell|musik|va |kreatör|experiment|stil|manus|geni",
        "content_cost": r"ecchi|fan.?service|angst|våld|död|mord|lidande|svält|sexuell|slemhinna|blod",
    }
    for key,pat in manual.items():
        if re.search(fold(pat),x) and key not in axes: axes.append(key)
    return axes


def direction(text, context=""):
    x=fold(text); c=fold(context)
    has=lambda pattern,value: bool(re.search(fold(pattern),value))
    if has(r"minns inte|pausade|paus|utanför verket|inte sett tillrackligt|no judgment|skäl utanför",x):
        return "uncertain_or_non_evaluative"
    neg=has(r"inte|sakna|for lite|för lite|tappa|tappar|drog ned|höll nere|stör|trött|svag|misslyck|tilltalade mig inte|fungerade inte|loop|upprep|för mycket|tunn|slösade|krystad|billigt trick",x)
    pos=has(r"fungerade|uppskattar|bättre än väntat|fina ögonblick|bra |väl gjord|välgjord|intressant|genial|geniuna|nyfikenhet|rolig|kawaii|väckte frågor|fick mer tid|hög nivå|kreatörer.{0,30}bra|äga sin|ägde sin|gjorde saken fullt ut|gjorde exakt vad",x)
    neg_context=has(r"vad drog.{0,25}ned|satte tak|höll.{0,20}nere|vad gjorde att du avbröt|vad gjorde att du inte fortsatte",c)
    if pos and (neg or neg_context): return "mixed_for_this_title"
    if neg or neg_context: return "negative_for_this_title"
    if pos or has(r"vad bar|bidrog positivt|bar serien|fungerade battre|bättre än väntat",c):
        return "positive_for_this_title"
    return "factor_named_direction_unclear"


def answer_text(answer):
    if not answer: return ""
    if isinstance(answer,dict):
        selected=answer.get("selected_options") or []
        free=answer.get("free_text") or ""
        return "; ".join([*selected,free]).strip("; ")
    return str(answer)


def franchise(title):
    tokens=re.findall(r"[a-z0-9]+",fold(title))
    return " ".join(tokens[:2]) if len(tokens)>1 else " ".join(tokens)


def folds(groups):
    yield from GroupKFold(n_splits=5).split(np.zeros((len(groups),1)),np.zeros(len(groups)),groups)


def axis_rating_model(rows, features):
    rated=[r for r in rows if r["status"]=="completed" and r.get("score",0)>0 and r["profile_status"]=="complete"]
    cols=list(next(iter(features.values())).keys())
    X=np.array([[features[r["mal_id"]][k] for k in cols] for r in rated],dtype=float)
    y=np.array([r["score"] for r in rated],dtype=float)
    groups=np.array([franchise(r["title"]) for r in rated])
    oof=np.zeros(len(rated)); med=np.zeros(len(rated)); chosen=[]
    for tr,te in folds(groups):
        inner={a:[] for a in ALPHAS}
        for a in ALPHAS:
            for itr,ite in folds(groups[tr]):
                m=Ridge(alpha=a).fit(X[tr][itr],y[tr][itr])
                inner[a].extend(np.abs(y[tr][ite]-m.predict(X[tr][ite])))
        alpha=min(ALPHAS,key=lambda a:(np.mean(inner[a]),a)); chosen.append(alpha)
        med[te]=median(y[tr]); oof[te]=Ridge(alpha=alpha).fit(X[tr],y[tr]).predict(X[te])
    fullalpha=float(median(chosen)); full=Ridge(alpha=fullalpha).fit(X,y)
    all_preds=[]
    for r in rows:
        if r["status"]=="completed" and r.get("score",0)>0: continue
        pred=float(full.predict(np.array([[features[r["mal_id"]][k] for k in cols]]))[0])
        all_preds.append({"mal_id":r["mal_id"],"title":r["title"],"status":r["status"],"year":r.get("release_year"),"season":r.get("release_season"),"score_if_completed":round(pred,2)})
    season=defaultdict(list)
    for i,r in enumerate(rated): season[r.get("release_season") or "unknown"].append(i)
    season_metrics={k:{"n":len(v),"axis_mae":round(float(np.mean(np.abs(y[v]-oof[v]))),4),"median_mae":round(float(np.mean(np.abs(y[v]-med[v]))),4)} for k,v in season.items()}
    weights={k:round(float(v),4) for k,v in zip(cols,full.coef_)}
    return {"n":len(rated),"median_mae":round(mean_absolute_error(y,med),4),"axis_mae":round(mean_absolute_error(y,oof),4),"mae_gain":round(mean_absolute_error(y,med)-mean_absolute_error(y,oof),4),"selected_alphas":chosen,"final_alpha":fullalpha,"features":cols,"weights":weights,"season_metrics":season_metrics,
            "oof":[{"mal_id":r["mal_id"],"title":r["title"],"year":r.get("release_year"),"season":r.get("release_season"),"score":int(y[i]),"predicted":round(float(oof[i]),2),"median":round(float(med[i]),2)} for i,r in enumerate(rated)],"unrated_predictions":all_preds}


def main():
    anime=json.loads((ROOT/"anime.json").read_text(encoding="utf-8"))["anime"]
    profiles=json.loads((ROOT/"anime_profiles.json").read_text(encoding="utf-8"))["profiles"]
    prefs=json.loads((ROOT/"anime_preference_learning.json").read_text(encoding="utf-8"))
    explicit=prefs["insights"]["explicit_user_qualitative_evidence"]
    items=prefs["questions"]["items"]
    rows=[]; feat={}; evidence=[]
    for raw in anime:
        p=profiles.get(str(raw["mal_id"]),{})
        worktext=passage(p)
        f=cues(worktext)
        feat[raw["mal_id"]]=f
        rows.append({**raw,"profile_status":p.get("profile_status","missing"),"profile":p,"work_cues":f})
    # Raw answers are retained as work-specific evidence. No cross-title weight is
    # assigned merely because an item was selected in a questionnaire.
    for qid,q in items.items():
        if q.get("status")!="answered": continue
        ans=q.get("answer")
        text=answer_text(ans)
        if not text: continue
        axes=map_axes(text)
        evidence.append({"mal_id":q["mal_id"],"title":q.get("title"),"source_id":qid,"source_type":"explicit_question_answer","round":q.get("created_round"),"status":q.get("evidence",{}).get("observed_status"),"episodes_watched":q.get("evidence",{}).get("episodes_watched"),"user_score":q.get("evidence",{}).get("user_score"),"axes":axes,"direction":direction(text,q.get("question","")),"certainty":"direct_factor_selection; direction only assigned when wording states it","text":text})
    for eid,e in explicit.items():
        ids=e.get("mal_ids",[])
        for mid in ids:
            evidence.append({"mal_id":mid,"title":None,"source_id":eid,"source_type":"explicit_user_statement","round":None,"status":None,"episodes_watched":None,"user_score":None,"axes":map_axes(e.get("verbatim", "")),"direction":direction(e.get("verbatim", ""),e.get("kind", "")),"certainty":e.get("evidence_status",e.get("kind","explicit statement")),"text":e.get("verbatim","")})
    by_id=defaultdict(list)
    for e in evidence: by_id[e["mal_id"]].append(e)
    # Full release-season audit of every completed and dropped item. PTW rows are
    # kept as context, but predictions are not converted into preferences.
    audit=[]
    for r in rows:
        if r["status"] not in ("completed","dropped"): continue
        ev=by_id.get(r["mal_id"],[])
        axes=sorted(set(a for e in ev for a in e["axes"]))
        why=" | ".join(dict.fromkeys(e["text"] for e in ev if e["text"]))
        audit.append({"mal_id":r["mal_id"],"title":r["title"],"year":r.get("release_year"),"season":r.get("release_season"),"status":r["status"],"user_score":r.get("score") or "","episodes_watched":r.get("episodes_watched"),"profile_status":r["profile_status"],"work_cue_tags":";".join(k for k,v in r["work_cues"].items() if v),"explicit_evidence_count":len(ev),"explicit_axes":";".join(axes),"direct_reasons":why})
    model=axis_rating_model(rows,feat)
    summary=Counter(); byaxis=defaultdict(lambda:{"titles":set(),"negative":set(),"positive":set(),"mixed":set(),"unclear":set(),"drop":set(),"scores":[]})
    for e in evidence:
        if not e["axes"]: continue
        for a in e["axes"]:
            s=byaxis[a]; s["titles"].add(e["mal_id"])
            d=e["direction"]
            if d=="negative_for_this_title": s["negative"].add(e["mal_id"])
            elif d=="positive_for_this_title": s["positive"].add(e["mal_id"])
            elif d=="mixed_for_this_title": s["mixed"].add(e["mal_id"])
            else: s["unclear"].add(e["mal_id"])
            if e.get("status")=="dropped": s["drop"].add(e["mal_id"])
            if e.get("user_score"): s["scores"].append(e["user_score"])
    axis_summary={k:{"label":AXES[k]["label"],"titles_with_explicit_mentions":len(v["titles"]),"explicit_negative_titles":len(v["negative"]),"explicit_positive_titles":len(v["positive"]),"explicit_mixed_titles":len(v["mixed"]),"direction_unclear_titles":len(v["unclear"]),"dropped_titles":len(v["drop"]),"work_text_coverage":sum(bool(feat[mid].get(k+"__cue_1") or feat[mid].get(k+"__cue_2")) for mid in feat)} for k,v in byaxis.items()}
    result={"schema_version":1,"snapshot":{"anime_blob":"ec68ba8db62df4d1275e020988f8cdb0f6bf06d3","profiles_blob":"65ee46c5d708cb696fa1378977d4c15f02258f55","preference_blob":"1fdcf7acc3912789ca71fed8f4b26f65a4f0623f"},"principles":["work-side textual cues describe a title; they are not quality judgments","a user's factor selection stays tied to that title unless repeated cross-title evidence supports a tentative hypothesis","dropped is not treated as a low numeric rating","no MAL mean is used"],"axes":{k:{"label":v["label"],"question":v["question"],"cue_1_patterns":v["cue_1"],"cue_2_patterns":v["cue_2"]} for k,v in AXES.items()},"counts":{"titles":len(rows),"complete_profiles":sum(r["profile_status"]=="complete" for r in rows),"completed":sum(r["status"]=="completed" for r in rows),"dropped":sum(r["status"]=="dropped" for r in rows),"completed_scored_profiled":model["n"],"evidence_records":len(evidence),"titles_with_direct_evidence":len(by_id)},"rating_model":model,"axis_summary":axis_summary,"seasonal_audit":audit,"evidence":evidence}
    (OUT/"axis_results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with (OUT/"seasonal_audit.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(audit[0]));w.writeheader();w.writerows(sorted(audit,key=lambda x:(x["year"] or 0,{"winter":0,"spring":1,"summer":2,"fall":3}.get(x["season"],4),x["mal_id"])))
    with (OUT/"axis_evidence.csv").open("w",encoding="utf-8",newline="") as f:
        fields=["mal_id","title","source_id","source_type","round","status","episodes_watched","user_score","axes","direction","certainty","text"]
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for e in evidence: w.writerow({**e,"axes":";".join(e["axes"])})
    print(json.dumps({"counts":result["counts"],"rating":{k:v for k,v in model.items() if k not in ("oof","unrated_predictions","weights","features")},"axis_summary":axis_summary},ensure_ascii=False,indent=2))


if __name__=="__main__": main()
