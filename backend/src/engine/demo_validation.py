"""Server-side validation + conditional cleaning for the chat questionnaire (q1..q10).

Mirrors the rules enforced in chat.html. Returns (clean_answers, errors); stale answers
for questions that are not applicable are dropped so they cannot affect the result.
"""

YN = ("Yes", "No", "Don't know")
NEVER = "Never had a baby/Full time pregnancy"
NA = "Not applicable"
DK = "Don't know"
CANCER_TYPES = ("Breast Cancer", "Ovarian Cancer", "Colorectal Cancer", "Pancreatic Cancer",
                "Uterine Cancer", "Thyroid Cancer", "Others", DK)
WHO = ("First Order (Mother, Sibling, Father)", "Second Order (Related to Mother/Father)", "I don't know")


def _int(v, lo, hi):
    """Return (int|None, error|None)."""
    try:
        s = str(v).strip()
        if not s.lstrip("-").isdigit():
            raise ValueError
        n = int(s)
    except (TypeError, ValueError):
        return None, "Please enter a valid number."
    if not lo <= n <= hi:
        return None, f"Please enter a number between {lo} and {hi}."
    return n, None


def _types(v):
    items = [t.strip() for t in (v if isinstance(v, list) else str(v or "").split(",")) if str(t).strip()]
    return items


def validate(a: dict) -> tuple[dict, dict]:
    out: dict = {}
    err: dict = {}

    def numeric(key, lo, hi, specials=()):
        v = a.get(key)
        if v in specials:
            out[key] = v
            return v
        n, e = _int(v, lo, hi) if v not in (None, "") else (None, "This question is required.")
        if e:
            err[key] = e
        else:
            out[key] = n
        return n

    def choice(key, options):
        v = a.get(key)
        if v in options:
            out[key] = v
            return v
        err[key] = "Please choose one of the options."
        return None

    def cancer_types(key, other_key):
        sel = _types(a.get(key))
        if not sel:
            err[key] = "Please select at least one option."
        elif any(t not in CANCER_TYPES for t in sel):
            err[key] = "Please choose from the listed options."
        else:
            out[key] = ",".join(sel)
            if "Others" in sel:
                other = str(a.get(other_key) or "").strip()
                if not other:
                    err[other_key] = "Please specify the cancer type."
                else:
                    out[other_key] = other[:200]

    numeric("age", 18, 95)
    numeric("height_cm", 130, 200)
    numeric("weight_kg", 30, 150)
    numeric("q1_age", 8, 25, (DK,))
    q2 = numeric("q2_age", 20, 70, (NA, DK))
    if q2 == NA:
        choice("q3a", YN)
    choice("q3b", YN)
    choice("q4", YN)

    q5b = numeric("q5_age", 12, 55, (NEVER,))
    if q5b == NEVER:
        out["q5_count"] = 0  # auto; Q5A skipped, Q6 excluded
    elif q5b is not None:
        numeric("q5_count", 0, 20)
        numeric("q6", 0, 400)

    choice("q7", YN)
    if choice("q8", YN) == "Yes":
        out["q8_detail"] = str(a.get("q8_detail") or "").strip()[:500]
    if choice("q9", YN) == "Yes":
        cancer_types("q9_type", "q9_type_other")
    if choice("q10", YN) == "Yes":
        choice("q10_who", WHO)
        cancer_types("q10_type", "q10_type_other")
    return out, err
