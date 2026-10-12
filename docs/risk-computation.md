# PinkShieldAI Risk Computation

## Overview

PinkShieldAI computes breast cancer risk using a **BRISK-extended logistic regression model** calibrated with India-specific odds ratios. The model takes answers from a structured questionnaire (15 Tier 1 factors across 17 questions including sub-questions) and outputs a risk probability, risk level classification, contributing factors, protective factors, and personalised recommendations.

**Source code:** `backend/src/engine/risk_model.py`

## Mathematical Model

The core computation is standard logistic regression:

```
logit(p) = intercept + sum(coefficient_i * x_i)
p = 1 / (1 + exp(-logit))
```

Where:
- `intercept = -0.940`
- Each `coefficient_i` is the log odds ratio for factor `i`
- `x_i` is the encoded value of the respondent's answer for factor `i`
- `p` is the predicted risk probability (0 to 1)

## Coefficient Sources

| Source | Year | Factors Derived |
|--------|------|-----------------|
| BRISK (Banegas et al.) | 2017 | Age, parity, age at first birth, prior biopsy |
| Seshadri et al. | 2026 | Breastfeeding, central obesity |
| Vishwakarma et al. | 2019 | Physical activity, fried food intake |
| Sofi et al. | 2018 | Menstrual regularity |
| Jacob et al. | 2025 | Age at menarche |
| Nagrani et al. | 2016 | Age at menopause |

All odds ratios are drawn from studies on Indian populations or meta-analyses with Indian cohorts.

## Risk Classification (Snehitha Model)

The predicted probability is classified into four levels, validated for Indian populations:

| Risk Level | Probability Range | Interpretation |
|------------|-------------------|----------------|
| **Baseline** | < 40.04% | Population-average or below-average risk |
| **Evident** | 40.04% -- 57.4% | Moderately elevated risk |
| **Significant** | 57.4% -- 79.5% | Substantially elevated risk |
| **High** | >= 79.5% | Highly elevated risk |

## Factor-by-Factor Scoring

### 1.1 Age

- **Type:** Continuous (integer, 18--100)
- **Encoding:** Linear, `+0.027` per year of age
- **Rationale:** Risk increases steadily with age; in India, incidence peaks at 45--55

| Age | Contribution to logit |
|-----|----------------------|
| 30 | +0.810 |
| 45 | +1.215 |
| 55 | +1.485 |

### 1.2 + 1.2b Family History of Cancer

Family history is captured in two parts:
1. **Order of relation** (1.2): first order (mother, sister, daughter), second order (grandmother, aunt, niece), third order (any other relative), none, prefer not to answer
2. **Cancer type(s)** (1.2b): multi-select from 14 cancer types (breast, ovarian, uterine/endometrial, cervical, lung, colorectal, brain, prostate, stomach, liver, pancreatic, thyroid, leukemia/blood, other)

Risk is scored **only when breast cancer is present** in the selected cancer types. Non-breast cancer types are recorded for clinical completeness but do not affect the risk score.

| Relation Order | Breast Cancer in Family | Coefficient |
|----------------|------------------------|-------------|
| First order | Yes | **+0.810** |
| Second order | Yes | **+0.400** |
| Third order | Yes | **+0.200** |
| Any order | No (other cancers only) | 0.000 |
| None | N/A | 0.000 (protective flag) |
| Prefer not to answer | N/A | 0.000 |

Sub-question 1.2c (free text for "other" cancer type) is recorded but does not affect scoring.

### 1.3 Prior Breast Biopsy

- **Type:** Boolean (yes / no)
- **Encoding:** Binary

| Answer | Coefficient |
|--------|-------------|
| Yes | **+1.420** |
| No | 0.000 |

Includes history of breast biopsy, breast lump, or benign breast conditions (fibroadenoma, cysts).

### 1.4 Parity (Number of Childbirths)

- **Type:** Categorical (0, 1, 2, 3+)
- **Encoding:** Nulliparity penalised; high parity flagged as protective

| Answer | Coefficient | Note |
|--------|-------------|------|
| 0 (no children) | **+0.811** | Risk factor |
| 1 | 0.000 | |
| 2 | 0.000 | |
| 3+ | 0.000 | Flagged as protective |

### 1.4b Age at First Birth

- **Type:** Categorical (under 20, 20--24, 25--29, 30+)
- **Condition:** Only asked if parity >= 1

| Answer | Coefficient | Note |
|--------|-------------|------|
| Under 20 | 0.000 | Flagged as protective |
| 20--24 | 0.000 | |
| 25--29 | **+0.811** | Risk factor |
| 30 or older | **+1.035** | Risk factor |

### 1.5 Breastfeeding Duration

- **Type:** Categorical (never, < 6 months, 6--12 months, 12--24 months, > 24 months)
- **Condition:** Only asked if parity >= 1

| Answer | Coefficient | Note |
|--------|-------------|------|
| Never | **+1.306** | ln(3.69); strong risk factor |
| Under 6 months | **+0.500** | Risk factor |
| 6--12 months | **-0.300** | Protective |
| 12--24 months | **-0.600** | Protective |
| Over 24 months | **-0.892** | Strongly protective |

Breastfeeding is one of the strongest modifiable protective factors in Indian populations.

### 1.6 Waist Circumference (Central Obesity)

- **Type:** Categorical (< 80 cm, 80--88 cm, > 88 cm, don't know)

| Answer | Coefficient | Note |
|--------|-------------|------|
| Under 80 cm | 0.000 | Flagged as protective |
| 80--88 cm | **+0.400** | Elevated |
| Over 88 cm | **+1.008** | Risk factor |
| Don't know | 0.000 | No contribution |

Waist circumference is a stronger predictor of breast cancer risk in Indian women than BMI.

### 1.7 Physical Activity

- **Type:** Categorical (sedentary, light, moderate, vigorous)

| Answer | Coefficient | Note |
|--------|-------------|------|
| Sedentary | **+1.526** | Strong risk factor |
| Light | **+0.700** | |
| Moderate | 0.000 | |
| Vigorous | **-0.400** | Protective |

### 1.8 Fried Food Consumption

- **Type:** Categorical (daily, few times/week, once/week, rarely/never)

| Answer | Coefficient | Note |
|--------|-------------|------|
| Daily | **+1.361** | Strong risk factor |
| Few times/week | **+0.600** | |
| Once/week | 0.000 | |
| Rarely/never | 0.000 | Flagged as protective |

India-specific factor; includes pakoras, samosas, puris, and other deep-fried foods.

### 1.9 Menopausal Status

- **Type:** Categorical (premenopausal, perimenopausal, postmenopausal)
- **Encoding:** No direct coefficient. Used to gate sub-question 1.9b.

### 1.9b Age at Menopause

- **Type:** Continuous (integer, 30--65)
- **Condition:** Only asked if postmenopausal

| Age at Menopause | Coefficient | Note |
|------------------|-------------|------|
| > 50 | **+1.058** | Late menopause = risk factor |
| 45--50 | 0.000 | |
| < 45 | **-0.300** | Early menopause = protective |

Indian women reach menopause earlier on average (46--47 years) than Western women.

### 1.10 Menstrual Regularity

- **Type:** Boolean (yes / no)
- **Condition:** Only asked if pre- or perimenopausal

| Answer | Coefficient |
|--------|-------------|
| Regular (yes) | 0.000 |
| Irregular (no) | **+0.453** |

### 1.11 Age at Menarche

- **Type:** Continuous (integer, 8--20)
- **Encoding:** Linear, `-0.082` per year of age at first period

| Age at Menarche | Contribution to logit | Note |
|-----------------|----------------------|------|
| 10 | -0.820 | Early = risk factor |
| 12 | -0.984 | |
| 14 | -1.148 | Later = protective |

Earlier menarche means longer lifetime oestrogen exposure.

### 1.12 + 1.12b Breast Symptoms (Safety-Critical)

These two questions are **safety checks** and do not contribute to the risk score. If the respondent answers "yes" to either, the session is flagged for **urgent clinical referral**.

| Factor | Question | Trigger |
|--------|----------|---------|
| 1.12 | Breast changes (lump, thickening, pain, shape change) | If yes: referral + triggers 1.12b |
| 1.12b | Nipple discharge or skin changes | If yes: referral |

## Skip Logic

Some questions are conditionally skipped based on prior answers:

| Factor | Skipped When |
|--------|-------------|
| 1.2b (cancer types) | 1.2 = none or prefer_not_to_answer |
| 1.2c (other cancer text) | 1.2 = none or prefer_not_to_answer; also requires 1.2b includes "other" |
| 1.4b (age at first birth) | 1.4 = 0 (no children) |
| 1.5 (breastfeeding) | 1.4 = 0 (no children) |
| 1.9b (age at menopause) | 1.9 = premenopausal or perimenopausal |
| 1.10 (menstrual regularity) | 1.9 = postmenopausal |
| 1.12b (nipple discharge) | 1.12 = no |

## Worked Example

**Profile:** 50-year-old woman, first-order relative with breast cancer, no prior biopsy, 2 children (first at age 28), breastfed 18 months, waist 85 cm, moderate activity, fried food once/week, postmenopausal at age 52, menarche at age 12, no breast symptoms.

```
logit = -0.940 (intercept)
      + 0.027 * 50          = +1.350  (age)
      + 0.810               = +0.810  (first-order + breast cancer)
      + 0.000               = +0.000  (no prior biopsy)
      + 0.000               = +0.000  (parity = 2)
      + 0.811               = +0.811  (age at first birth 25-29)
      - 0.600               = -0.600  (breastfed 12-24 months)
      + 0.400               = +0.400  (waist 80-88 cm)
      + 0.000               = +0.000  (moderate activity)
      + 0.000               = +0.000  (fried food once/week)
      + 1.058               = +1.058  (menopause after 50)
      - 0.082 * 12          = -0.984  (menarche at 12)
                             --------
                     logit  =  1.905

p = 1 / (1 + exp(-1.905)) = 0.8706 = 87.1%

Risk level: High (>= 79.5%)
```

**Key risk factors:** Age 50, first-degree family history with breast cancer, late first birth, elevated waist, late menopause.

**Protective factors:** Breastfeeding 12--24 months.

## Recommendations Engine

After classification, the model generates personalised recommendations:

| Risk Level | Primary Recommendation |
|------------|----------------------|
| High | Consult a breast specialist; consider mammogram (if > 40) |
| Significant | Schedule clinical breast examination within months; discuss mammogram (if > 40) |
| Evident | Monthly breast self-examination; annual clinical examination |
| Baseline | Monthly self-examination; maintain healthy lifestyle |

Additionally:
- **Modifiable risk factors** (sedentary lifestyle, daily fried food, no breastfeeding, short breastfeeding, central obesity) are highlighted with actionable advice.
- **Physical activity** recommendations if sedentary or light activity.
- **Diet** recommendations if daily or frequent fried food consumption.

## Model Version

Current model version: **v0.1-mvp**

The model is a research prototype and is not a validated clinical tool. It is intended for risk awareness and screening triage, not diagnosis.
