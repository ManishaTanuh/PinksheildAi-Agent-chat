"""Tests for the stateless demo risk model (needs src/engine/demo_model.json from ml/train_demo_model.py)."""
from src.engine.demo_model import predict

LOW = {"age": 32, "height_cm": 160, "weight_kg": 55, "symptoms": "No", "tobacco_use": "No", "alcohol_use": "No",
       "q1_age": 14, "q2_age": "Not applicable", "q3a": "No", "q3b": "No", "q4": "No", "q5_count": 3,
       "q5_age": 21, "q6": 40, "q7": "No", "q8": "No", "q9": "No", "q10": "No"}
HIGH = {"age": 52, "height_cm": 155, "weight_kg": 85, "symptoms": "No", "tobacco_use": "No", "alcohol_use": "No",
        "q1_age": 10, "q2_age": 56, "q3a": "Yes", "q3b": "Yes", "q4": "Yes", "q5_count": 1, "q5_age": 30,
        "q6": 2, "q7": "No", "q8": "Yes", "q9": "No", "q10": "Yes",
        "q10_who": "First Order (Mother, Sibling, Father)", "q10_type": "Breast Cancer"}


def test_low_and_high_profiles():
    assert predict(LOW)["risk_class"] == "LOW_RISK"
    assert predict(HIGH)["risk_class"] == "HIGH_RISK"


def test_symptoms_force_high():
    r = predict({**LOW, "symptoms": "Yes"})
    assert r["risk_class"] == "HIGH_RISK" and r["symptom_override"]


def test_missing_answers_do_not_crash():
    assert predict({"age": 40})["risk_class"] in ("HIGH_RISK", "LOW_RISK")


# ---- chat questionnaire validation (src/engine/demo_validation.py) ----
from src.engine.demo_validation import validate

NEVER = "Never had a baby/Full time pregnancy"
BASE = {"age": 40, "height_cm": 160, "weight_kg": 60, "q1_age": 12, "q2_age": 50, "q3b": "No", "q4": "No", "q5_age": 22, "q5_count": 2, "q6": 12,
        "q7": "No", "q8": "No", "q9": "No", "q10": "No"}


def test_numeric_messages():
    assert validate({**BASE, "q1_age": "abc"})[1]["q1_age"] == "Please enter a valid number."
    assert validate({**BASE, "q1_age": 30})[1]["q1_age"] == "Please enter a number between 8 and 25."
    assert validate({**BASE, "q6": 401})[1]["q6"] == "Please enter a number between 0 and 400."
    assert validate(BASE)[1] == {}


def test_conditionals_clear_stale_answers():
    clean, err = validate({**BASE, "q3a": "Yes", "q5_age": NEVER, "q6": 30, "q8": "No", "q8_detail": "x"})
    assert not err and "q3a" not in clean and clean["q5_count"] == 0 and "q6" not in clean and "q8_detail" not in clean


def test_special_options_not_numbers():
    clean, err = validate({**BASE, "q1_age": "Don't know", "q2_age": "Not applicable", "q3a": "Yes"})
    assert not err and clean["q1_age"] == "Don't know" and clean["q3a"] == "Yes"


def test_cancer_follow_ups_required():
    assert "q9_type" in validate({**BASE, "q9": "Yes"})[1]
    e = validate({**BASE, "q10": "Yes", "q10_who": "I don't know", "q10_type": "Others"})[1]
    assert "q10_type_other" in e


def test_basic_details_ranges():
    assert validate({**BASE, "age": 17})[1]["age"] == "Please enter a number between 18 and 95."
    assert validate({**BASE, "height_cm": 220})[1]["height_cm"] == "Please enter a number between 130 and 200."
    assert validate({**BASE, "weight_kg": "x"})[1]["weight_kg"] == "Please enter a valid number."


def test_personal_high_related_cancer_forces_high():
    r = predict({**LOW, "q9": "Yes", "q9_type": "Breast Cancer"})
    assert r["risk_class"] == "HIGH_RISK" and r["cancer_history_override"]
    # a mid/other-related type is not forced
    assert not predict({**LOW, "q9": "Yes", "q9_type": "Thyroid Cancer"})["cancer_history_override"]


def test_decimals_accepted_except_pregnancy_count():
    clean, err = validate({**BASE, "height_cm": "158.5", "weight_kg": 62.3, "age": "41.5", "q6": "7,5"})
    assert not err and clean["height_cm"] == 158.5 and clean["weight_kg"] == 62.3 and clean["q6"] == 7.5
    assert validate({**BASE, "q5_count": "2.5"})[1]["q5_count"] == "Please enter a valid number."
    assert validate({**BASE, "height_cm": "129.9"})[1]["height_cm"] == "Please enter a number between 130 and 200."
    assert validate({**BASE, "weight_kg": "1.2.3"})[1]["weight_kg"] == "Please enter a valid number."
