"""Train the small DEMO risk model (pilot questionnaire -> HIGH / LOW).

Dev-only script (needs numpy + scikit-learn; the app itself does not).
No patient data is used or stored: it synthesises a cohort, labels it with the
HIGH / LOW rules from the questionnaire brief (below), fits a logistic
regression and exports the weights to src/engine/demo_model.json.

Run from backend/:  python ml/train_demo_model.py
"""
import json
import random
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.engine.demo_features import encode, normalize  # noqa: E402

HIGH_SCORE = 2.0  # rule score at/above which the synthetic label is HIGH


def rule_score(a: dict) -> float:
    """Screening rules from the brief. Positive = high-risk factor, negative = low-risk."""
    f = normalize(a)
    s = 0.0
    # --- high-risk factors ---
    if f["bmi"] and f["bmi"] > 30: s += 2.0
    if f["q1_age"] is not None and f["q1_age"] < 11: s += 1.5          # early menarche
    if f["q2_age"] is not None and f["q2_age"] > 55: s += 1.5          # late menopause
    if f["q3a"] == "yes": s += 1.0                                      # irregular periods
    if f["q3b"] == "yes": s += 1.0                                      # PCOS
    if f["q4"] == "yes": s += 0.5                                       # hormonal birth control / HRT
    if f["q7"] == "yes": s += 0.5                                       # pregnancy treatment
    if f["q8"] == "yes": s += 1.0                                       # breast problem / biopsy / radiation
    if f["q5_never_baby"] != "yes" and f["q6"] is not None and f["q6"] < 6: s += 1.5   # short breastfeeding
    if f["q10"] == "yes": s += 1.0                                      # family history
    if f["q10_who"] == "first": s += 1.0
    s += {"high": 1.0, "mid": 0.5}.get(f["q10_group"], 0.0)
    if f["q9"] == "yes": s += 1.5                                       # previous cancer
    s += {"high": 1.0, "mid": 0.5}.get(f["q9_group"], 0.0)
    # --- low-risk factors ---
    if f["q5_never_baby"] != "yes" and f["q6"] is not None and f["q6"] > 24: s -= 2.0
    if f["q1_age"] is not None and f["q1_age"] > 13: s -= 1.0
    if f["q2_age"] is not None and f["q2_age"] < 40: s -= 1.0
    if f["q10"] == "no": s -= 1.0
    if f["q9"] == "no": s -= 1.0
    return s


def sample(rng: random.Random) -> dict:
    pick = lambda opts, w: rng.choices(opts, w)[0]
    a = {"age": min(90, max(18, int(rng.gauss(42, 13)))),
         "height_cm": round(rng.gauss(156, 7)), "weight_kg": round(max(35, rng.gauss(64, 13)))}
    a["symptoms"] = pick(["Yes", "No"], [0.05, 0.95])
    a["tobacco_use"] = pick(["Yes", "No", "I do not wish to answer"], [0.1, 0.8, 0.1])
    a["alcohol_use"] = pick(["Yes", "No", "I do not wish to answer"], [0.07, 0.83, 0.1])
    a["q1_age"] = pick([int(min(25, max(8, rng.gauss(13, 1.6)))), "Don't know"], [0.95, 0.05])
    post = a["age"] >= 40 and rng.random() < (0.3 if a["age"] < 48 else 0.8)
    a["q2_age"] = int(min(70, max(20, rng.gauss(48, 5)))) if post else pick(["Not applicable", "Don't know"], [0.95, 0.05])
    yn = lambda p_yes: pick(["Yes", "No", "Don't know"], [p_yes, 0.9 - p_yes if p_yes < 0.9 else 0.0, 0.1])
    a["q3a"], a["q3b"], a["q4"] = yn(0.22), yn(0.08), yn(0.25)
    a["q7"], a["q8"] = yn(0.06), yn(0.12)
    if rng.random() < 0.15:
        a["q5_age"], a["q5_count"], a["q6"] = "Never had a baby", 0, 0
    else:
        a["q5_age"] = int(min(40, max(16, rng.gauss(24, 4))))
        a["q5_count"] = pick([1, 2, 3, 4], [0.25, 0.45, 0.22, 0.08])
        a["q6"] = int(max(0, rng.gauss(18 * a["q5_count"] ** 0.5, 12)))
    a["q9"] = pick(["Yes", "No", "Don't know"], [0.04, 0.93, 0.03])
    types = ["Breast Cancer", "Ovarian Cancer", "Colorectal Cancer", "Pancreatic Cancer", "Uterine Cancer", "Thyroid Cancer", "Others", "Don't know"]
    if a["q9"] == "Yes":
        a["q9_type"] = ",".join(rng.sample(types, rng.choice([1, 1, 2])))
    a["q10"] = pick(["Yes", "No", "Don't know"], [0.25, 0.68, 0.07])
    if a["q10"] == "Yes":
        a["q10_who"] = pick(["First Order (Mother, Sibling, Father)", "Second order (Related to Mother/Father)", "I don't know"], [0.4, 0.5, 0.1])
        a["q10_type"] = ",".join(rng.sample(types, rng.choice([1, 1, 2])))
    return a


def main(n: int = 30000, seed: int = 7) -> None:
    rng = random.Random(seed)
    people = [sample(rng) for _ in range(n)]
    names = encode(people[0])[0]
    X = np.array([encode(p)[1] for p in people])
    score = np.array([rule_score(p) for p in people])
    y = (score >= HIGH_SCORE).astype(int)
    print(f"cohort={n}  high-risk share={y.mean():.1%}")

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
    clf = LogisticRegression(C=1.0, max_iter=5000).fit(Xtr, ytr)
    p = clf.predict_proba(Xte)[:, 1]
    print(f"holdout accuracy={accuracy_score(yte, p >= 0.5):.3f}  AUC={roc_auc_score(yte, p):.3f}")

    order = np.argsort(-np.abs(clf.coef_[0]))[:8]
    print("strongest features:", [(names[i], round(float(clf.coef_[0][i]), 2)) for i in order])

    out = {"note": "Demo model trained on synthetic data. Not a diagnostic tool.",
           "feature_names": names, "intercept": float(clf.intercept_[0]),
           "weights": [round(float(w), 5) for w in clf.coef_[0]], "threshold": 0.5}
    dest = ROOT / "src" / "engine" / "demo_model.json"
    dest.write_text(json.dumps(out))
    print("wrote", dest)


if __name__ == "__main__":
    main()
