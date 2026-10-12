# PinkShieldAI — Agentic Questionnaire Factor Hierarchy

## How This Document Works

This is the master reference for the PinkShieldAI agentic chatbot's question selection logic. Factors are organized into **4 tiers** reflecting evidence strength and conversational priority. The agent asks Tier 1 questions to every woman, then adaptively selects from Tiers 2–4 based on accumulated risk signals.

**Design principles:**
- Conversational, not clinical — questions should feel like a health check-in, not a medical exam
- Voice/chat-friendly — all questions must work over WhatsApp text or voice call in any Indian language
- No medical infrastructure required — no mammogram, no blood test, no genetic test
- Adaptive — the agent decides what to ask next based on prior answers; not every woman gets every question
- Evidence-grounded — every factor links to India-specific OR from meta-analyses or individual studies (see docs 05, 06)

**Target completion times:**
| Path | Questions | Time |
|---|---|---|
| Tier 1 only (low-risk fast track) | ~12 | ~4 min |
| Tier 1 + Tier 2 (standard) | ~22–28 | ~8 min |
| Tier 1 + 2 + 3 (enriched) | ~32–38 | ~11 min |
| Full (including Tier 4 research) | ~42–48 | ~14 min |

---

## Tier 1 — Always Ask (Core Risk Stratification)

**Every woman answers these.** These ~12 factors capture the highest-evidence risk signals from Indian meta-analyses. They alone should deliver ~75% of the model's discriminative power.

**Agent rule:** Always ask. No skipping. Order is optimized for conversational flow — demographics first, then reproductive history, then body/lifestyle, then safety check.

---

### 1.1 Age

| Attribute | Details |
|---|---|
| **Question** | "How old are you?" / "What is your age?" |
| **Data type** | Integer (years) |
| **Why it matters** | Sets baseline risk; Indian breast cancer peaks at 45–55 (a decade earlier than the West). Risk rises with age but the age-incidence curve differs from Western models. |
| **India-specific evidence** | Peak age 45–55; ~40–50% diagnosed under 50 (vs ~20% in US/UK). BRISK coefficient: +0.027 per year. |
| **In other tools** | Gail ✓ · IBIS ✓ · BOADICEA ✓ · BRISK ✓ |
| **Adaptive trigger** | Age <35 → flag as young-onset context (different risk factor profile per Nishtha 2026). Age >50 → trigger menopause questions in 1.9. |

---

### 1.2 Family History of Breast Cancer (First-Degree)

| Attribute | Details |
|---|---|
| **Question** | "Has your mother, sister, or daughter ever been diagnosed with breast cancer?" |
| **Data type** | Yes / No / Don't know |
| **Why it matters** | **Strongest risk factor in Indian data.** |
| **India-specific OR** | **2.35–5.33** (meta-analytic: Seshadri 2026 OR 2.35; Vishwakarma 2019 OR 5.33) |
| **In other tools** | Gail ✓ (1st-degree only) · IBIS ✓ (full pedigree) · BOADICEA ✓ (full pedigree) · BRISK ✓ (1st-degree) |
| **Adaptive trigger** | If **yes** → Tier 2 deep-dive: which relative, age at diagnosis, bilateral, ovarian cancer, paternal lineage, male breast cancer (see 2.1). If **don't know** → note as missing data, do not assume negative. |

---

### 1.3 Prior Breast Biopsy or Benign Breast Disease

| Attribute | Details |
|---|---|
| **Question** | "Have you ever had a breast biopsy, or been told you have a breast lump or benign breast condition?" |
| **Data type** | Yes / No |
| **Why it matters** | Strongest single-factor OR in BRISK model (+1.420 coefficient). History of benign breast disease is a potent risk marker. |
| **India-specific OR** | **4.28** (meta-analytic: Seshadri 2026); **10.4** (JIPMER: Balasubramaniam 2013) |
| **In other tools** | Gail ✓ (biopsy count + atypia) · IBIS ✓ (ADH/ALH/LCIS) · BOADICEA ✓ · BRISK ✓ |
| **Adaptive trigger** | If **yes** → Tier 2: number of biopsies, atypical hyperplasia (if known), when (see 2.2). |

---

### 1.4 Parity and Age at First Childbirth

| Attribute | Details |
|---|---|
| **Questions** | "How many children have you given birth to?" → "At what age did you have your first child?" |
| **Data type** | Parity: 0 / 1 / 2 / 3+ · Age at first birth: <20 / 20–24 / 25–29 / ≥30 |
| **Why it matters** | Nulliparity and late first birth are consistent risk factors globally and in India. Indian women traditionally have earlier first births (protective) but this is changing rapidly in urban areas. |
| **India-specific OR** | Nulliparity: **1.58** (Vishwakarma 2019); First birth >25: **1.57** (Vishwakarma 2019); First birth ≥30: **5.4** (Rao 1994, Tata Memorial). BRISK: +0.811 for nullipara/25–29, +1.035 for ≥30. |
| **In other tools** | Gail ✓ · IBIS ✓ · BOADICEA ✓ · BRISK ✓ |
| **Adaptive trigger** | Nullipara → skip 1.5 (breastfeeding), ask about fertility treatment in Tier 2 (2.4). Age at first birth ≥30 → elevated risk signal. Parity 3+ → protective factor (OR 0.50–0.60). |

---

### 1.5 Breastfeeding History

| Attribute | Details |
|---|---|
| **Question (if has children — skip if 1.4 = nullipara)** | "Did you breastfeed your children? For roughly how long in total across all children?" |
| **Data type** | Never / <6 months / 6–12 months / 12–24 months / >24 months |
| **Why it matters** | **Strongest India-specific protective factor.** Never breastfeeding has OR 3.49–3.69 in Indian meta-analyses. BRISK gives -0.892 coefficient (nearly halves odds) for >24 months. Gail and IBIS completely ignore this factor. |
| **India-specific OR** | Never breastfed: **3.69** (Vishwakarma 2019); <6 months: **4.12** (Seshadri 2026). Each 12 months of breastfeeding reduces risk by **4.3%** (Collaborative Group 2002). |
| **In other tools** | Gail ✗ · IBIS ✗ · BOADICEA ✗ · BRISK ✓ |
| **Adaptive trigger** | If **never breastfed** despite having children → strong risk signal, flag. |

---

### 1.6 Waist Circumference (Central Obesity)

| Attribute | Details |
|---|---|
| **Question (voice/phone)** | "Would you describe your belly area as flat, slightly rounded, or noticeably rounded?" |
| **Question (chat/WhatsApp — enhanced)** | "If you have a tape measure handy, could you measure around your waist at the level of your belly button, standing relaxed? If not, would you describe your belly area as flat, slightly rounded, or noticeably rounded?" |
| **Data type** | cm (numeric) if measured, OR categorical proxy: Flat / Slightly rounded / Noticeably rounded → maps to <80cm / 80–88cm / >88cm |
| **Why it matters** | **BMI is misleading in Indian women.** The "thin-fat Indian" phenotype means Indian women carry visceral fat at lower BMI thresholds. WHR/waist circumference is the correct anthropometric measure. |
| **India-specific OR** | WHR >0.85: **2.74** (Seshadri 2026 meta-analysis); WHR ≥0.95: **3.4–4.3** (Nagrani 2016, Tata Memorial). BMI >25 was **NOT significant** in the same meta-analysis. |
| **In other tools** | Gail ✗ · IBIS ✓ (BMI only, v8) · BOADICEA ✓ (BMI) · BRISK ✗ |
| **Adaptive trigger** | If >80cm or "noticeably rounded" → flag central obesity risk. Also collect height + weight for BMI as secondary measure in Tier 3 (3.8). |

---

### 1.7 Physical Activity Level

| Attribute | Details |
|---|---|
| **Question** | "How would you describe your daily physical activity? Mostly sitting, some walking and housework, or regular exercise/physical labor?" |
| **Data type** | Sedentary / Light (housework, some walking) / Moderate (regular walking, active housework) / Vigorous (exercise, manual labor) |
| **Why it matters** | Sedentary lifestyle is a strong, independent, and modifiable risk factor in Indian data. Rural Indian women have higher occupational activity (protective). |
| **India-specific OR** | Sedentary: **4.6** (Sofi 2018, AIIMS); Low vigorous activity: **2.7** (Jacob 2025, Kerala); Low physical activity: **3.33** (Sankar 2023). Household activity 5–6 h/day: OR **0.48–0.49** — protective (Mathew 2009). |
| **In other tools** | Gail ✗ · IBIS ✗ · BOADICEA ✗ · BRISK ✗ |
| **Adaptive trigger** | If sedentary → strong risk signal, captured. No further drill-down needed. |

---

### 1.8 Fried Food and Dietary Fat

| Attribute | Details |
|---|---|
| **Question** | "How often do you eat fried or deep-fried foods — daily, a few times a week, or rarely?" |
| **Data type** | Daily / Few times/week / Once/week / Rarely/never |
| **Why it matters** | High-fat/fried food is one of the strongest modifiable risk factors in Indian data — meta-analytic OR 4.20, stronger than many Tier 1 factors in other tools. |
| **India-specific OR** | Fried food: **3.9** (Jacob 2025); High-fat diet: **4.20** (Seshadri 2026 meta-analysis); Fat >30g/day: **2.4** (Balasubramaniam 2013). |
| **In other tools** | Gail ✗ · IBIS ✗ · BOADICEA ✗ · BRISK ✗. **No existing tool captures dietary risk.** |
| **Note** | Vegetarian/non-vegetarian classification is **NOT independently predictive** (lifelong vegetarianism OR 1.09, NS — Gathani 2017, 2,101 cases across 8 Indian cancer centres). The real signal is fried food frequency, not meat/no-meat. Non-veg diet shows OR 1.62 in meta-analysis (Seshadri 2026) but this likely confounds with cooking method and fat intake rather than being an independent effect. |

---

### 1.9 Menstrual / Menopausal Status

| Attribute | Details |
|---|---|
| **Questions** | "Are you still having regular periods?" → If no: "At what age did your periods stop?" |
| **Data type** | Premenopausal / Perimenopausal / Postmenopausal · Age at menopause (if applicable) |
| **Why it matters** | Menopause timing reflects cumulative estrogen exposure. Late menopause (>50) is a risk factor; Indian women reach menopause earlier on average (46–47 vs 51 in West), which is protective. |
| **India-specific OR** | Late menopause (>50): **2.88** (Vishwakarma 2019); **1.92** (Seshadri 2026). Postmenopausal status: **1.35** (Vishwakarma 2019). |
| **In other tools** | Gail ✗ · IBIS ✓ · BOADICEA ✓ · BRISK ✗ (menstrual regularity only) |
| **Adaptive trigger** | If postmenopausal → Tier 2: type of menopause (natural/surgical), HRT use (2.3). If premenopausal → ask menstrual regularity (1.10). |

---

### 1.10 Menstrual Cycle Regularity

| Attribute | Details |
|---|---|
| **Question (if premenopausal from 1.9)** | "Are your menstrual cycles regular?" |
| **Data type** | Yes / No |
| **Why it matters** | Captures hormonal milieu. Irregular cycles may indicate PCOS or other endocrine conditions with breast cancer associations. Included in BRISK but absent from all Western tools. |
| **India-specific OR** | BRISK coefficient: +0.453 for irregular cycles. |
| **In other tools** | Gail ✗ · IBIS ✗ · BOADICEA ✗ · BRISK ✓ |
| **Adaptive trigger** | If irregular → Tier 3: PCOS diagnosis (3.6b). |

---

### 1.11 Age at Menarche

| Attribute | Details |
|---|---|
| **Question** | "At what age did you first get your period?" |
| **Data type** | Integer (years) or categories: <12 / 12–13 / ≥14 |
| **Why it matters** | Earlier menarche = longer cumulative estrogen exposure = higher risk. Consistent across Indian and Western data. |
| **India-specific OR** | <13 years: **1.83** (Vishwakarma 2019); **1.95** (Seshadri 2026). BRISK coefficient: -0.082 (later menarche is protective). |
| **In other tools** | Gail ✓ · IBIS ✓ · BOADICEA ✓ · BRISK ✓ |
| **Adaptive trigger** | None — standalone factor, no branching needed. |

---

### 1.12 Current Breast Symptoms (Safety Check)

| Attribute | Details |
|---|---|
| **Questions** | "Have you noticed any changes in your breasts recently — a lump, thickening, pain, or change in shape?" → "Have you noticed any nipple discharge or skin changes on your breast?" |
| **Data type** | Yes / No (for each) |
| **Why it matters** | **Safety-critical.** Not a risk factor per se, but essential for immediate clinical referral if symptoms present. Takes 15 seconds and should never be deferred. |
| **In other tools** | Gail ✗ · IBIS ✗ · BOADICEA ✗ · BRISK ✗ |
| **Agent rule** | If **any symptom reported** → immediately recommend clinical breast examination. Do NOT wait for risk score completion. Flag as **urgent clinical referral** in output. Bloody nipple discharge or peau d'orange requires urgent referral regardless of risk score. |

---

## Tier 2 — Conditional Deep-Dive

**Asked when Tier 1 answers trigger further exploration.** Each sub-section lists its trigger condition. These factors add ~15–20% discriminative power on top of Tier 1.

**Agent rule:** Enter each sub-section ONLY if the specified trigger condition is met. If Tier 1 accumulated risk is already clearly low (all protective answers), the agent MAY abbreviate Tier 2 — but should still offer: "Your answers so far suggest lower risk. Would you like to continue with a few more questions for a more complete picture?"

---

### 2.1 Family History — Extended Pedigree
**Trigger:** 1.2 = Yes or Don't Know

| # | Question | Data type | Why |
|---|---|---|---|
| 2.1a | "Which relative was diagnosed — mother, sister, or daughter?" | Multi-select: mother / sister(s) / daughter(s) | Number of affected 1st-degree relatives matters: ≥2 relatives dramatically increases risk |
| 2.1b | "At what age were they diagnosed?" | Integer or range: <40 / 40–50 / >50 | Younger diagnosis in relatives suggests hereditary component (BRCA) |
| 2.1c | "Did they have cancer in both breasts?" | Yes / No / Don't know | Bilateral breast cancer suggests genetic predisposition |
| 2.1d | "Has anyone in your family — on either your mother's or father's side — had ovarian cancer?" | Yes / No / Don't know | Ovarian cancer in family suggests BRCA mutations (shared pathway) |
| 2.1e | "Has any male relative had breast cancer?" | Yes / No / Don't know | Male breast cancer is a strong BRCA2 indicator |
| 2.1f | "Do you have any second-degree relatives (grandmother, aunt, niece) with breast or ovarian cancer?" | Yes / No / Don't know | Extends pedigree depth — IBIS and BOADICEA use 2nd/3rd degree |
| 2.1g | "Has anyone in your family had any other type of cancer?" | Free text or multi-select | Captures cancer clustering (Li-Fraumeni, Lynch syndrome associations) |

**In other tools:** Gail captures only 1st-degree count. IBIS/BOADICEA capture full pedigree including 2.1a–f. BRISK captures 1st-degree only.

**India-specific note:** Indian founder BRCA1 mutations are regionally distributed — 185delAG in South India, 5382insC in Eastern India. 67% of pathogenic findings in Indian cohorts are in non-BRCA genes (TP53, PALB2, ATM). Family history thresholds for genetic counseling referral should be lower than Western guidelines.

---

### 2.2 Breast Biopsy Details
**Trigger:** 1.3 = Yes

| # | Question | Data type | Why |
|---|---|---|---|
| 2.2a | "How many breast biopsies have you had?" | 1 / 2 / 3+ | Multiple biopsies increase risk multiplicatively |
| 2.2b | "Were you told any of the biopsies showed 'atypical' cells or 'atypical hyperplasia'?" | Yes / No / Don't know | Atypical hyperplasia: OR ~4–5× (Gail, IBIS factor). Rare in Indian data due to low biopsy rates, but very high signal when present. |
| 2.2c | "Were you told you have LCIS (lobular carcinoma in situ)?" | Yes / No / Don't know | LCIS is a strong risk factor (IBIS factor); excluded from Gail model |
| 2.2d | "When was your most recent biopsy?" | Years ago (approximate) | Recent biopsy more clinically relevant |

**In other tools:** Gail ✓ (count + atypia). IBIS ✓ (ADH/ALH/LCIS). BOADICEA ✓. BRISK ✓ (binary only).

---

### 2.3 Hormonal Exposures
**Trigger:** All women (OCP is relevant at any age); postmenopausal women get additional HRT and menopause-type questions

| # | Question | Data type | Trigger | Why |
|---|---|---|---|---|
| 2.3a | "Have you ever taken birth control pills? If yes, for how long?" | Never / <1 year / 1–5 years / >5 years | All women | OCP use: OR **2.01** (Seshadri 2026). Low prevalence in India (3.7%, Khadilkar 2020) but still worth capturing. |
| 2.3b | "Have you taken any hormone replacement therapy (HRT) after menopause?" | Never / Past / Current · Duration | Postmenopausal only | Extremely rare in India (0.5%, Khadilkar 2020). Ask briefly — if yes, it's a meaningful risk signal precisely because it's unusual. |
| 2.3c | "Have you undergone any fertility treatments (IVF, hormone injections)?" | Yes / No | All women | Emerging evidence on ovarian stimulation and breast cancer risk. Rising in urban India. |
| 2.3d | "Was your menopause natural, or due to surgery or medical treatment?" | Natural / Surgical (hysterectomy/oophorectomy) / Medical | Postmenopausal only | Type of menopause affects risk differently. Oophorectomy before 40 is strongly protective. |

**In other tools:** Gail ✗ (no hormonal factors). IBIS ✓ (HRT type/duration, menopause details). BOADICEA ✓ (HRT, OCP). BRISK ✗.

**Note:** Age at menopause is already captured in 1.9 — do not re-ask here.

---

### 2.4 Reproductive History — Extended
**Trigger:** All women (abortion and marriage age have strong ORs relevant regardless of parity)

| # | Question | Data type | Why |
|---|---|---|---|
| 2.4a | "Have you had any miscarriages or abortions?" | 0 / 1 / 2 / 3+ | Previous abortions: OR **2.48** (Seshadri 2026 meta-analytic); OR **4.0** (Sofi 2018, AIIMS). Controversial globally but consistently significant in Indian data. |
| 2.4b | "At what age did you get married?" | Integer (years) or Never married | Late marriage (>21): OR **2.66** (Seshadri 2026); Unmarried: OR **1.96** (Seshadri 2026). Proxy for delayed reproduction. |
| 2.4c | **(If nulliparous from 1.4)** "Have you tried fertility treatments?" | Yes / No | Links to hormonal exposure (2.3c) and captures possible PCOS/endocrine context |

**In other tools:** Gail ✗ · IBIS ✗ (no abortion/marriage data) · BRISK ✗.

**India-specific note:** Marriage age is culturally sensitive. Frame as health context, not judgment. The agent should preface: "These questions help us understand your health timeline — there are no right or wrong answers."

---

### 2.5 Diet — Extended
**Trigger:** Always asked (complements 1.8)

| # | Question | Data type | Why |
|---|---|---|---|
| 2.5a | "How would you describe your overall diet — mostly home-cooked, a mix, or mostly outside/restaurant food?" | Home-cooked / Mix / Mostly outside | Proxy for fat/oil intake and processed food exposure |

**In other tools:** All tools ✗.

---

### 2.6 Screening History
**Trigger:** Always asked (determines downstream recommendation urgency)

| # | Question | Data type | Why |
|---|---|---|---|
| 2.6a | "When was your last breast check by a doctor (clinical breast examination)?" | Never / <1 year / 1–3 years / >3 years | Determines recommendation urgency |
| 2.6b | "Have you ever had a mammogram?" | Yes / No | <5% of Indian women have. If yes → Tier 4 breast density question (4.2). Also action-oriented for recommendations. |

**In other tools:** BRISK collects screening history (not scored). Others ✗.

---

## Tier 3 — Contextual Enrichment

**Factors that add discriminative power but have lower individual ORs, emerging evidence, or serve as proxy variables.** The agent asks these when: (a) Tier 1+2 risk is borderline (neither clearly low nor clearly high), or (b) the woman has time and is willing to continue.

**Agent rule:** Offer as optional: "We have a few more questions that can help make your risk picture more complete. Would you like to continue?"

---

### 3.1 Location and Urbanization

| Attribute | Details |
|---|---|
| **Question** | "Where do you currently live — a large city, a smaller town, or a rural area?" → "Where did you grow up for the first 20 years of your life?" |
| **Data type** | Metro / Urban / Semi-urban / Rural (current + childhood) |
| **India-specific OR** | Urban residence: **1.22** (Vishwakarma 2019). Rural first 20 years: OR **0.65** — protective (Nagrani 2014). Incidence: Delhi 35–40 vs rural 10–15 per 100,000. |
| **In other tools** | All tools ✗ — no existing tool captures this |
| **Why for PinkShieldAI** | Serves as proxy for lifestyle transition (diet, activity, breastfeeding pattern changes) AND allows regional baseline calibration |

---

### 3.2 Education / Socioeconomic Status

| Attribute | Details |
|---|---|
| **Question** | "What is your highest level of education?" |
| **Data type** | No formal / Primary / Secondary / Graduate / Postgraduate |
| **India-specific evidence** | Higher SES correlates with higher breast cancer risk in India (later marriage, fewer children, less breastfeeding, more processed food, less physical activity). Yeole & Kurkure 2003: incidence increased with education level. |
| **In other tools** | All tools ✗ |
| **Why for PinkShieldAI** | SES proxy. Also useful for adapting communication complexity (agent adjusts language level). |

---

### 3.3 Sleep Quality and Regularity

| Attribute | Details |
|---|---|
| **Questions** | "How would you rate your sleep — good, fair, or poor?" → "Do you sleep and wake at regular times?" |
| **Data type** | Sleep quality: Good / Fair / Poor · Regularity: Regular / Somewhat irregular / Very irregular |
| **India-specific OR** | Poor sleep: **11.29** (Vishwakarma 2022, RGCI Delhi); Irregular sleep: **34.11** (same study). Striking ORs but from a single case-control study (187 cases) — needs replication. |
| **In other tools** | All tools ✗ |
| **Evidence strength** | ⚠️ Single study, high ORs may reflect confounding or small sample. Include for data capture but weight cautiously in model until replicated. |

---

### 3.4 Perceived Stress Level

| Attribute | Details |
|---|---|
| **Question** | "Over the past year, how would you describe your stress level — low, moderate, or high?" |
| **Data type** | Low / Moderate / High / Severe |
| **India-specific OR** | Severe stress: **6.74** (Vishwakarma 2022, RGCI Delhi). Same caveats as 3.3. |
| **In other tools** | All tools ✗ |
| **Evidence strength** | ⚠️ Single study. Likely correlated with sleep (3.3). Capture for research but weight cautiously. |

---

### 3.5 Tobacco and Smoke Exposure

| Attribute | Details |
|---|---|
| **Questions** | "Do you use any form of tobacco — cigarettes, beedis, or chewing tobacco/gutka/paan?" → "Does anyone in your household smoke regularly?" |
| **Data type** | Active: Never / Smokeless (gutka, paan, betel) / Smoking / Both · Passive: Yes / No |
| **India-specific OR** | Active tobacco use: **1.67** (Seshadri 2026 meta-analytic). Passive smoke exposure found in **12.8%** of Indian BC patients (Khadilkar 2020). |
| **In other tools** | All tools ✗ |
| **India-specific note** | Smokeless tobacco (betel quid, gutka) is the dominant form in India; relationship to breast cancer less established than for oral cancers but worth capturing. Passive smoking is under-studied in Indian breast cancer but has established biological plausibility. |

---

### 3.6 Medical History — Metabolic and Endocrine

| # | Question | Data type | Why | OR |
|---|---|---|---|---|
| 3.6a | "Have you been diagnosed with diabetes?" | Yes (Type 1/2) / No | Metabolic syndrome: OR **3.037** (Wani 2017). Diabetes is a component. | ~1.2–1.5 (global meta-analyses) |
| 3.6b | "Have you been diagnosed with PCOS (polycystic ovary syndrome)?" | Yes / No | Links to irregular cycles (1.10), hormonal milieu, insulin resistance. Emerging evidence. | Emerging |
| 3.6c | "Do you have any thyroid condition?" | Yes (hypo/hyper) / No | Emerging association; hypothyroidism may alter estrogen metabolism. | Emerging |
| 3.6d | "Have you ever been told you have low vitamin D?" | Yes / No / Don't know | Vitamin D deficiency (<20 ng/ml): OR **2.4** (Sofi 2018, AIIMS). Prevalent in India despite sun exposure. | **2.4** |

**In other tools:** All tools ✗ (none capture metabolic/endocrine comorbidities).

---

### 3.7 Alcohol Use

| Attribute | Details |
|---|---|
| **Question** | "Do you drink alcohol? If yes, how often?" |
| **Data type** | Never / Occasionally / Weekly / Daily |
| **India-specific evidence** | Only **1.2%** of Indian women consume alcohol (NFHS-4). No Indian case-control study found alcohol significant. Collaborative Group 2002: "negligible effect" in developing countries (avg 0.4 g/day). |
| **In other tools** | Gail ✗ · IBIS ✗ · BOADICEA ✗ · BRISK ✗ (Rosner-Colditz includes alcohol) |
| **Agent rule** | Ask briefly. If "never" (expected in ~99% of cases), move on instantly. Only drill into quantity/frequency if "yes." |

---

### 3.8 Height and Weight (BMI — Secondary Measure)

| Attribute | Details |
|---|---|
| **Question** | "What is your height and weight?" |
| **Data type** | Height (cm or feet/inches) + Weight (kg or pounds) → compute BMI |
| **India-specific evidence** | BMI >25 was **NOT significant** in Seshadri 2026 meta-analysis. WHR is the correct measure (captured in 1.6). BMI collected as secondary measure and for research/comparison with Western models. Use Asian WHO cutoffs: overweight ≥23, obese ≥25. |
| **In other tools** | Gail ✗ · IBIS ✓ (v8) · BOADICEA ✓ · BRISK ✗ |
| **Agent rule** | Collect for completeness. Do NOT weight heavily in risk model — waist circumference (1.6) takes priority. |

---

### 3.9 Chest Radiation History

| Attribute | Details |
|---|---|
| **Question** | "Have you ever received radiation treatment to your chest area — for example, for lymphoma or another condition?" |
| **Data type** | Yes / No |
| **Evidence** | Chest radiation before age 30 is a strong breast cancer risk factor (OR >4 globally). Rare but very high signal. |
| **In other tools** | Gail ✗ · IBIS ✓ · BOADICEA ✓ · BRISK ✗ |
| **Agent rule** | Brief question. If yes → major risk flag regardless of other factors. |

---

### 3.10 Consanguinity

| Attribute | Details |
|---|---|
| **Question** | "Are your parents related to each other — for example, are they cousins?" |
| **Data type** | Yes / No / Don't know |
| **Why it matters** | Consanguinity is prevalent in certain Indian communities (parts of South India, some Muslim communities); may concentrate recessive alleles including cancer predisposition genes. |
| **Evidence** | Limited direct evidence for breast cancer specifically, but relevant for genetic risk architecture. |
| **In other tools** | All tools ✗ |
| **Agent rule** | Ask sensitively. If yes → note in genetic risk context. |

---

### 3.11 Breast Self-Examination Practice

| Attribute | Details |
|---|---|
| **Question** | "Do you examine your breasts regularly for any changes?" |
| **Data type** | Yes (monthly) / Sometimes / Never |
| **Why it matters** | Not a risk factor, but relevant for: (a) downstream recommendation (encourage if not doing), (b) health awareness level proxy, (c) likelihood of early detection. |
| **In other tools** | BRISK collects this (not scored) |

---

## Tier 4 — Future / Research Factors

**Factors worth capturing for model refinement but not currently actionable in the risk score.** The agent asks these ONLY in research mode, extended assessments, or when the woman volunteers information.

**Agent rule:** Do NOT ask unless: (a) the assessment is in "research" or "comprehensive" mode, (b) the woman has already expressed willingness for a longer conversation, or (c) she volunteers the information.

---

### 4.1 Genetic Testing Results (If Available)

| # | Question | Data type | Why |
|---|---|---|---|
| 4.1a | "Have you ever had genetic testing for cancer risk? If so, what were the results?" | No test / Tested negative / BRCA1+ / BRCA2+ / Other gene / VUS / Don't know | BRCA1/2 prevalence in Indian BC patients: ~8% (unselected) to 52% (early-onset). 67% of pathogenic findings are in non-BRCA genes. |
| 4.1b | "Has any family member had genetic testing?" | Same options | Extends family genetic information |

**Agent rule:** Most Indian women will never have had genetic testing. Ask only if family history is strong (2.1) or woman mentions it. Do NOT recommend genetic testing without clinical context.

---

### 4.2 Breast Density (If Mammogram Done)

| # | Question | Data type | Why |
|---|---|---|---|
| 4.2a | **(If 2.6b = Yes)** "Were you told your breasts are 'dense'?" | Yes / No / Don't know | Breast density is the strongest independent risk factor in Western models (IBIS, BCSC). If available, it dramatically improves discrimination (AUC 0.65→0.76 in IBIS v7+). |

**In other tools:** Gail ✗ · IBIS ✓ (v7+) · BOADICEA ✓ · BCSC ✓ · BRISK ✗.

---

### 4.3 Soy / Isoflavone Intake

| Attribute | Details |
|---|---|
| **Question** | "How often do you eat soy products — tofu, soy milk, or soy chunks?" |
| **Data type** | Daily / Weekly / Rarely / Never |
| **Evidence** | Asian women soy intake: OR **0.59** (Chen 2014 meta-analysis). South Asians highest quartile isoflavone: OR **0.58** (dos Santos Silva 2004). Protective factor, but Indian soy consumption is lower than East Asian. Primary Indian phytoestrogen source is pulses/dals, not soy. |

---

### 4.4 Turmeric / Curcumin Intake

| Attribute | Details |
|---|---|
| **Question** | "Do you regularly consume turmeric in your food or as a supplement?" |
| **Data type** | Daily in cooking / Supplement / Rarely / Never |
| **Evidence** | No epidemiological study directly measuring turmeric intake and breast cancer risk exists. Average Indian intake: 60–100 mg curcumin/day. Evidence is mechanistic only (NF-kB, COX-2 modulation). **Research gap** — capture for future analysis but do NOT score. |

---

### 4.5 Night Shift Work

| Attribute | Details |
|---|---|
| **Question** | "Do you regularly work night shifts?" |
| **Data type** | Yes (frequency) / No |
| **Evidence** | IARC classifies night shift work as "probably carcinogenic" (Group 2A). Limited India-specific data. Relevant for urban working women. |

---

### 4.6 Environmental Exposures

| # | Question | Data type | Why |
|---|---|---|---|
| 4.6a | "Do you live near any industrial area or pesticide-treated agricultural land?" | Yes / No | Environmental estrogens (endocrine disruptors) have theoretical breast cancer links. No India-specific quantitative data. |
| 4.6b | "What type of cooking fuel do you primarily use?" | LPG / Kerosene / Wood/cow dung / Electric/induction | Indoor air pollution from biomass cooking is prevalent in rural India. Possible but unquantified breast cancer link. |

---

### 4.7 Pregnancy and Hormonal Details — Extended

| # | Question | Data type | Why |
|---|---|---|---|
| 4.7a | "Did you have any complications during pregnancy such as gestational diabetes or preeclampsia?" | Yes / No | Gestational diabetes may indicate insulin resistance pathway. Emerging evidence. |
| 4.7b | "Did you take DES (diethylstilbestrol) during pregnancy, or was your mother given DES?" | Yes / No / Don't know | DES exposure increases risk. Historical — less relevant in India but worth capturing. |

---

## Adaptive Flow — Agent Decision Tree

```
START
│
├─ Ask Tier 1 (all 12 questions, ~4 min)
│  ├─ 1.1  Age
│  ├─ 1.2  Family history (1st degree) ──── if YES ──→ 2.1 Extended pedigree
│  ├─ 1.3  Prior biopsy/benign disease ─── if YES ──→ 2.2 Biopsy details
│  ├─ 1.4  Parity / age at first birth ── if nullipara → skip 1.5
│  ├─ 1.5  Breastfeeding ──────────────── (skip if nullipara from 1.4)
│  ├─ 1.6  Waist circumference ────────── (voice: self-description; chat: tape measure)
│  ├─ 1.7  Physical activity
│  ├─ 1.8  Fried food frequency
│  ├─ 1.9  Menstrual/menopausal status ── if postmeno → 2.3b/d (HRT, menopause type)
│  ├─ 1.10 Menstrual regularity ──────── (skip if postmenopausal)
│  ├─ 1.11 Age at menarche
│  └─ 1.12 Current breast symptoms ───── if ANY symptom → IMMEDIATE REFERRAL
│
├─ SYMPTOM CHECK (from 1.12)
│  └─ If ANY breast symptom ──→ IMMEDIATE REFERRAL (override everything)
│
├─ Compute Tier 1 risk estimate
│  ├─ If CLEARLY LOW (all protective) ──→ Offer Tier 2 as optional
│  ├─ If BORDERLINE ────────────────────→ Ask full Tier 2 + offer Tier 3
│  └─ If ELEVATED ──────────────────────→ Ask full Tier 2 + Tier 3
│
├─ Ask Tier 2 (conditional, ~4 min)
│  ├─ 2.1  Family history deep-dive (if triggered)
│  ├─ 2.2  Biopsy details (if triggered)
│  ├─ 2.3  Hormonal exposures (OCP for all; HRT/menopause-type if postmeno)
│  ├─ 2.4  Reproductive extended (all women: abortions, marriage age)
│  ├─ 2.5  Diet extended (home-cooked vs outside)
│  └─ 2.6  Screening history (always — for recommendations)
│
├─ Ask Tier 3 (if borderline or elevated, ~3 min)
│  ├─ 3.1   Location / urbanization
│  ├─ 3.2   Education / SES
│  ├─ 3.3   Sleep quality
│  ├─ 3.4   Stress level
│  ├─ 3.5   Tobacco + passive smoke
│  ├─ 3.6   Medical history (diabetes, PCOS, thyroid, vitamin D)
│  ├─ 3.7   Alcohol (brief)
│  ├─ 3.8   Height/weight (BMI secondary)
│  ├─ 3.9   Chest radiation
│  ├─ 3.10  Consanguinity
│  └─ 3.11  BSE practice
│
├─ Ask Tier 4 (research mode only, ~3 min)
│  ├─ 4.1–4.7 (all optional)
│
└─ COMPUTE FINAL RISK SCORE → Output 5-tier risk level
```

### Urgent Referral Overrides

Regardless of computed risk score, the agent MUST recommend immediate clinical evaluation if:
- Any current breast symptom reported (1.12)
- Known BRCA1/BRCA2 carrier (4.1a)
- ≥2 first-degree relatives with breast cancer, especially if diagnosed young (<50)
- Prior atypical hyperplasia or LCIS (2.2b or 2.2c)
- Prior chest radiation before age 30 (3.9)

---

## Factor × Tool Coverage Matrix

| # | Factor | India OR | Gail | IBIS | BOADICEA | BRISK | PinkShieldAI |
|---|---|---|---|---|---|---|---|
| **Tier 1** | | | | | | | |
| 1.1 | Age | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1.2 | Family history (1st degree) | 2.35–5.33 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1.3 | Prior biopsy / benign disease | 4.28–10.4 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1.4 | Parity / age at first birth | 1.57–5.4 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1.5 | Breastfeeding | 3.69–4.12 | ✗ | ✗ | ✗ | ✓ | ✓ |
| 1.6 | Waist circumference (WHR) | 2.74–4.10 | ✗ | ✗ | ✗ | ✗ | ✓ |
| 1.7 | Physical activity | 2.7–4.6 | ✗ | ✗ | ✗ | ✗ | ✓ |
| 1.8 | Fried food / dietary fat | 3.9–4.20 | ✗ | ✗ | ✗ | ✗ | ✓ |
| 1.9 | Menopausal status / age | 1.35–2.88 | ✗ | ✓ | ✓ | ✗ | ✓ |
| 1.10 | Menstrual regularity | BRISK +0.453 | ✗ | ✗ | ✗ | ✓ | ✓ |
| 1.11 | Age at menarche | 1.83–1.95 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1.12 | Current breast symptoms | — | ✗ | ✗ | ✗ | ✗ | ✓ |
| **Tier 2** | | | | | | | |
| 2.1 | Extended family pedigree | — | ✗ | ✓ | ✓ | ✗ | ✓ |
| 2.2 | Biopsy details / atypia | ~4–5 | ✓ | ✓ | ✓ | ✗ | ✓ |
| 2.3 | OCP / HRT / fertility Rx | 2.01 | ✗ | ✓ | ✓ | ✗ | ✓ |
| 2.4 | Abortions / marriage age | 2.48–2.66 | ✗ | ✗ | ✗ | ✗ | ✓ |
| 2.5 | Diet extended (cooking source) | proxy | ✗ | ✗ | ✗ | ✗ | ✓ |
| 2.6 | Screening history | — | ✗ | ✗ | ✗ | ✗ | ✓ |
| **Tier 3** | | | | | | | |
| 3.1 | Location / urbanization | 0.65–1.22 | ✗ | ✗ | ✗ | ✗ | ✓ |
| 3.2 | Education / SES | proxy | ✗ | ✗ | ✗ | ✗ | ✓ |
| 3.3 | Sleep quality | 11.29* | ✗ | ✗ | ✗ | ✗ | ✓ |
| 3.4 | Stress level | 6.74* | ✗ | ✗ | ✗ | ✗ | ✓ |
| 3.5 | Tobacco + passive smoke | 1.67 | ✗ | ✗ | ✗ | ✗ | ✓ |
| 3.6 | Diabetes / PCOS / thyroid / vit D | 2.4–3.0 | ✗ | ✗ | ✗ | ✗ | ✓ |
| 3.7 | Alcohol use | negligible | ✗ | ✗ | ✗ | ✗ | ✓ |
| 3.8 | BMI (secondary) | 1.19 (NS) | ✗ | ✓ | ✓ | ✗ | ✓ |
| 3.9 | Chest radiation | >4 | ✗ | ✓ | ✓ | ✗ | ✓ |
| 3.10 | Consanguinity | unknown | ✗ | ✗ | ✗ | ✗ | ✓ |
| 3.11 | BSE practice | — | ✗ | ✗ | ✗ | ✗ | ✓ |
| **Tier 4** | | | | | | | |
| 4.1 | Genetic test results | high | ✗ | ✓ | ✓ | ✗ | ✓ |
| 4.2 | Breast density | high | ✗ | ✓ | ✓ | ✗ | ✓ |
| 4.3 | Soy / isoflavone intake | 0.58–0.59 | ✗ | ✗ | ✗ | ✗ | ✓ |
| 4.4 | Turmeric / curcumin | unknown | ✗ | ✗ | ✗ | ✗ | ✓ |
| 4.5 | Night shift work | IARC 2A | ✗ | ✗ | ✗ | ✗ | ✓ |
| 4.6 | Environmental exposures | unknown | ✗ | ✗ | ✗ | ✗ | ✓ |
| 4.7 | Extended pregnancy details | emerging | ✗ | ✗ | ✗ | ✗ | ✓ |

*Single study, needs replication

**Summary:** PinkShieldAI captures **36 factors** across 4 tiers — vs. Gail (7), IBIS (15–20), BOADICEA (20+), BRISK (8 scored). Critically, PinkShieldAI is the **only tool** that captures waist circumference, physical activity, dietary fat, sleep/stress, urbanization, passive smoke exposure, and the full suite of India-specific factors — while requiring zero clinical infrastructure.

---

## Evidence Strength Summary — All Factors Ranked by India-Specific OR

### Meta-Analytic Evidence (Strongest — pooled across multiple Indian studies)

| Rank | Factor | India OR | Source | # Studies |
|---|---|---|---|---|
| 1 | Family history of BC | 2.35–5.33 | Seshadri 2026 / Vishwakarma 2019 | 19–24 |
| 2 | Past benign breast disease | 4.28 | Seshadri 2026 | 19 |
| 3 | High-fat diet | 4.20 | Seshadri 2026 | 19 |
| 4 | Breastfeeding <6 months | 4.12 | Seshadri 2026 | 19 |
| 5 | Never breastfed | 3.69 | Vishwakarma 2019 | 24 |
| 6 | Late menopause (>50) | 2.88 | Vishwakarma 2019 | 24 |
| 7 | Central obesity (WHR >0.85) | 2.74 | Seshadri 2026 | 19 |
| 8 | Late marriage (>21) | 2.66 | Seshadri 2026 | 19 |
| 9 | Previous abortions | 2.48 | Seshadri 2026 | 19 |
| 10 | OCP use | 2.01 | Seshadri 2026 | 19 |
| 11 | Unmarried status | 1.96 | Seshadri 2026 | 19 |
| 12 | Early menarche (<13) | 1.83–1.95 | Vishwakarma / Seshadri | 19–24 |
| 13 | Late menopause | 1.92 | Seshadri 2026 | 19 |
| 14 | Tobacco use | 1.67 | Seshadri 2026 | 19 |
| 15† | Non-vegetarian diet | 1.62 | Seshadri 2026 | 19 |
| 16 | Nulliparity | 1.58 | Vishwakarma 2019 | 24 |
| 17 | Age at first pregnancy >25 | 1.57 | Vishwakarma 2019 | 24 |
| 18 | Low parity | 1.52 | Seshadri 2026 | 19 |
| 19 | Postmenopausal status | 1.35 | Vishwakarma 2019 | 24 |
| 20 | Urban residence | 1.22 | Vishwakarma 2019 | 24 |
| 21 | Obesity (BMI >25) | 1.19 (NS) | Vishwakarma 2019 | 24 |

†**Footnote on non-vegetarian diet (rank 15):** This meta-analytic OR of 1.62 likely confounds with cooking method and fat content rather than being an independent effect of meat consumption. Lifelong vegetarianism showed OR 1.09 (NS) in a large multi-centre study (Gathani 2017, 2,101 cases across 8 Indian cancer centres). The actionable signal is **fried food frequency** (captured in 1.8), not vegetarian/non-vegetarian classification. We capture this OR through the dietary fat question, not through a veg/non-veg question.

### Individual Study Evidence (Strong but needs replication)

| Rank | Factor | India OR | Source | Study type |
|---|---|---|---|---|
| 1 | Irregular sleep | 34.11 | Vishwakarma 2022 (RGCI Delhi) | Case-control, n=374 |
| 2 | Poor sleep | 11.29 | Vishwakarma 2022 (RGCI Delhi) | Case-control, n=374 |
| 3 | Benign breast lesion history | 10.4 | Balasubramaniam 2013 (JIPMER) | Case-control, n=304 |
| 4 | Severe stress | 6.74 | Vishwakarma 2022 (RGCI Delhi) | Case-control, n=374 |
| 5 | Late first pregnancy (≥30) | 5.4 | Rao 1994 (Tata Memorial) | Case-control, n=1400 |
| 6 | Sedentary lifestyle | 4.6 | Sofi 2018 (AIIMS) | Case-control, n=400 |
| 7 | WHR ≥0.95 (premenopausal) | 4.3 | Nagrani 2016 (Tata Memorial) | Case-control, n=3137 |
| 8 | WHR ≥0.95 (urban) | 4.10 | Nagrani 2016 (Tata Memorial) | Case-control, n=3152 |
| 9 | Number of abortions | 4.0 | Sofi 2018 (AIIMS) | Case-control, n=400 |
| 10 | Frequent fried food | 3.9 | Jacob 2025 (Kerala) | Case-control, n=6086 |
| 11 | Calcium <10.5 mg/dl | 3.7 | Sofi 2018 (AIIMS) | Case-control, n=400 |
| 12 | No breastfeeding | 3.49 | Lodha 2011 (Bhopal) | Case-control |
| 13 | WHR ≥0.95 (postmenopausal) | 3.4 | Nagrani 2016 (Tata Memorial) | Case-control, n=3137 |
| 14 | Low physical activity | 3.33 | Sankar 2023 (PSG Coimbatore) | Case-control, n=280 |
| 15 | Metabolic syndrome | 3.04 | Wani 2017 | Case-control, n=100 |
| 16 | WHR ≥0.95 (rural) | 3.01 | Nagrani 2016 (Tata Memorial) | Case-control, n=3152 |
| 17 | Non-veg diet (Udupi) | 2.80 | Kamath 2013 | Case-control |
| 18 | Low vigorous activity | 2.7 | Jacob 2025 (Kerala) | Case-control, n=6086 |
| 19 | Vitamin D deficiency | 2.4 | Sofi 2018 (AIIMS) | Case-control, n=400 |
| 20 | Fat >30g/day | 2.4 | Balasubramaniam 2013 (JIPMER) | Case-control, n=304 |
| 21 | OCP use | 2.4 | Sofi 2018 (AIIMS) | Case-control, n=400 |

### Protective Factors (OR < 1)

| Factor | India OR | Source | Captured in |
|---|---|---|---|
| Rural upbringing (first 20 yrs) | **0.65** | Nagrani 2014 (Tata Memorial) | 3.1 |
| Soy isoflavone (high intake, Asian) | **0.59** | Chen 2014 meta-analysis | 4.3 |
| Soy (South Asians, highest quartile) | **0.58** | dos Santos Silva 2004 | 4.3 |
| Breastfeeding ≥6 months | **0.64** | Nagrani 2016 | 1.5 |
| Household activity 5–6 h/day | **0.48–0.49** | Mathew 2009 (Trivandrum/Chennai) | 1.7 |
| 3+ pregnancies | **0.50–0.60** | Rao 1994 (Tata Memorial) | 1.4 (derived from parity) |

### Factors With Negligible or No India-Specific Evidence

| Factor | Status | Why |
|---|---|---|
| Alcohol | Negligible effect | 1.2% prevalence; 0.4 g/day average; "negligible" per Collaborative Group 2002 |
| HRT | Near-zero prevalence | 0.5% usage (Khadilkar 2020); not a population-level factor |
| BMI (alone) | NOT significant | Seshadri 2026 meta-analysis; WHR is the correct measure |
| Vegetarian/non-veg classification | NOT independently predictive | Lifelong vegetarianism OR 1.09 (NS, Gathani 2017). Fried food frequency is the real signal. |
| Turmeric / curcumin | Research gap | No epidemiological study. Mechanistic evidence only. |
| Breast density | Data unavailable | <5% mammography coverage. Cannot be captured at population scale. |
| PRS / polygenic risk | Not transferable | European PRS AUC drops from 0.63 to 0.55–0.58 in South Asians. No South Asian GWAS. |
