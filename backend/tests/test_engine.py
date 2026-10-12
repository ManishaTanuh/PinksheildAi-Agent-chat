"""Tests for the questionnaire engine: factors, validation, state machine, and risk model."""
import pytest
from src.engine.factors import FACTORS_BY_ID, TIER_1_ORDER, TIER_1_FACTORS
from src.engine.validation import validate_answer
from src.engine.risk_model import compute_risk


class TestFactorRegistry:
    def test_all_tier1_factors_present(self):
        expected_ids = [
            "1.1", "1.2", "1.2b", "1.2c", "1.3", "1.4", "1.4b", "1.5",
            "1.6", "1.7", "1.8", "1.9", "1.9b", "1.10",
            "1.11", "1.12", "1.12b",
        ]
        for fid in expected_ids:
            assert fid in FACTORS_BY_ID, f"Missing factor {fid}"

    def test_factor_count(self):
        assert len(TIER_1_FACTORS) == 17

    def test_all_factors_have_questions(self):
        for f in TIER_1_FACTORS:
            assert f.question, f"Factor {f.id} missing question"
            assert f.data_type in ("integer", "categorical", "boolean", "multi_select", "text")

    def test_all_factors_have_ui_type(self):
        for f in TIER_1_FACTORS:
            assert f.ui_type in ("slider", "radio", "dropdown", "multi_select", "text"), \
                f"Factor {f.id} has invalid ui_type: {f.ui_type}"

    def test_factors_with_options_have_display_labels(self):
        for f in TIER_1_FACTORS:
            if f.options and f.data_type != "text":
                assert f.display_labels, f"Factor {f.id} has options but no display_labels"
                for opt in f.options:
                    assert opt in f.display_labels, f"Factor {f.id} missing display_label for '{opt}'"

    def test_safety_critical_factors(self):
        safety = [f for f in TIER_1_FACTORS if f.is_safety_critical]
        assert len(safety) == 2
        ids = {f.id for f in safety}
        assert ids == {"1.12", "1.12b"}

    def test_family_history_options(self):
        fh = FACTORS_BY_ID["1.2"]
        assert "first_order" in fh.options
        assert "second_order" in fh.options
        assert "third_order" in fh.options
        assert "none" in fh.options
        assert "prefer_not_to_answer" in fh.options

    def test_cancer_types_is_multi_select(self):
        ct = FACTORS_BY_ID["1.2b"]
        assert ct.data_type == "multi_select"
        assert ct.ui_type == "multi_select"
        assert "breast" in ct.options
        assert "other" in ct.options

    def test_cancer_other_is_text(self):
        co = FACTORS_BY_ID["1.2c"]
        assert co.data_type == "text"
        assert co.ui_type == "text"


class TestValidation:
    def test_valid_age(self):
        ok, err = validate_answer("1.1", "45")
        assert ok and err is None

    def test_age_too_low(self):
        ok, err = validate_answer("1.1", "10")
        assert not ok

    def test_age_too_high(self):
        ok, err = validate_answer("1.1", "150")
        assert not ok

    def test_age_not_number(self):
        ok, err = validate_answer("1.1", "forty")
        assert not ok

    def test_valid_categorical(self):
        ok, err = validate_answer("1.4", "0")
        assert ok

    def test_invalid_categorical(self):
        ok, err = validate_answer("1.4", "5")
        assert not ok

    def test_valid_boolean(self):
        ok, err = validate_answer("1.3", "yes")
        assert ok

    def test_invalid_boolean(self):
        ok, err = validate_answer("1.3", "maybe")
        assert not ok

    def test_unknown_factor(self):
        ok, err = validate_answer("99.99", "foo")
        assert not ok

    def test_family_history_first_order(self):
        ok, err = validate_answer("1.2", "first_order")
        assert ok

    def test_family_history_none(self):
        ok, err = validate_answer("1.2", "none")
        assert ok

    def test_family_history_prefer_not_to_answer(self):
        ok, err = validate_answer("1.2", "prefer_not_to_answer")
        assert ok

    def test_family_history_invalid(self):
        ok, err = validate_answer("1.2", "yes")
        assert not ok

    def test_multi_select_single(self):
        ok, err = validate_answer("1.2b", "breast")
        assert ok

    def test_multi_select_multiple(self):
        ok, err = validate_answer("1.2b", "breast,ovarian,lung")
        assert ok

    def test_multi_select_invalid_option(self):
        ok, err = validate_answer("1.2b", "breast,fake_cancer")
        assert not ok

    def test_multi_select_empty(self):
        ok, err = validate_answer("1.2b", "")
        assert not ok

    def test_text_valid(self):
        ok, err = validate_answer("1.2c", "some rare cancer type")
        assert ok

    def test_text_empty(self):
        ok, err = validate_answer("1.2c", "")
        assert not ok

    def test_text_too_long(self):
        ok, err = validate_answer("1.2c", "x" * 501)
        assert not ok


class TestRiskModel:
    def test_low_risk_profile(self):
        """Young woman with all protective factors."""
        answers = {
            "1.1": "30",
            "1.2": "none",
            "1.3": "no",
            "1.4": "2",
            "1.4b": "under_20",
            "1.5": "over_24m",
            "1.6": "under_80cm",
            "1.7": "vigorous",
            "1.8": "rarely_never",
            "1.9": "premenopausal",
            "1.10": "yes",
            "1.11": "14",
            "1.12": "no",
        }
        result = compute_risk(answers)
        assert result["risk_level"] == "baseline"
        assert result["risk_probability"] < 0.40
        assert len(result["protective_factors"]) > 0

    def test_high_risk_profile(self):
        """Older woman with multiple risk factors."""
        answers = {
            "1.1": "55",
            "1.2": "first_order",
            "1.2b": "breast",
            "1.3": "yes",
            "1.4": "0",
            "1.6": "over_88cm",
            "1.7": "sedentary",
            "1.8": "daily",
            "1.9": "postmenopausal",
            "1.9b": "53",
            "1.11": "10",
            "1.12": "no",
        }
        result = compute_risk(answers)
        assert result["risk_level"] in ("significant", "high")
        assert result["risk_probability"] > 0.55
        assert len(result["key_risk_factors"]) > 3

    def test_moderate_risk_profile(self):
        """Mixed risk and protective factors."""
        answers = {
            "1.1": "38",
            "1.2": "none",
            "1.3": "no",
            "1.4": "2",
            "1.4b": "20_24",
            "1.5": "12_24m",
            "1.6": "80_to_88cm",
            "1.7": "moderate",
            "1.8": "few_times_week",
            "1.9": "premenopausal",
            "1.10": "yes",
            "1.11": "13",
            "1.12": "no",
        }
        result = compute_risk(answers)
        assert result["risk_probability"] > 0.10
        assert result["risk_probability"] < 0.80

    def test_empty_answers(self):
        """Should still compute with intercept only."""
        result = compute_risk({})
        assert "risk_level" in result
        assert "risk_probability" in result
        assert result["model_version"] == "v0.1-mvp"

    def test_recommendations_present(self):
        answers = {"1.1": "50", "1.7": "sedentary", "1.8": "daily"}
        result = compute_risk(answers)
        assert len(result["recommendations"]) > 0

    def test_breastfeeding_never_vs_extended(self):
        """Never breastfed should produce higher risk than extended."""
        base = {"1.1": "40", "1.4": "2", "1.4b": "25_29"}
        never = compute_risk({**base, "1.5": "never"})
        extended = compute_risk({**base, "1.5": "over_24m"})
        assert never["risk_probability"] > extended["risk_probability"]

    def test_risk_levels_are_ordered(self):
        result_low = compute_risk({"1.1": "25"})
        result_high = compute_risk({
            "1.1": "55", "1.2": "first_order", "1.2b": "breast",
            "1.3": "yes", "1.4": "0", "1.7": "sedentary", "1.8": "daily",
        })
        assert result_low["risk_probability"] < result_high["risk_probability"]

    def test_family_history_order_affects_risk(self):
        """First-order family history should have higher risk than third-order."""
        base = {"1.1": "45", "1.2b": "breast"}
        first = compute_risk({**base, "1.2": "first_order"})
        third = compute_risk({**base, "1.2": "third_order"})
        assert first["risk_probability"] > third["risk_probability"]

    def test_family_history_non_breast_cancer_no_effect(self):
        """Non-breast cancer in family should not add risk."""
        base = {"1.1": "45"}
        no_fh = compute_risk({**base, "1.2": "none"})
        lung_only = compute_risk({**base, "1.2": "first_order", "1.2b": "lung"})
        assert abs(no_fh["risk_probability"] - lung_only["risk_probability"]) < 0.01
