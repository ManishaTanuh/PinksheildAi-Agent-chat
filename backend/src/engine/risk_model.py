"""BRISK-extended logistic regression model with India-specific ORs.

Coefficients from BRISK (Banegas 2017) extended with India-specific odds
ratios from Seshadri 2026, Vishwakarma 2019, Sofi 2018, Jacob 2025,
and Nagrani 2016 meta-analyses.

Risk categories from the Snehitha model (clinically validated for Indian
populations): Baseline (<40.04%), Evident (<57.4%), Significant (<79.5%),
High (>=79.5%).

logit(p) = intercept + sum(coefficient_i * x_i)
p = 1 / (1 + exp(-logit))
"""

import math

INTERCEPT = -0.940

RISK_THRESHOLDS = [
    ("baseline", 0.0, 0.4004),
    ("evident", 0.4004, 0.574),
    ("significant", 0.574, 0.795),
    ("high", 0.795, 1.01),
]


def compute_risk(answers: dict[str, str]) -> dict:
    """Compute breast cancer risk from questionnaire answers.

    Returns risk level, probability, contributing factors, protective factors,
    and recommendations.
    """
    logit = INTERCEPT
    risk_factors = []
    protective_factors = []

    # 1.1 Age (+0.027 per year)
    age = _int_or_none(answers.get("1.1"))
    if age is not None:
        contribution = 0.027 * age
        logit += contribution
        if age >= 45:
            risk_factors.append({"factor": "Age", "detail": f"Age {age} — risk increases with age"})

    # 1.2 + 1.2b Family history — scored only when breast cancer is in the family
    fh = answers.get("1.2")
    cancer_types = answers.get("1.2b", "")
    has_breast = "breast" in cancer_types.split(",") if cancer_types else False
    if fh == "first_order" and has_breast:
        logit += 0.810
        risk_factors.append({"factor": "Family history", "detail": "First-degree relative with breast cancer"})
    elif fh == "second_order" and has_breast:
        logit += 0.400
        risk_factors.append({"factor": "Family history", "detail": "Second-degree relative with breast cancer"})
    elif fh == "third_order" and has_breast:
        logit += 0.200
        risk_factors.append({"factor": "Family history", "detail": "Third-degree relative with breast cancer"})
    elif fh == "none":
        protective_factors.append({"factor": "Family history", "detail": "No family history of cancer"})

    # 1.3 Prior biopsy (+1.420 if yes)
    biopsy = answers.get("1.3")
    if biopsy == "yes":
        logit += 1.420
        risk_factors.append({"factor": "Prior biopsy", "detail": "History of breast biopsy or benign breast disease"})

    # 1.4 + 1.4b Parity and age at first birth
    parity = answers.get("1.4")
    afb = answers.get("1.4b")
    if parity == "0":
        logit += 0.811
        risk_factors.append({"factor": "Nulliparity", "detail": "No childbirths"})
    elif parity in ("3+",):
        protective_factors.append({"factor": "Parity", "detail": "Multiple childbirths are protective"})

    if afb == "30_plus":
        logit += 1.035
        risk_factors.append({"factor": "Late first birth", "detail": "First child at age 30 or older"})
    elif afb == "25_29":
        logit += 0.811
        risk_factors.append({"factor": "Late first birth", "detail": "First child between ages 25–29"})
    elif afb == "under_20":
        protective_factors.append({"factor": "Early first birth", "detail": "First child before age 20 is protective"})

    # 1.5 Breastfeeding (-0.892 for >24m, graded)
    bf = answers.get("1.5")
    if bf == "over_24m":
        logit += -0.892
        protective_factors.append({"factor": "Extended breastfeeding", "detail": "Breastfed over 24 months total"})
    elif bf == "12_24m":
        logit += -0.600
        protective_factors.append({"factor": "Breastfeeding", "detail": "Breastfed 12–24 months total"})
    elif bf == "6_12m":
        logit += -0.300
        protective_factors.append({"factor": "Breastfeeding", "detail": "Breastfed 6–12 months total"})
    elif bf == "never":
        logit += 1.306  # ln(3.69) for never breastfed
        risk_factors.append({"factor": "No breastfeeding", "detail": "Never breastfed despite having children"})
    elif bf == "under_6m":
        logit += 0.500
        risk_factors.append({"factor": "Short breastfeeding", "detail": "Breastfed less than 6 months total"})

    # 1.6 Central obesity (+1.008 for waist >88cm)
    waist = answers.get("1.6")
    if waist == "over_88cm":
        logit += 1.008
        risk_factors.append({"factor": "Central obesity", "detail": "Waist over 88 cm"})
    elif waist == "80_to_88cm":
        logit += 0.400
        risk_factors.append({"factor": "Elevated waist size", "detail": "Waist between 80–88 cm"})
    elif waist == "under_80cm":
        protective_factors.append({"factor": "Healthy waist", "detail": "Waist under 80 cm"})

    # 1.7 Physical activity (+1.526 for sedentary)
    activity = answers.get("1.7")
    if activity == "sedentary":
        logit += 1.526
        risk_factors.append({"factor": "Sedentary lifestyle", "detail": "Mostly sitting, limited physical activity"})
    elif activity == "light":
        logit += 0.700
    elif activity == "vigorous":
        logit += -0.400
        protective_factors.append({"factor": "Active lifestyle", "detail": "Regular exercise or physical labor"})

    # 1.8 Fried food (+1.361 for daily)
    fried = answers.get("1.8")
    if fried == "daily":
        logit += 1.361
        risk_factors.append({"factor": "Daily fried food", "detail": "Daily consumption of fried or deep-fried foods"})
    elif fried == "few_times_week":
        logit += 0.600
    elif fried == "rarely_never":
        protective_factors.append({"factor": "Low fried food", "detail": "Rarely eating fried foods"})

    # 1.9b Age at menopause (+1.058 for >50)
    menopause_age = _int_or_none(answers.get("1.9b"))
    if menopause_age is not None:
        if menopause_age > 50:
            logit += 1.058
            risk_factors.append({"factor": "Late menopause", "detail": f"Menopause at age {menopause_age} (after 50)"})
        elif menopause_age < 45:
            logit += -0.300
            protective_factors.append({"factor": "Early menopause", "detail": f"Menopause at age {menopause_age} (before 45)"})

    # 1.10 Menstrual regularity (+0.453 for irregular)
    regularity = answers.get("1.10")
    if regularity == "no":
        logit += 0.453
        risk_factors.append({"factor": "Irregular cycles", "detail": "Irregular menstrual cycles"})

    # 1.11 Age at menarche (-0.082 per year)
    menarche = _int_or_none(answers.get("1.11"))
    if menarche is not None:
        contribution = -0.082 * menarche
        logit += contribution
        if menarche < 12:
            risk_factors.append({"factor": "Early menarche", "detail": f"First period at age {menarche}"})
        elif menarche >= 14:
            protective_factors.append({"factor": "Later menarche", "detail": f"First period at age {menarche}"})

    probability = 1.0 / (1.0 + math.exp(-logit))
    risk_level = _classify_risk(probability)
    recommendations = _get_recommendations(risk_level, risk_factors, answers)

    return {
        "risk_level": risk_level,
        "risk_probability": round(probability, 4),
        "logit": round(logit, 4),
        "key_risk_factors": risk_factors,
        "protective_factors": protective_factors,
        "recommendations": recommendations,
        "model_version": "v0.1-mvp",
    }


def _classify_risk(probability: float) -> str:
    for level, low, high in RISK_THRESHOLDS:
        if low <= probability < high:
            return level
    return "high"


def _get_recommendations(risk_level: str, risk_factors: list[dict], answers: dict) -> list[str]:
    recs = []

    if risk_level == "high":
        recs.append("We strongly recommend you consult a breast specialist for a clinical breast examination and further evaluation.")
        recs.append("Consider asking your doctor about a screening mammogram, especially if you are over 40.")
    elif risk_level == "significant":
        recs.append("We recommend scheduling a clinical breast examination with your doctor within the next few months.")
        recs.append("If you are over 40, discuss mammogram screening with your doctor.")
    elif risk_level == "evident":
        recs.append("Continue regular breast self-examination once a month.")
        recs.append("Schedule a clinical breast examination with your doctor at least once a year.")
    else:
        recs.append("Continue regular breast self-examination once a month.")
        recs.append("Maintain a healthy lifestyle with regular physical activity and a balanced diet.")

    modifiable = []
    for rf in risk_factors:
        if rf["factor"] in ("Sedentary lifestyle", "Daily fried food", "No breastfeeding", "Short breastfeeding", "Central obesity"):
            modifiable.append(rf["factor"].lower())

    if modifiable:
        recs.append(f"Modifiable risk factors identified: {', '.join(modifiable)}. Small lifestyle changes can reduce your risk.")

    if answers.get("1.7") in ("sedentary", "light"):
        recs.append("Try to include at least 30 minutes of moderate physical activity most days of the week.")

    if answers.get("1.8") in ("daily", "few_times_week"):
        recs.append("Consider reducing fried food intake and including more fruits, vegetables, and whole grains.")

    return recs


def _int_or_none(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None
