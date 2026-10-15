"""Answer -> feature encoding for the demo risk model (PinkShield pilot questionnaire).

Shared by ml/train_demo_model.py and src/engine/demo_model.py so training and
inference can never drift apart. No I/O, nothing stored.
"""

# numeric fields: key -> (min, max, default when unanswered)
NUMERIC = {
    "age": (18, 95, 45),
    "bmi": (12, 50, 24),
    "q1_age": (8, 25, 13),          # age at first period
    "q2_age": (20, 70, 48),         # age periods stopped / surgery
    "q5_count": (0, 20, 2),         # full-term pregnancies
    "q5_age": (12, 55, 24),         # age at first baby
    "q6": (0, 400, 12),             # months breastfed in total
}
YN = ["yes", "no", "dk", "missing"]
CATEGORICAL = {
    "symptoms": YN, "tobacco_use": YN, "alcohol_use": YN,
    "q2_status": ["age", "not_applicable", "dk", "missing"],
    "q3a": YN, "q3b": YN, "q4": YN, "q7": YN, "q8": YN,
    "q5_never_baby": ["yes", "no", "missing"],
    "q9": YN, "q9_group": ["high", "mid", "other", "none"],
    "q10": YN, "q10_who": ["first", "second", "dk", "none"], "q10_group": ["high", "mid", "other", "none"],
}

HIGH_TYPES = {"breast cancer", "ovarian cancer", "colorectal cancer", "pancreatic cancer"}
MID_TYPES = {"uterine cancer", "thyroid cancer"}


def _yn(v) -> str:
    s = str(v if v is not None else "").strip().lower().replace("’", "'")
    if s == "yes":
        return "yes"
    if s == "no":
        return "no"
    if s in ("don't know", "dont know", "dont_know", "i do not wish to answer", "i don't know"):
        return "dk"
    return "missing"


def _num(v):
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return None


def _group(v) -> str:
    items = [t.strip().lower() for t in str(v or "").split(",") if t.strip()]
    if any(t in HIGH_TYPES for t in items):
        return "high"
    if any(t in MID_TYPES for t in items):
        return "mid"
    return "other" if items else "none"


def normalize(a: dict) -> dict:
    """Raw pilot-study answers -> clean dict of numeric/categorical features."""
    out: dict = {}
    h, w = _num(a.get("height_cm")), _num(a.get("weight_kg"))
    out["bmi"] = w / (h / 100) ** 2 if h and w and h > 0 else None
    out["age"] = _num(a.get("age"))
    for k in ("q1_age", "q5_count", "q6"):
        out[k] = _num(a.get(k))
    q2 = a.get("q2_age")
    out["q2_age"] = _num(q2)
    out["q2_status"] = "age" if out["q2_age"] is not None else (
        "not_applicable" if str(q2).strip().lower() == "not applicable" else _yn(q2))
    never = str(a.get("q5_age") or "").strip().lower().startswith("never")
    out["q5_age"] = None if never else _num(a.get("q5_age"))
    out["q5_never_baby"] = "yes" if never else ("no" if out["q5_age"] is not None else "missing")
    out["symptoms"] = _yn(a.get("symptoms"))
    for k in ("tobacco_use", "alcohol_use", "q3a", "q3b", "q4", "q7", "q8", "q9", "q10"):
        out[k] = _yn(a.get(k))
    out["q9_group"] = _group(a.get("q9_type")) if out["q9"] == "yes" else "none"
    out["q10_group"] = _group(a.get("q10_type")) if out["q10"] == "yes" else "none"
    who = str(a.get("q10_who") or "").lower()
    out["q10_who"] = "none" if out["q10"] != "yes" else ("first" if who.startswith("first") else "second" if who.startswith("second") else "dk")
    return out


def encode(a: dict) -> tuple[list[str], list[float]]:
    f = normalize(a)
    names: list[str] = []
    vals: list[float] = []
    for k, (lo, hi, default) in NUMERIC.items():
        raw = f.get(k)
        present = raw is not None
        v = raw if present else default
        names += [f"{k}", f"{k} answered"]
        vals += [(min(max(v, lo), hi) - lo) / (hi - lo), 1.0 if present else 0.0]
    for k, opts in CATEGORICAL.items():
        cur = f.get(k)
        cur = cur if cur in opts else opts[-1] if "missing" in opts else opts[0]
        for o in opts:
            names.append(f"{k}={o}")
            vals.append(1.0 if cur == o else 0.0)
    # threshold flags matching the screening brief (BMI>30, early/late menarche & menopause, breastfeeding)
    def flag(name, cond):
        names.append(name)
        vals.append(1.0 if cond else 0.0)

    bmi, m1, m2, bf = f.get("bmi"), f.get("q1_age"), f.get("q2_age"), f.get("q6")
    has_baby = f.get("q5_never_baby") != "yes"
    flag("BMI over 30", bmi is not None and bmi > 30)
    flag("first period before 11", m1 is not None and m1 < 11)
    flag("first period after 13", m1 is not None and m1 > 13)
    flag("periods stopped after 55", m2 is not None and m2 > 55)
    flag("periods stopped before 40", m2 is not None and m2 < 40)
    flag("breastfed under 6 months", has_baby and bf is not None and bf < 6)
    flag("breastfed over 24 months", has_baby and bf is not None and bf > 24)
    return names, vals
