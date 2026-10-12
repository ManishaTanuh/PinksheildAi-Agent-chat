# Breast Cancer Risk Assessment Tools — Global Landscape

## Overview

Breast cancer risk assessment tools estimate a woman's probability of developing breast cancer over a defined time period. They vary in complexity, inputs required, and populations they serve. No single tool dominates — clinicians choose based on available data and clinical context.

---

## 1. Gail Model (BCRAT)

### Summary
| Attribute | Details |
|---|---|
| **Full name** | Breast Cancer Risk Assessment Tool (BCRAT) |
| **Developer** | Dr. Mitchell H. Gail, National Cancer Institute (NCI), USA |
| **Year** | 1989 (original); 1999 (Model 2); 2007 (CARE model for African Americans) |
| **Key publication** | Gail et al., JNCI, 1989 |
| **Availability** | Free at bcrisktool.cancer.gov |
| **Time to complete** | ~2 minutes |

### Risk Factors (7–8 inputs)
1. Age
2. Age at menarche (<12, 12–13, ≥14)
3. Age at first live birth (<20, 20–24, 25–29, ≥30, nulliparous)
4. Number of first-degree relatives with breast cancer (0, 1, ≥2)
5. Number of prior breast biopsies (0, 1, ≥2)
6. Atypical hyperplasia on biopsy (yes/no/unknown)
7. Race/ethnicity (for baseline rate selection)

### Outputs
- 5-year absolute risk
- Lifetime risk (to age 90)
- Population average comparison

### Clinical Thresholds
| Threshold | Clinical Use |
|---|---|
| ≥1.67% five-year risk | Chemoprevention eligibility (USPSTF, NSABP P-1 criterion) |
| ≥20% lifetime risk | Enhanced screening consideration (though ACS prefers more comprehensive models for this) |

### Validation & Accuracy
| Metric | Value |
|---|---|
| Calibration (E/O ratio) | ~0.9–1.1 (excellent at population level) |
| Discrimination (C-statistic) | 0.56–0.63 (modest individual-level) |
| Populations validated | White, African American (CARE model), Hispanic, Asian American/Pacific Islander |

### Strengths
- Simplest and fastest of all major tools
- Well-calibrated at population level
- Race/ethnicity-specific versions exist
- Most widely used tool globally (~3,000+ citations)
- Standard for chemoprevention eligibility
- Free, publicly available

### Limitations
- **No second-degree or paternal family history**
- **No breast density** (strongest independent risk factor)
- **No genetic mutations** (BRCA1/2 excluded)
- **No BMI, HRT, lifestyle factors**
- Low individual-level discrimination (AUC ~0.58)
- US baseline rates — **overestimates risk ~3–5x in India** without recalibration
- **Sensitivity only 10.3% in Western Indian population** (Kumar et al. 2020, PMID 33163382) — essentially useless for individual-level prediction in India
- Excludes women with prior breast cancer or LCIS

---

## 2. IBIS / Tyrer-Cuszick Model

### Summary
| Attribute | Details |
|---|---|
| **Full name** | IBIS Breast Cancer Risk Evaluation Tool (Tyrer-Cuszick Model) |
| **Developers** | Prof. Jack Cuszick & Dr. Jonathan Tyrer |
| **Institution** | Centre for Cancer Prevention, Queen Mary University of London |
| **Year** | 2004 (v6); 2013 (v7 + density); 2017–18 (v8 + BMI + ATM/CHEK2/PALB2) |
| **Key publication** | Tyrer et al., Statistics in Medicine, 2004 |
| **Availability** | Free at ems-trials.org/riskevaluator (web + Windows download) |
| **Time to complete** | ~10–15 minutes |

### Risk Factors (15–20+ inputs)

**Personal:** Age, height, weight/BMI, Ashkenazi Jewish ancestry

**Reproductive/Hormonal:**
- Age at menarche
- Parity, age at first live birth
- Menopausal status, age at menopause, type of menopause
- HRT use (type, duration, current/past)

**Breast-specific:**
- Mammographic breast density (BI-RADS or Volpara)
- Prior biopsies, atypical hyperplasia (ADH/ALH), LCIS

**Genetic:**
- BRCA1/BRCA2 test results (or estimates carrier probability)
- ATM, CHEK2, PALB2 (v8)

**Family history (extensive pedigree):**
- First, second, and third-degree relatives
- Both maternal and paternal lineage
- Age at diagnosis, bilateral cancer, ovarian cancer
- Male breast cancer
- Unaffected relatives (informative for BRCA probability)

### Outputs
- 10-year absolute risk
- Lifetime risk (to age 85)
- BRCA1 carrier probability
- BRCA2 carrier probability

### Validation & Accuracy
| Metric | Value |
|---|---|
| Calibration (E/O ratio) | 0.9–1.2 (good in Caucasian populations) |
| Discrimination (C-statistic) | 0.57–0.65 (without density); 0.70–0.76 (v8 with density) |
| Key validations | UK family history clinics, Mayo Clinic, Nurses' Health Study, BCSC (US) |

### Guideline Endorsements
| Organization | Use |
|---|---|
| **NICE (UK)** | Primary recommended tool for risk stratification (CG164) |
| **NCCN (US)** | Acceptable for risk assessment and MRI eligibility |
| **ACS (US)** | Acceptable for MRI screening eligibility (≥20–25% lifetime) |

### Strengths
- **Most comprehensive** risk factor coverage of any widely available tool
- **Produces BRCA carrier probability** — unique among personal risk models
- **Includes breast density** (v7+) — substantially improves discrimination
- Handles complex family histories including paternal lineage
- Well-validated in Caucasian populations
- Endorsed by NICE, NCCN, ACS

### Limitations
- **UK baseline rates** — overestimates risk in lower-incidence populations
- Moderate discrimination without density (~0.60)
- **No polygenic risk scores (PRS)** yet
- Does not capture physical activity, alcohol, breastfeeding
- Requires detailed pedigree — time-consuming
- Windows-only downloadable version
- **Not validated in Indian populations** — recalibration required

---

## 3. BOADICEA / CanRisk

### Summary
| Attribute | Details |
|---|---|
| **Full name** | Breast and Ovarian Analysis of Disease Incidence and Carrier Estimation Algorithm |
| **Developer** | Prof. Antonis Antoniou, University of Cambridge |
| **Year** | 2004 (original); updated continuously; CanRisk web tool launched ~2019 |
| **Availability** | Free at canrisk.org (requires clinician registration) |

### What Makes It Different
- **Most genetically sophisticated** model available
- Incorporates **polygenic risk scores (PRS)** — a 313-SNP score for breast cancer
- Models BRCA1, BRCA2, PALB2, CHEK2, ATM as separate genes with age-specific penetrance
- Uses a **polygenic + monogenic** combined architecture
- Can incorporate mammographic density and other personal risk factors (in CanRisk v2+)

### Risk Factors
- Detailed family pedigree (similar depth to IBIS)
- Known genetic test results (BRCA1/2, PALB2, CHEK2, ATM, RAD51C, RAD51D)
- Polygenic risk score (if available from genotyping)
- Mammographic density
- Age at menarche, parity, age at first birth
- HRT, oral contraceptive use
- BMI, height
- Menopausal status, age at menopause
- Prior biopsies, atypical hyperplasia
- Tubal ligation, oophorectomy, mastectomy (risk-reducing surgery)

### Outputs
- 10-year and lifetime breast cancer risk
- Ovarian cancer risk
- BRCA1/BRCA2/PALB2/CHEK2/ATM carrier probabilities
- Contralateral breast cancer risk (for women with prior cancer)

### Validation & Accuracy
| Metric | Value |
|---|---|
| Discrimination (AUC) with PRS | 0.68–0.72 |
| Discrimination without PRS | 0.61–0.65 |
| Calibration | Generally good in European populations |

### Strengths
- Gold standard for genetic risk assessment
- Only major tool to fully integrate PRS
- Models contralateral risk and ovarian cancer
- CanRisk web tool is well-designed and free
- Recommended by UK NHS Genomic Medicine Service

### Limitations
- Requires genetic data for maximum accuracy
- PRS calibrated on European populations — **poor transferability to South Asian ancestry**
- Complex to use — designed for genetic counselors
- Less validated outside European populations
- Not widely used outside UK/Europe/Australasia

---

## 4. BCSC Model (Breast Cancer Surveillance Consortium)

### Summary
| Attribute | Details |
|---|---|
| **Developer** | BCSC, University of California San Francisco |
| **Year** | 2008 (Tice et al.); updated versions |
| **Key feature** | Incorporates **breast density** into a simple model |

### Risk Factors
- Age
- Race/ethnicity
- Family history (first-degree relatives)
- Prior breast biopsy
- Breast density (BI-RADS)

### Validation & Accuracy
| Metric | Value |
|---|---|
| Discrimination (AUC) | 0.63–0.66 |

### Strengths
- One of few simple models that includes breast density
- Validated in large US screening population (~1.1 million women)
- Good for mammography-based risk stratification

### Limitations
- US-specific baseline rates
- Limited risk factor set (no reproductive/hormonal factors)

---

## 5. Other Notable Tools

### Claus Model
| Attribute | Details |
|---|---|
| **Developer** | Elizabeth Claus, Yale |
| **Year** | 1991 |
| **Focus** | Family history only — both maternal and paternal |
| **Limitation** | No personal risk factors; largely superseded by IBIS and BOADICEA |

### BRCAPRO
| Attribute | Details |
|---|---|
| **Developer** | Berry & Parmigiani, Duke/Harvard |
| **Focus** | Bayesian model for BRCA1/BRCA2 carrier probability |
| **Outputs** | BRCA1/BRCA2 carrier probabilities + breast/ovarian cancer risk |
| **Usage** | Genetic counseling referrals; available in BayesMendel R package |

### Rosner-Colditz Model
| Attribute | Details |
|---|---|
| **Developer** | Harvard, from the Nurses' Health Study |
| **Focus** | Detailed hormonal and reproductive factors |
| **Unique inputs** | Endogenous hormone levels, breastfeeding duration, type of menopause |
| **Limitation** | Not available as a clinical tool; research use |

### Manchester Scoring System
| Attribute | Details |
|---|---|
| **Focus** | Point-based scoring for BRCA testing referral |
| **Usage** | UK NHS genetics services for triaging genetic testing referrals |

### iCARE (Individualized Coherent Absolute Risk Estimator)
| Attribute | Details |
|---|---|
| **Developer** | NCI (Chatterjee et al.) |
| **Focus** | Integrates clinical risk factors + PRS into absolute risk |
| **Status** | Research framework; available as Bioconductor R package (`BiocManager::install("iCARE")`) |
| **Non-Western validation** | Successfully applied to sub-Saharan African women — AUC **0.723** (Guo et al. 2025, JAMA Network Open, PMID 40249615) |
| **Latest enhancement** | Density integration (Mulder et al. 2025, PMID 41034228) |
| **Relevance to PinkShieldAI** | iCARE's architecture (population-specific baseline hazards + relative risk parameters) is the closest existing framework to what PinkShieldAI needs — an India-recalibrated version is technically feasible |

---

## 6. AI/Deep Learning Approaches (Emerging)

### Mirai (MIT/MGH)
- Deep learning model that predicts breast cancer risk from mammogram images alone
- Trained on 200,000+ mammograms from Massachusetts General Hospital
- Validated across multiple international sites (Sweden, Taiwan)
- AUC: 0.70–0.76 (exceeds all traditional questionnaire-based models)
- Predicts 1–5 year risk from a single mammogram
- Does not require any questionnaire input — purely image-based

### Hybrid Approaches
- Combining imaging AI (Mirai-type) + clinical risk factors + PRS shows the best discrimination
- AUC potentially 0.75–0.80+ in research settings
- Not yet in routine clinical use

### Implications for PinkShieldAI
- Image-based AI requires mammograms — not available for most Indian women
- Questionnaire-based risk assessment remains essential for population-level screening in India
- Hybrid approach (questionnaire → risk score → targeted mammography referral) is the practical path

---

## Comparative Summary

| Tool | Inputs | Time | AUC | Density | Genetics | Family Depth | Free | India-Ready |
|---|---|---|---|---|---|---|---|---|
| **Gail (BCRAT)** | 7–8 | 2 min | 0.58 | No | No | 1st-degree only | Yes | No (needs recalibration) |
| **IBIS (Tyrer-Cuszick)** | 15–20+ | 10–15 min | 0.65–0.76 | Yes (v7+) | BRCA | 1st/2nd/3rd-degree | Yes | No (needs recalibration) |
| **BOADICEA (CanRisk)** | 20+ | 15–20 min | 0.68–0.72 | Yes | BRCA + 5 genes + PRS | Full pedigree | Yes | No (PRS not transferable) |
| **BCSC** | 5 | 2 min | 0.63–0.66 | Yes | No | 1st-degree only | Yes | No |
| **Snehita BRISK** | 8 scored (of ~47 collected) | 5–10 min | ~0.70+ | No | No | 1st-degree | Yes (snehita.in/risk) | **Designed for India** (Kerala-validated) |
| **Mirai (AI)** | Mammogram | N/A | 0.70–0.76 | Implicit | No | No | Research | Needs mammogram |

### Key Insight for PinkShieldAI

**No existing tool is both validated for Indian women AND usable at population scale without mammography or genetic testing.** This is the gap PinkShieldAI fills — an India-calibrated, questionnaire-based risk assessment that can be delivered via voice/chat to millions of women who will never walk into a genetics clinic or get a mammogram.
