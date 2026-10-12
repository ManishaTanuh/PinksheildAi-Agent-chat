# PinkShieldAI — Voicebot Architecture

## Design Philosophy

Adapted from [openai/realtime-voice-component](https://github.com/openai/realtime-voice-component): **the app owns the logic; the voice layer is a constrained caller.** The questionnaire engine decides what to ask. The LLM speaks the questions conversationally and captures answers via narrow, single-action tools. Risk computation, validation, tier transitions, and referral logic stay server-side — never in the voice model's prompt.

This is not a free-form chatbot. It is a **tool-constrained voice agent** that follows a structured assessment flow while sounding natural and empathetic.

---

## System Architecture

```
                          ┌─────────────────────────────────┐
                          │         Channel Layer            │
                          │  WhatsApp · Web · Phone/IVR     │
                          └──────────┬──────────────────────┘
                                     │
                          ┌──────────▼──────────────────────┐
                          │      Transport / Gateway         │
                          │  Gupshup (WhatsApp) · Exotel    │
                          │  (telephony) · WebSocket (web)   │
                          └──────────┬──────────────────────┘
                                     │ audio / text
                          ┌──────────▼──────────────────────┐
                          │        Voice Pipeline            │
                          │                                  │
                          │  ┌───────────┐   ┌───────────┐  │
                          │  │ Sarvam    │   │ Sarvam    │  │
                          │  │ Saaras v3 │   │ Bulbul v3 │  │
                          │  │ STT      │   │ TTS       │  │
                          │  │ 22 langs  │   │ 11 langs  │  │
                          │  └─────┬─────┘   └─────▲─────┘  │
                          │        │               │         │
                          └────────┼───────────────┼─────────┘
                                   │ text          │ text
                          ┌────────▼───────────────┼─────────┐
                          │       Session Manager            │
                          │                                  │
                          │  ┌───────────────────────────┐   │
                          │  │    Claude (Reasoning)      │   │
                          │  │    Tool-constrained mode   │   │
                          │  │    System prompt + tools   │   │
                          │  └─────────┬─────────────────┘   │
                          │            │ tool calls           │
                          │  ┌─────────▼─────────────────┐   │
                          │  │  Questionnaire Engine      │   │
                          │  │  State · Validation ·      │   │
                          │  │  Adaptive flow · Risk      │   │
                          │  └───────────────────────────┘   │
                          │                                  │
                          └──────────────────────────────────┘
                                     │
                          ┌──────────▼──────────────────────┐
                          │       Data Layer                  │
                          │  Session store · Risk model ·     │
                          │  Analytics · Insurer dashboard    │
                          └─────────────────────────────────┘
```

### Why This Stack

| Decision | Rationale |
|---|---|
| **Sarvam AI for STT/TTS** | 22-language ASR, India-tuned, proven at 100M+ conversations (SBI Life), ₹30/hr STT |
| **Claude for reasoning** | Best tool-use discipline, safety alignment for healthcare, long context for session state |
| **Tool-constrained (not free-form)** | Prevents hallucinated medical advice; every action goes through validated tools |
| **Server-side questionnaire engine** | Risk logic, tier transitions, referral rules never exposed to client or LLM |

---

## Tool Definitions

Inspired by the `realtime-voice-component` form demo's pattern: narrow tools, one action per call, app-side validation, discovery tool for adaptive flow.

### Core Tools (5)

#### 1. `record_answer`

Records one questionnaire response. Equivalent to the form demo's `set_field`.

```
name: "record_answer"
description: "Record the woman's answer to the current question."
parameters:
  factor_id: enum [1.1, 1.2, 1.3, ..., 4.7b]   # from doc 07 hierarchy
  value: string                                    # normalized answer
  raw_utterance: string                            # what she actually said (for audit)
```

**Validation (server-side, per factor):**

| Factor | Validation rule |
|---|---|
| 1.1 (age) | Integer, 18–100 |
| 1.4 (parity) | 0, 1, 2, 3+ |
| 1.6 (waist) | cm numeric OR categorical {flat, slightly_rounded, noticeably_rounded} |
| 1.8 (fried food) | {daily, few_times_week, once_week, rarely_never} |
| 1.11 (menarche age) | Integer, 8–20 |
| 1.12 (symptoms) | {yes, no} per sub-question |
| ... | Each factor has type-specific rules |

**Returns:**

```json
{
  "accepted": true,
  "factor_id": "1.1",
  "normalized_value": "47",
  "next_action": "continue"
}
```

Or on validation failure:

```json
{
  "accepted": false,
  "factor_id": "1.1",
  "error": "Age must be between 18 and 100.",
  "retry": true
}
```

#### 2. `get_next_question`

The adaptive flow engine. Equivalent to `get_unfilled_fields` but smarter — it decides which question to ask next based on accumulated answers, tier logic, and risk signals.

```
name: "get_next_question"
description: "Get the next question to ask based on the woman's answers so far."
parameters: {}   # no parameters — engine decides
```

**Returns:**

```json
{
  "factor_id": "1.5",
  "tier": 1,
  "question_text": "Did you breastfeed your children? For roughly how long in total?",
  "response_options": ["Never", "Less than 6 months", "6 to 12 months", "12 to 24 months", "More than 24 months"],
  "skip_reason": null,
  "context_for_model": "She has 2 children (from 1.4). Ask about breastfeeding duration across all children."
}
```

Or when a question should be skipped:

```json
{
  "factor_id": "1.5",
  "tier": 1,
  "skipped": true,
  "skip_reason": "Nulliparous — breastfeeding not applicable.",
  "next": { "factor_id": "1.6", "..." : "..." }
}
```

Or when transitioning tiers:

```json
{
  "tier_transition": true,
  "from_tier": 1,
  "to_tier": 2,
  "risk_summary": "borderline",
  "offer_message": "Your answers so far suggest some risk factors worth exploring. Would you like to continue with a few more questions for a more complete picture?",
  "factors_remaining": 8,
  "estimated_time": "4 minutes"
}
```

#### 3. `flag_urgent_referral`

Safety override. Called when symptoms or high-risk conditions are detected.

```
name: "flag_urgent_referral"
description: "Flag for immediate clinical referral. Called when breast symptoms or critical risk factors are reported."
parameters:
  reason: enum [breast_symptom, brca_known, multiple_family, atypical_hyperplasia, chest_radiation]
  details: string
```

**Returns:**

```json
{
  "action": "immediate_referral",
  "message": "Based on the symptoms you've described, I strongly recommend seeing a doctor for a clinical breast examination as soon as possible. This is not a diagnosis — it's a precaution.",
  "continue_assessment": true,
  "referral_logged": true
}
```

**Agent rule:** The model MUST call this tool whenever 1.12 (breast symptoms) = yes. This is enforced in the system prompt AND validated server-side — if `record_answer(1.12, "yes")` is received without a subsequent `flag_urgent_referral`, the engine auto-triggers it.

#### 4. `compute_risk_score`

Final computation after all applicable tiers are complete.

```
name: "compute_risk_score"
description: "Compute the final breast cancer risk score based on all recorded answers."
parameters: {}
```

**Returns:**

```json
{
  "risk_level": "moderate",
  "risk_tier": 3,
  "risk_tiers": {
    "1_very_low": "0–5%",
    "2_low": "5–15%",
    "3_moderate": "15–25%",
    "4_high": "25–40%",
    "5_very_high": ">40%"
  },
  "key_factors": [
    { "factor": "Never breastfed", "contribution": "high", "or": 3.69 },
    { "factor": "Sedentary lifestyle", "contribution": "high", "or": 4.6 },
    { "factor": "Central obesity", "contribution": "moderate", "or": 2.74 }
  ],
  "protective_factors": [
    { "factor": "3 children", "contribution": "protective", "or": 0.55 },
    { "factor": "Rural upbringing", "contribution": "protective", "or": 0.65 }
  ],
  "recommendations": [
    "Schedule a clinical breast examination within the next 3 months",
    "Increase physical activity — even 30 minutes of walking daily is protective",
    "Consider reducing fried food intake"
  ],
  "screening_recommendation": "Annual clinical breast exam. Discuss mammography with your doctor.",
  "summary_for_voice": "Based on your answers, your risk level is moderate. Your main risk factors are physical inactivity and central obesity, but you have protective factors like having three children and growing up in a rural area. I recommend scheduling a clinical breast exam within three months."
}
```

#### 5. `get_session_state`

Lets the model re-ground itself on what's been captured so far. Equivalent to the form demo's state sync pattern.

```
name: "get_session_state"
description: "Get a summary of all answers recorded so far and current assessment progress."
parameters: {}
```

**Returns:**

```json
{
  "answers_recorded": 8,
  "current_tier": 1,
  "factors_completed": ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8"],
  "factors_remaining_in_tier": ["1.9", "1.10", "1.11", "1.12"],
  "accumulated_risk_signals": {
    "elevated": ["never_breastfed", "sedentary", "central_obesity"],
    "protective": ["parity_3", "early_first_birth"],
    "neutral": ["age_47", "no_family_history", "no_biopsy"]
  },
  "urgent_flags": [],
  "estimated_completion": "4 more minutes"
}
```

### Auxiliary Tools (3)

#### 6. `clarify_question`

When the woman asks "what does that mean?" or seems confused.

```
name: "clarify_question"
description: "Get a simpler explanation of the current question."
parameters:
  factor_id: string
  confusion_type: enum [medical_term, why_asking, how_to_answer, language]
```

Returns plain-language explanation tailored to factor. Example for 1.3 (biopsy): *"A biopsy is when a doctor takes a small piece of tissue from your breast to test it. Have you ever had that done?"*

#### 7. `switch_language`

Mid-conversation language switch.

```
name: "switch_language"
description: "Switch the conversation to a different language."
parameters:
  language: enum [en, hi, ta, te, kn, ml, bn, mr, gu, od, pa]
```

Reconfigures Sarvam STT/TTS pipeline. Session state preserved. The model's system prompt updates to instruct responses in the new language.

#### 8. `end_session`

Graceful termination.

```
name: "end_session"
description: "End the assessment session. Called when the assessment is complete, the woman wants to stop, or timeout."
parameters:
  reason: enum [completed, user_requested, timeout, error]
  partial_results: boolean
```

---

## System Prompt Design

The system prompt follows the `realtime-voice-component` principle: **tool-first, constrained scope, no free-form medical advice.**

```
You are Sakhi, a warm and empathetic health assessment assistant for PinkShieldAI.
You help women understand their breast cancer risk through a conversational
questionnaire. You are NOT a doctor. You do NOT diagnose. You assess risk factors.

## Your tools

You have 8 tools. Use them — do not answer from memory.

- `record_answer`: Record each answer. One answer per call. Always validate.
- `get_next_question`: Ask the engine what to ask next. NEVER decide on your own.
- `flag_urgent_referral`: Call IMMEDIATELY if any breast symptom is reported.
- `compute_risk_score`: Call when the engine signals assessment is complete.
- `get_session_state`: Call if you lose track of where you are in the assessment.
- `clarify_question`: Call when the woman is confused. Do not explain medical
  terms from your own knowledge — use the tool.
- `switch_language`: Call if the woman wants to switch languages.
- `end_session`: Call to end the session gracefully.

## Rules

1. ALWAYS call `get_next_question` to decide what to ask. Never skip ahead,
   never go back, never pick questions yourself.
2. Ask ONE question at a time. Wait for the answer before calling
   `get_next_question` again.
3. If a tool can handle the request, CALL THE TOOL. Do not reply in text.
4. NEVER provide a diagnosis, prognosis, or treatment recommendation from your
   own knowledge. All recommendations come from `compute_risk_score`.
5. If the woman reports ANY breast symptom (lump, discharge, skin change, pain),
   call `flag_urgent_referral` IMMEDIATELY before continuing.
6. Be conversational, warm, and reassuring. Use simple language. Avoid medical
   jargon unless the woman uses it first.
7. If the woman asks "why are you asking this?", call
   `clarify_question(factor_id, "why_asking")`.
8. Respect "I don't want to answer" — record as null and move on.
9. At tier transitions, read the `offer_message` from `get_next_question`
   naturally. Respect her choice if she wants to stop.
10. NEVER reveal internal factor IDs, tier numbers, OR values, or risk model
    details. Speak in plain language only.

## Tone

- Address her respectfully. Use "aap" (formal you) in Hindi.
- Acknowledge sensitive topics: "I understand this can be personal. There are
  no right or wrong answers."
- After recording an answer, brief acknowledgment: "Thank you" or
  "Got it" — then immediately call `get_next_question`.
- Do not summarize what she said back to her unless clarifying ambiguity.

## Session flow

1. Greet and explain purpose (~15 seconds)
2. Call `get_next_question` to start
3. Loop: ask question → record answer → get next question
4. At tier boundaries, offer to continue or stop
5. When engine signals done, call `compute_risk_score`
6. Deliver results conversationally from the tool output
7. Call `end_session(completed)`
```

### State Sync Pattern

After every `record_answer`, the questionnaire engine returns a `context_for_model` field in the next `get_next_question` response. This keeps the model grounded on what it knows without requiring it to track state itself — identical to the `realtime-voice-component` pattern of pushing UI state back into the session after each change.

---

## Session Flow — End to End

```
Woman calls/messages
        │
        ▼
┌─ Transport Gateway ─────────────────────────────────────────────┐
│  Channel detection (WhatsApp / Web / Phone)                     │
│  Language detection (from phone number region or explicit ask)   │
│  Create session_id                                              │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─ Voice Pipeline ────────────────────────────────────────────────┐
│  IF voice channel:                                              │
│    Audio → Sarvam STT (streaming, <500ms) → text               │
│  IF text channel (WhatsApp/web):                                │
│    Text passes through directly                                 │
└────────┬────────────────────────────────────────────────────────┘
         │ text
         ▼
┌─ Session Manager ───────────────────────────────────────────────┐
│                                                                  │
│  1. Claude receives text + system prompt + tool definitions      │
│  2. Claude calls `get_next_question` → engine returns question   │
│  3. Claude speaks question naturally                             │
│  4. Woman answers → STT → text → Claude                         │
│  5. Claude calls `record_answer(factor_id, value)`               │
│  6. Engine validates, stores, updates risk state                 │
│  7. Claude calls `get_next_question` → next question or tier    │
│     transition or assessment complete                            │
│  8. Loop until done or woman stops                               │
│  9. Claude calls `compute_risk_score` → delivers results         │
│                                                                  │
│  Throughout: `postToolResponse: true` equivalent — Claude        │
│  automatically chains tool calls without waiting for re-trigger  │
│                                                                  │
└────────┬────────────────────────────────────────────────────────┘
         │ text
         ▼
┌─ Voice Pipeline ────────────────────────────────────────────────┐
│  IF voice channel:                                              │
│    Text → Sarvam TTS (streaming, <400ms) → audio                │
│  IF text channel:                                               │
│    Text delivered directly                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Streaming Pipeline for Low Latency

The critical latency path is: **woman finishes speaking → she hears the next question.**

```
                 ┌──────────────────── target: <1.5s ────────────────────┐
                 │                                                       │
Woman speaks ─→ STT(stream) ─→ Claude(TTFT) ─→ Tool exec ─→ TTS(stream) ─→ Woman hears
                 200–500ms      300–600ms       <50ms        200–400ms
                                                  │
                                          Questionnaire engine
                                          lookup is local/cached
                                          — near-instant
```

| Stage | Target | Technique |
|---|---|---|
| STT | <500ms | Sarvam streaming ASR; start processing before utterance ends |
| Claude TTFT | <600ms | Sonnet for speed; Haiku fallback for degraded conditions; tool-only mode reduces output tokens |
| Tool execution | <50ms | Questionnaire engine is stateless lookup + simple validation; no DB call in hot path |
| TTS | <400ms | Sarvam streaming TTS; start speaking before full text is generated |
| **Total** | **<1.5s** | Streaming at every stage; no batch boundaries |

### Latency Optimization: Tool-Only Mode

Following the `realtime-voice-component` pattern, Claude runs in effective tool-only mode. The system prompt forces tool calls for every action. This means:

- Claude's output is primarily tool calls (short, structured) + brief conversational text
- No long-form responses to generate — keeps TTFT low
- `postToolResponse` equivalent: after `record_answer` returns, Claude immediately calls `get_next_question` without waiting for another user turn
- The engine pre-computes the next question while Claude is processing the current answer — ready instantly when called

---

## Questionnaire Engine — Server-Side State Machine

The engine implements the adaptive flow from doc 07. It is NOT an LLM — it is deterministic code.

```python
class QuestionnaireEngine:
    """Deterministic state machine. No LLM calls. No randomness."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.answers: dict[str, Answer] = {}
        self.current_tier: int = 1
        self.risk_signals: RiskAccumulator = RiskAccumulator()
        self.referral_flags: list[ReferralFlag] = []
        self.started_at: datetime = now()

    def record_answer(self, factor_id: str, value: str,
                      raw_utterance: str) -> RecordResult:
        """Validate and store one answer. Update risk signals."""
        schema = FACTOR_SCHEMAS[factor_id]
        normalized = schema.validate(value)
        if not normalized.valid:
            return RecordResult(accepted=False, error=normalized.error)

        self.answers[factor_id] = Answer(
            value=normalized.value,
            raw=raw_utterance,
            recorded_at=now()
        )
        self.risk_signals.update(factor_id, normalized.value)
        return RecordResult(accepted=True, normalized_value=normalized.value)

    def get_next_question(self) -> NextQuestion:
        """Decide what to ask next. Pure logic — no LLM."""

        # Check for tier completion
        tier_factors = TIER_FACTORS[self.current_tier]
        remaining = [f for f in tier_factors
                     if f.id not in self.answers
                     and not self._should_skip(f)]

        if remaining:
            factor = remaining[0]
            return NextQuestion(
                factor_id=factor.id,
                tier=self.current_tier,
                question_text=factor.question,
                response_options=factor.options,
                context_for_model=self._build_context(factor)
            )

        # Tier complete — decide whether to advance
        if self.current_tier < 4:
            return self._evaluate_tier_transition()

        # All tiers done
        return NextQuestion(assessment_complete=True)

    def _should_skip(self, factor: Factor) -> bool:
        """Adaptive skip logic from doc 07."""
        if factor.id == "1.5":  # breastfeeding
            parity = self.answers.get("1.4")
            return parity and parity.value == "0"  # nullipara
        if factor.id == "1.10":  # menstrual regularity
            meno = self.answers.get("1.9")
            return meno and meno.value == "postmenopausal"
        if factor.id == "2.1a":  # extended pedigree
            fh = self.answers.get("1.2")
            return fh and fh.value == "no"
        # ... full skip logic per doc 07 adaptive flow
        return False

    def _evaluate_tier_transition(self) -> NextQuestion:
        """Decide whether to enter next tier based on risk level."""
        risk_level = self.risk_signals.current_level()

        if self.current_tier == 1:
            if risk_level == "clearly_low":
                # Offer Tier 2 as optional
                return NextQuestion(
                    tier_transition=True,
                    from_tier=1, to_tier=2,
                    risk_summary="low",
                    offer_message="Your answers so far suggest lower risk. "
                                  "Would you like to continue with a few more "
                                  "questions for a more complete picture?",
                    optional=True
                )
            else:
                # Borderline or elevated — proceed to Tier 2
                self.current_tier = 2
                return self.get_next_question()

        if self.current_tier == 2:
            if risk_level in ("borderline", "elevated"):
                self.current_tier = 3
                return NextQuestion(
                    tier_transition=True,
                    from_tier=2, to_tier=3,
                    offer_message="We have a few more questions that can help "
                                  "make your risk picture more complete. "
                                  "Would you like to continue?",
                    optional=True
                )
            else:
                return NextQuestion(assessment_complete=True)

        # Tier 3 → done (Tier 4 is research-only)
        return NextQuestion(assessment_complete=True)

    def compute_risk_score(self) -> RiskResult:
        """Compute final risk using India-calibrated model."""
        # Uses ORs from doc 07 evidence tables
        # Logistic regression with India-specific baseline
        # Returns 5-tier risk level + key factors + recommendations
        ...
```

### Why Deterministic (Not LLM-Driven)

| Concern | LLM-driven flow | Deterministic engine |
|---|---|---|
| **Reproducibility** | Same woman could get different questions on different calls | Identical input → identical flow |
| **Auditability** | "Why did you ask that?" → "the model decided" | Full decision trace in code |
| **Safety** | Model might skip 1.12 (symptoms) | Engine guarantees every Tier 1 question is asked |
| **Regulation** | Insurer/regulator cannot audit an LLM | Engine logic is inspectable, testable, versionable |
| **Speed** | LLM call per decision = added latency | Hash table lookup = <1ms |

The LLM's role is **conversational delivery**, not **clinical logic**. It makes the questions sound natural, handles clarifications, manages conversational flow — but it never decides what to ask or how to score.

---

## Channel Adapters

### WhatsApp (via Gupshup)

```
Woman sends WhatsApp message
    │
    ▼
Gupshup webhook → Session Manager
    │
    ├─ Text message → direct to Claude
    ├─ Voice note → Sarvam STT → text → Claude
    │
    ▼
Claude response text → Gupshup API → WhatsApp message
    │
    ├─ Option buttons for multiple-choice questions
    ├─ Text for open-ended questions
    └─ (No TTS needed — text channel)
```

**WhatsApp-specific adaptations:**
- Use interactive message buttons for response options (e.g., "Never / <6 months / 6–12 months / >24 months")
- Support voice notes — run through Sarvam STT before processing
- Session state persists across message gaps (woman can close WhatsApp and come back hours later)
- Send a summary card at end with risk level and recommendations

### Phone / IVR (via Exotel)

```
Woman dials number or receives outbound call
    │
    ▼
Exotel connects → WebSocket audio stream
    │
    ▼
Sarvam STT (streaming) ←→ Claude ←→ Sarvam TTS (streaming)
    │
    ▼
Audio back to phone call
```

**Phone-specific adaptations:**
- Full streaming pipeline — sub-1.5s latency critical for natural conversation
- DTMF fallback for yes/no questions (press 1 for yes, 2 for no)
- Barge-in handling: if woman starts speaking while TTS is playing, stop TTS and process her speech
- Silence detection: if no response in 10s, repeat question; after 30s, ask if she's still there
- Call recording (with consent) for audit trail
- Regional phone number → auto-detect likely language → confirm in greeting

### Web Chat

```
Browser ←→ WebSocket ←→ Session Manager
    │
    ├─ Text input → direct to Claude
    ├─ Microphone → Sarvam STT → text → Claude
    │
    ▼
Claude response → rendered as chat bubbles
    │
    ├─ Clickable option chips for multiple-choice
    ├─ Text input for open-ended
    └─ Optional: Sarvam TTS playback for accessibility
```

**Web-specific adaptations:**
- Visual progress indicator (Tier 1: ████░░░░ 67%)
- Clickable response options reduce friction vs. typing
- Optional voice mode (microphone button) — same Sarvam pipeline
- Show risk visualization at end (chart, not just text)
- "Save and continue later" — persist session, send email/WhatsApp link

---

## Language Handling

### Detection and Switching

```
Session start:
  1. Channel signal (WhatsApp locale, phone number STD code, browser lang)
  2. Greeting in detected language + English fallback
  3. "Would you like to continue in [detected language]?"
  4. Explicit `switch_language` tool available throughout

Mid-session switch:
  1. Woman starts speaking in a different language
  2. Sarvam STT detects language mismatch
  3. Session Manager calls `switch_language` automatically
  4. TTS switches; all subsequent questions in new language
  5. Session state fully preserved — no restart needed
```

### Code-Switching Support

Indian women frequently mix languages (e.g., Hindi + English, Tamil + English). Sarvam's ASR handles this natively — "code-switching" is a first-class feature of Saaras v3. The STT output is mixed-language text; Claude processes it naturally since it understands both.

### Language Coverage Plan

| Phase | Languages | Coverage (insurance market) |
|---|---|---|
| MVP | English, Hindi | ~60% of urban health insurance buyers |
| Phase 2 | + Tamil, Telugu, Kannada, Bengali, Marathi | ~90% |
| Phase 3 | + Gujarati, Malayalam, Odia, Punjabi | ~97% |
| Future | Assamese, Urdu + others via Bhashini fallback | ~99% |

---

## Conversation Example — Happy Path

```
SAKHI: Namaste! I'm Sakhi from PinkShieldAI. I'm here to help you understand
       your breast health through a few simple questions. This is not a
       medical test — just a health check-in. There are no right or wrong
       answers. Shall we begin?

WOMAN: Haan, chaliye. [Yes, let's go.]

       → Claude calls get_next_question()
       ← Engine returns: factor 1.1, "How old are you?"

SAKHI: How old are you?

WOMAN: Forty-seven.

       → Claude calls record_answer("1.1", "47", "forty-seven")
       ← Engine: accepted, normalized to 47
       → Claude calls get_next_question()
       ← Engine returns: factor 1.2, family history

SAKHI: Thank you. Has your mother, sister, or daughter ever been diagnosed
       with breast cancer?

WOMAN: No, nobody in my family.

       → Claude calls record_answer("1.2", "no", "no nobody in my family")
       → Claude calls get_next_question()
       ← Engine returns: factor 1.3 (skips 2.1 since 1.2 = no)

SAKHI: Have you ever had a breast biopsy, or been told you have a breast lump?

WOMAN: What's a biopsy? [confusion]

       → Claude calls clarify_question("1.3", "medical_term")
       ← Engine returns plain-language explanation

SAKHI: A biopsy is when a doctor takes a tiny piece of tissue from your breast
       to check it under a microscope. Have you ever had that done?

WOMAN: Oh no, never.

       → Claude calls record_answer("1.3", "no", "oh no never")
       → Claude calls get_next_question()

       [... continues through Tier 1 ...]

       ← Engine returns: tier transition 1→2, risk_summary = "borderline"

SAKHI: Thank you for answering those questions. Based on what you've shared,
       there are a couple of areas worth exploring a bit more. It would take
       about 4 more minutes. Would you like to continue?

WOMAN: Yes, please.

       → Claude calls get_next_question()
       ← Engine advances to Tier 2

       [... continues through Tier 2 ...]

       ← Engine returns: assessment_complete = true

       → Claude calls compute_risk_score()
       ← Engine returns risk level, factors, recommendations

SAKHI: Based on all your answers, your overall risk level is moderate. The
       main factors are that you haven't breastfed and you have a mostly
       sedentary lifestyle. On the positive side, having three children and
       growing up in a rural area are protective. I'd recommend scheduling a
       clinical breast exam in the next three months, and even 30 minutes of
       walking daily can make a real difference. Would you like me to send you
       a summary?

WOMAN: Yes, WhatsApp par bhej do. [Send it on WhatsApp.]

       → Claude calls end_session("completed")
```

---

## Comparison with OpenAI Realtime Voice Component Patterns

| Pattern from `realtime-voice-component` | PinkShieldAI adaptation |
|---|---|
| **Tool-constrained output mode** | Claude's system prompt enforces tool-first; no free-form medical advice |
| **`set_field` — one field per call** | `record_answer` — one answer per call, server-side validation |
| **`get_unfilled_fields` — discovery** | `get_next_question` — smarter: adaptive, tier-aware, skip-logic-aware |
| **`submit_form` — final action** | `compute_risk_score` — computes and returns structured results |
| **App-side validation (Zod)** | Server-side validation per factor schema (age range, enum matching, etc.) |
| **State sync after changes** | `context_for_model` in every `get_next_question` response |
| **`postToolResponse: true`** | Claude auto-chains: record_answer → get_next_question without waiting |
| **Shared controller across routes** | Session persists across channel switches and interruptions |
| **Ghost cursor (visual confirmation)** | Not applicable for voice — replaced by verbal acknowledgment ("Got it") |
| **Server-proxied auth** | API keys server-side; Sarvam + Claude keys never in client |
| **Wake word (optional layer)** | Future: "Hey Sakhi" activation for hands-free phone assessment |
| **WebRTC transport** | Replaced by Sarvam streaming API for Indian language support |

### What We Took

1. **Architecture**: app owns logic, voice is a constrained caller
2. **Tool design**: narrow single-action tools with server-side validation
3. **Discovery tool**: engine decides what to ask, not the model
4. **State sync**: push context back to model after every state change
5. **Auto-chaining**: model chains tool calls without extra user turns
6. **Session lifecycle**: controller/session persists across UI transitions

### What We Changed

1. **Transport**: WebRTC → Sarvam streaming (Indian language support)
2. **LLM**: GPT-4o Realtime → Claude (better tool discipline, safety)
3. **Scope**: Simple 5-field form → 36-factor adaptive multi-tier questionnaire
4. **Validation**: Client-side Zod → server-side factor-specific schemas
5. **Channels**: Browser-only → WhatsApp + Phone + Web
6. **Visual confirmation**: Ghost cursor → verbal acknowledgment + DTMF fallback

---

## Cost Model

### Per Assessment (7-minute average, Quality stack)

| Component | Calculation | Cost |
|---|---|---|
| Sarvam STT | ~3.5 min audio × ₹30/hr | ₹1.75 |
| Claude Sonnet (tool calls) | ~12 tool calls + conversational text, ~2K input + 500 output tokens per turn × 12 turns | ₹2–4 |
| Sarvam TTS | ~3.5 min output × ₹30/10K chars (~500 chars/min) | ₹5.25 |
| Infrastructure | Session management, compute, storage | ₹1–2 |
| **Total per assessment** | | **₹10–13** |
| **Charge to insurer** | | **₹100–200** |
| **Gross margin** | | **~88–93%** |

**Notes:**
- WhatsApp text-only assessments skip STT/TTS → cost drops to **₹3–5** per assessment
- Phone/IVR assessments have full STT/TTS cost
- Claude Sonnet is the sweet spot: fast enough for <600ms TTFT, smart enough for tool discipline
- At 1 lakh assessments/month: total cost ~₹10–13 lakh, revenue ~₹1–2 crore

### Cost Comparison with OpenAI Realtime API

| Stack | Per-minute cost | 7-min assessment | Indian languages |
|---|---|---|---|
| OpenAI Realtime (GPT-4o audio) | ~$0.12–0.24/min | ~$0.84–1.68 (₹70–140) | English only |
| Sarvam + Claude (our stack) | ~₹1.5–2/min | ~₹10–13 | 22 languages |

Our stack is **5–10x cheaper** and supports Indian languages. The OpenAI Realtime API's cost is dominated by GPT-4o audio token pricing; our approach decouples STT/TTS (cheap via Sarvam) from reasoning (efficient via Claude tool-only mode).

---

## Implementation Phases

### Phase 1 — WhatsApp MVP (Weeks 1–6)

**Goal:** Text-based questionnaire on WhatsApp, English + Hindi.

| Component | Implementation |
|---|---|
| Channel | Gupshup WhatsApp Business API |
| LLM | Claude Sonnet via Anthropic API |
| Questionnaire engine | Python, deterministic, in-memory state |
| Tools | `record_answer`, `get_next_question`, `compute_risk_score`, `end_session` |
| Risk model | Logistic regression using doc 07 ORs, India-calibrated baseline |
| Languages | English, Hindi |
| Output | Risk level + recommendations in chat |

**Why WhatsApp first:** No STT/TTS complexity. No latency engineering. Fastest path to real user data. WhatsApp is where Indian women already are.

### Phase 2 — Voice on Web (Weeks 7–12)

**Goal:** Add voice input/output on web interface.

| Component | Implementation |
|---|---|
| Channel | Web chat with optional microphone |
| STT/TTS | Sarvam Saaras v3 / Bulbul v3 |
| Streaming | WebSocket between browser and session manager |
| Visual | Progress bar, clickable options, risk visualization |
| Languages | + Tamil, Telugu, Kannada |

### Phase 3 — Phone/IVR (Weeks 13–20)

**Goal:** Outbound and inbound phone-based assessments.

| Component | Implementation |
|---|---|
| Telephony | Exotel |
| Streaming | Full duplex audio streaming |
| Features | Barge-in, silence detection, DTMF fallback |
| Languages | + Bengali, Marathi, Gujarati |
| Scale | Target 10K assessments/month |

### Phase 4 — Scale and Optimize (Weeks 21+)

| Component | Implementation |
|---|---|
| Wake word | "Hey Sakhi" via Porcupine (following realtime-voice-component demo pattern) |
| Languages | + Malayalam, Odia, Punjabi; Bhashini fallback for others |
| Risk model | Calibrate with real assessment data; validate against BRISK |
| Insurer dashboard | Portfolio risk analytics, completion funnels, language distribution |
| Scale | Target 1 lakh assessments/month |
