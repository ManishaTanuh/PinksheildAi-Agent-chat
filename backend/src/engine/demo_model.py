"""Stateless demo risk model: pilot-questionnaire answers -> HIGH / LOW risk.

Pure-Python inference over weights exported by ml/train_demo_model.py
(demo_model.json). Nothing is stored or logged. DEMO ONLY - trained on a
synthetic cohort labelled by simple screening rules, not a diagnostic tool.
"""
import json
import math
from pathlib import Path

from .demo_features import encode

_MODEL = json.loads((Path(__file__).parent / "demo_model.json").read_text())


def predict(answers: dict) -> dict:
    names, vals = encode(answers)
    logit = _MODEL["intercept"] + sum(w * x for w, x in zip(_MODEL["weights"], vals))
    prob = 1.0 / (1.0 + math.exp(-logit))

    contribs = sorted(((n, w * x) for n, w, x in zip(names, _MODEL["weights"], vals) if x),
                      key=lambda t: abs(t[1]), reverse=True)
    drivers = [{"feature": n, "effect": "raises risk" if c > 0 else "lowers risk"}
               for n, c in contribs if abs(c) > 0.1 and not n.endswith("answered")][:5]

    symptoms = str(answers.get("symptoms", "")).strip().lower() == "yes"
    high = prob >= _MODEL["threshold"] or symptoms
    return {
        "risk_class": "HIGH_RISK" if high else "LOW_RISK",
        "probability": round(prob, 4),
        "symptom_override": symptoms,
        "top_drivers": drivers,
        "disclaimer": "Demo model trained on synthetic data. Not a diagnosis.",
    }
