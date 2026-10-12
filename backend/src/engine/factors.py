from dataclasses import dataclass


@dataclass(frozen=True)
class Factor:
    id: str
    tier: int
    label: str
    question: str
    data_type: str  # "integer", "categorical", "boolean", "multi_select", "text"
    ui_type: str = "radio"  # "slider", "radio", "dropdown", "multi_select", "text"
    options: list[str] | None = None
    display_labels: dict[str, str] | None = None
    min_val: int | None = None
    max_val: int | None = None
    coefficient: float | None = None
    skip_if: str | None = None
    triggers_sub: str | None = None
    trigger_condition: str | None = None
    clarification: str | None = None
    is_safety_critical: bool = False


TIER_1_FACTORS: list[Factor] = [
    Factor(
        id="1.1", tier=1, label="age",
        question="How old are you?",
        data_type="integer",
        ui_type="slider",
        min_val=18, max_val=100,
        coefficient=0.027,
        clarification="We ask your age because breast cancer risk changes with age. In India, risk peaks between 45 and 55.",
    ),
    Factor(
        id="1.2", tier=1, label="family_history",
        question="Has anyone in your family ever been diagnosed with cancer?",
        data_type="categorical",
        ui_type="radio",
        options=["first_order", "second_order", "third_order", "none", "prefer_not_to_answer"],
        display_labels={
            "first_order": "First order (mother, sister, daughter)",
            "second_order": "Second order (grandmother, aunt, niece)",
            "third_order": "Third order (any other known relative)",
            "none": "None",
            "prefer_not_to_answer": "Prefer not to answer",
        },
        coefficient=0.810,
        triggers_sub="1.2b",
        trigger_condition="first_order,second_order,third_order",
        clarification="Family history is one of the strongest risk factors. First-degree relatives (mother, sister, daughter) carry the highest risk.",
    ),
    Factor(
        id="1.2b", tier=1, label="family_cancer_types",
        question="What type(s) of cancer were they diagnosed with?",
        data_type="multi_select",
        ui_type="multi_select",
        options=[
            "breast", "ovarian", "uterine_endometrial", "cervical",
            "lung", "colorectal", "brain", "prostate",
            "stomach", "liver", "pancreatic", "thyroid",
            "leukemia_blood", "other",
        ],
        display_labels={
            "breast": "Breast",
            "ovarian": "Ovarian",
            "uterine_endometrial": "Uterine / Endometrial",
            "cervical": "Cervical",
            "lung": "Lung",
            "colorectal": "Colorectal",
            "brain": "Brain",
            "prostate": "Prostate",
            "stomach": "Stomach",
            "liver": "Liver",
            "pancreatic": "Pancreatic",
            "thyroid": "Thyroid",
            "leukemia_blood": "Leukemia / Blood cancer",
            "other": "Other",
        },
        skip_if="1.2=none,1.2=prefer_not_to_answer",
        triggers_sub="1.2c",
        trigger_condition="other",
        clarification="Select all cancer types that apply. Breast cancer in the family is the strongest risk factor, but we record all types for a complete picture.",
    ),
    Factor(
        id="1.2c", tier=1, label="family_cancer_other",
        question="Please specify the other cancer type(s).",
        data_type="text",
        ui_type="text",
        skip_if="1.2=none,1.2=prefer_not_to_answer",
        clarification="Enter the name of any cancer type not listed above.",
    ),
    Factor(
        id="1.3", tier=1, label="prior_biopsy",
        question="Have you ever had a breast biopsy, or been told you have a breast lump or benign breast condition?",
        data_type="boolean",
        ui_type="radio",
        options=["yes", "no"],
        display_labels={"yes": "Yes", "no": "No"},
        coefficient=1.420,
        clarification="A previous breast biopsy or benign breast condition can indicate higher risk. This includes fibroadenomas, cysts, or any lump that was checked.",
    ),
    Factor(
        id="1.4", tier=1, label="parity",
        question="How many children have you given birth to?",
        data_type="categorical",
        ui_type="radio",
        options=["0", "1", "2", "3+"],
        display_labels={"0": "None", "1": "1", "2": "2", "3+": "3 or more"},
        triggers_sub="1.4b",
        trigger_condition="1,2,3+",
        clarification="The number of pregnancies carried to term affects hormonal exposure over your lifetime.",
    ),
    Factor(
        id="1.4b", tier=1, label="age_first_birth",
        question="At what age did you have your first child?",
        data_type="categorical",
        ui_type="radio",
        options=["under_20", "20_24", "25_29", "30_plus"],
        display_labels={
            "under_20": "Under 20",
            "20_24": "20–24",
            "25_29": "25–29",
            "30_plus": "30 or older",
        },
        coefficient=0.811,
        skip_if="1.4=0",
        clarification="Age at first childbirth affects breast cancer risk because pregnancy changes breast tissue. Earlier first births tend to be protective.",
    ),
    Factor(
        id="1.5", tier=1, label="breastfeeding",
        question="Did you breastfeed your children? For roughly how long in total across all children?",
        data_type="categorical",
        ui_type="radio",
        options=["never", "under_6m", "6_12m", "12_24m", "over_24m"],
        display_labels={
            "never": "Never",
            "under_6m": "Less than 6 months",
            "6_12m": "6–12 months",
            "12_24m": "12–24 months",
            "over_24m": "Over 24 months",
        },
        coefficient=-0.892,
        skip_if="1.4=0",
        clarification="Breastfeeding is one of the strongest protective factors against breast cancer, especially in Indian women. Even a few months can make a difference.",
    ),
    Factor(
        id="1.6", tier=1, label="waist_circumference",
        question="What is your waist measurement in centimetres?",
        data_type="categorical",
        ui_type="radio",
        options=["under_80cm", "80_to_88cm", "over_88cm", "dont_know"],
        display_labels={
            "under_80cm": "Under 80 cm (31 inches)",
            "80_to_88cm": "80–88 cm (31–35 inches)",
            "over_88cm": "Over 88 cm (35 inches)",
            "dont_know": "Don't know",
        },
        coefficient=1.008,
        clarification="Waist size is a stronger predictor of breast cancer risk in Indian women than overall weight. A waist over 80 cm (about 31 inches) is considered elevated.",
    ),
    Factor(
        id="1.7", tier=1, label="physical_activity",
        question="How would you describe your daily physical activity?",
        data_type="categorical",
        ui_type="radio",
        options=["sedentary", "light", "moderate", "vigorous"],
        display_labels={
            "sedentary": "Mostly sitting",
            "light": "Some walking and housework",
            "moderate": "Regular moderate exercise",
            "vigorous": "Regular vigorous exercise or physical labour",
        },
        coefficient=1.526,
        clarification="Regular physical activity is protective against breast cancer. This includes housework, walking, exercise, or manual labour.",
    ),
    Factor(
        id="1.8", tier=1, label="fried_food",
        question="How often do you eat fried or deep-fried foods?",
        data_type="categorical",
        ui_type="radio",
        options=["daily", "few_times_week", "once_week", "rarely_never"],
        display_labels={
            "daily": "Daily",
            "few_times_week": "A few times a week",
            "once_week": "About once a week",
            "rarely_never": "Rarely or never",
        },
        coefficient=1.361,
        clarification="Fried and high-fat foods are a significant risk factor in Indian studies. This includes pakoras, samosas, puris, and other deep-fried items.",
    ),
    Factor(
        id="1.9", tier=1, label="menopausal_status",
        question="What is the status of your menstrual periods?",
        data_type="categorical",
        ui_type="radio",
        options=["premenopausal", "perimenopausal", "postmenopausal"],
        display_labels={
            "premenopausal": "Regular periods",
            "perimenopausal": "Irregular / transitioning",
            "postmenopausal": "Periods have stopped",
        },
        triggers_sub="1.9b",
        trigger_condition="postmenopausal",
        clarification="Menopause timing reflects your lifetime oestrogen exposure. Indian women reach menopause slightly earlier on average (46–47 years) compared to Western women.",
    ),
    Factor(
        id="1.9b", tier=1, label="age_at_menopause",
        question="At what age did your periods stop?",
        data_type="integer",
        ui_type="slider",
        min_val=30, max_val=65,
        coefficient=1.058,
        skip_if="1.9=premenopausal,1.9=perimenopausal",
        clarification="Late menopause (after age 50) is associated with higher risk because of longer oestrogen exposure.",
    ),
    Factor(
        id="1.10", tier=1, label="menstrual_regularity",
        question="Are your menstrual cycles regular?",
        data_type="boolean",
        ui_type="radio",
        options=["yes", "no"],
        display_labels={"yes": "Yes", "no": "No"},
        coefficient=0.453,
        skip_if="1.9=postmenopausal",
        clarification="Irregular cycles may indicate hormonal imbalances that can affect breast cancer risk.",
    ),
    Factor(
        id="1.11", tier=1, label="age_at_menarche",
        question="At what age did you first get your period?",
        data_type="integer",
        ui_type="slider",
        min_val=8, max_val=20,
        coefficient=-0.082,
        clarification="Earlier onset of periods means longer lifetime oestrogen exposure, which is associated with slightly higher risk.",
    ),
    Factor(
        id="1.12", tier=1, label="breast_symptoms",
        question="Have you noticed any changes in your breasts recently — a lump, thickening, pain, or change in shape?",
        data_type="boolean",
        ui_type="radio",
        options=["yes", "no"],
        display_labels={"yes": "Yes", "no": "No"},
        is_safety_critical=True,
        triggers_sub="1.12b",
        trigger_condition="yes",
        clarification="This is a safety check. Any breast changes should be evaluated by a doctor regardless of your overall risk level.",
    ),
    Factor(
        id="1.12b", tier=1, label="nipple_discharge",
        question="Have you noticed any nipple discharge or skin changes on your breast?",
        data_type="boolean",
        ui_type="radio",
        options=["yes", "no"],
        display_labels={"yes": "Yes", "no": "No"},
        is_safety_critical=True,
        skip_if="1.12=no",
        clarification="Nipple discharge, especially if bloody, and skin changes like puckering or dimpling are important symptoms that need medical attention.",
    ),
]

FACTORS_BY_ID: dict[str, Factor] = {f.id: f for f in TIER_1_FACTORS}

TIER_1_ORDER: list[str] = [f.id for f in TIER_1_FACTORS]
