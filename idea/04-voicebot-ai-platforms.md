# Voicebot and AI Platform Options — Multilingual Scale

## Requirements

- 10+ Indian languages (Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Odia, Punjabi minimum)
- Voice (phone/IVR) and chat (WhatsApp, web) channels
- Low latency for natural conversation
- Healthcare/insurance domain suitability
- Ability to handle code-switching (mixing English with local languages)
- Scalable to millions of assessments

---

## Enterprise Conversational AI Platforms

### Gnani.ai (formerly Vernacular.ai)

| Attribute | Details |
|---|---|
| **Focus** | End-to-end voice automation for India |
| **Indian languages** | 20+ languages; purpose-built for Indian accents and noisy environments |
| **Voice quality** | High; in-house ASR optimized for India |
| **Enterprise ready** | Yes — major Indian banks and telecos as clients |
| **Pricing** | Enterprise; per-call or per-minute; competitive for India |
| **Insurance use cases** | Claims status, policy servicing, outbound campaigns; BFSI is a key vertical |
| **Pros** | Built for India; proven scale; omnichannel; end-to-end (no stitching) |
| **Cons** | Less documentation vs. global platforms; LLM integration flexibility unclear |
| **Fit for PinkShieldAI** | **Strong** — if we want a turnkey voice platform with Indian language depth |

### Yellow.ai

| Attribute | Details |
|---|---|
| **Focus** | Enterprise omnichannel conversational AI |
| **Indian languages** | 135+ languages globally, 15+ Indian |
| **Voice quality** | Good; IVR and contact center integration |
| **Enterprise ready** | Yes — 1,100+ clients (Bajaj Finserv, Domino's, Indigo) |
| **Pricing** | Enterprise subscription; interaction-based |
| **Insurance use cases** | Bajaj Finserv insurance customer service; multiple BFSI clients |
| **Pros** | Mature; strong integrations (CRM, ticketing, telephony); generative AI "DynamicNLP" |
| **Cons** | Expensive for startups; complex platform |
| **Fit for PinkShieldAI** | **Good** — if we want enterprise credibility and multi-channel from day one |

### Haptik (Reliance Jio)

| Attribute | Details |
|---|---|
| **Focus** | Conversational AI; WhatsApp-first |
| **Indian languages** | 15+ Indian languages |
| **Voice quality** | Moderate; more chat-focused than voice |
| **Enterprise ready** | Yes — powers JioMart, JioFiber |
| **Insurance use cases** | Healthcare and insurance clients; WhatsApp-first aligns with Indian user behavior |
| **Pros** | Deep India expertise; Jio scale; strongest WhatsApp integration |
| **Cons** | Jio affiliation may concern competitors; voice is secondary to chat |
| **Fit for PinkShieldAI** | **Good for WhatsApp channel** — pair with a voice specialist for phone |

### Gupshup

| Attribute | Details |
|---|---|
| **Focus** | Business messaging infrastructure (WhatsApp API, RCS, SMS) |
| **Indian languages** | Multilingual messaging; integrates with translation services |
| **Voice quality** | Limited native voice |
| **Pricing** | Per-message; competitive at volume |
| **Fit for PinkShieldAI** | **Messaging layer only** — good for delivery infrastructure, not conversational AI |

---

## India-First AI Companies

### Sarvam AI

| Attribute | Details |
|---|---|
| **Focus** | Full-stack sovereign AI platform for Indian languages |
| **Founded** | August 2023, Bengaluru. Founders from AI4Bharat/IIT Madras |
| **Funding** | ~₹350 crore (~$41M) from Lightspeed, Peak XV/Sequoia India, Khosla Ventures |
| **Indian languages** | ASR (Saaras v3): **22 languages** (all scheduled). TTS (Bulbul v3): **11 languages**. Translation (Mayura v1): 10+ |
| **Code-switching** | Handles English + local language mixing natively |
| **Voice quality** | High; natural, expressive synthesis tuned for Indian accents and dialects |
| **Scale** | 100M+ conversations in production; sub-500ms latency; 99.9% uptime SLA |
| **Enterprise clients** | SBI Life (millions of policy calls in 10+ languages), Tata Capital (3x engagement increase), UIDAI/Aadhaar |
| **Products** | Samvaad (voice agents), Arya (enterprise workflows), Akshar (document digitization), Studio (content transformation) |
| **LLMs** | Sarvam-105B (MoE, 128K context), Sarvam-30B — open source (Apache 2.0) |
| **Data residency** | 100% India; DPDP compliant |
| **Pricing** | STT: ₹30/hour. TTS: ₹30/10K chars. Translation: ₹20/10K chars |
| **Pros** | Purpose-built for India; proven insurance deployments; competitive INR pricing; sovereign data; open-source LLMs reduce lock-in |
| **Cons** | Young company (founded Aug 2023); TTS only 11 of 22 languages in production; ASR/TTS models proprietary |
| **Fit for PinkShieldAI** | **Very strong** — best-in-class Indian language AI with proven insurance scale; pair with Claude as the reasoning brain |

### Bhashini (Government of India / MeitY)

| Attribute | Details |
|---|---|
| **Focus** | National public digital platform for language translation |
| **Indian languages** | Aims for all 22 scheduled languages; 12–15+ currently supported |
| **Voice quality** | Moderate; improving but may not match commercial platforms |
| **Pricing** | Free/open for government and non-commercial; commercial pricing unclear |
| **Pros** | Free/low-cost; broadest language ambition; government backing; Digital India integration |
| **Cons** | Variable quality; limited enterprise SLA; latency concerns |
| **Fit for PinkShieldAI** | **Supplementary** — use as fallback for languages not covered by primary platform |

---

## Global Cloud Platforms

### Azure Bot Service + Azure AI Speech

| Attribute | Details |
|---|---|
| **Indian languages** | **13 Indian languages + English India** for both STT and TTS — Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Odia, Punjabi, Assamese, Urdu, Nepali |
| **TTS voices** | **47 voices** across 13 Indian languages; Hindi has 9 voices with emotional styles (cheerful, empathetic, newscast); English India has 15 voices including DragonHD Neural |
| **Voice quality** | Highest among cloud providers; emotional style support critical for healthcare empathy |
| **LLM integration** | Azure OpenAI (GPT-4o) native integration |
| **Healthcare** | Azure Health Bot with built-in medical triage and FHIR integration; used by Apollo Hospitals, Star Health, ICICI Lombard, Max Healthcare |
| **Pricing** | STT ~₹85/audio hour; TTS ~₹1,360/million chars (Neural), ~₹2,040/million (HD); Bot Service free tier available |
| **Compliance** | HIPAA/HITRUST, ISO 27001, SOC 2; three India data centers (Central, South, West) |
| **Pros** | Broadest Indian language TTS coverage; emotional voice styles; purpose-built Health Bot; strongest compliance story |
| **Cons** | Complex pricing with multiple services to stitch together; no single bundled product |
| **Fit for PinkShieldAI** | **Strong** — best cloud option for healthcare voicebot with max language coverage and compliance |

### Google CCAI (Dialogflow CX)

| Attribute | Details |
|---|---|
| **Indian languages** | 9–10 Indian languages (Hindi, Bengali, Tamil, Telugu, Kannada, Malayalam, Marathi, Gujarati, Urdu) |
| **Voice quality** | Good neural TTS; STT strong for Hindi and Indian English, variable for others |
| **Pricing** | Dialogflow CX ₹0.60/request (text), ₹0.085/sec (audio); STT ~₹0.50–0.75/15 sec |
| **Pros** | Strong NLU; robust GCP ecosystem; Google Health integrations |
| **Cons** | Indian language voice quality varies; GCP expertise required |
| **Fit for PinkShieldAI** | **Good** — especially if already on GCP (which we are for TANUH/BCD) |

### Amazon Lex + Polly + Connect

| Attribute | Details |
|---|---|
| **Indian languages** | Limited — Hindi and Indian English primarily; few other languages |
| **Voice quality** | Polly has neural Hindi voice (Kajal); limited beyond Hindi |
| **Pricing** | Lex ₹0.34/voice request; Polly ₹340/million chars; Connect ₹1.53/min |
| **Cons** | **Weakest Indian language support** among big three |
| **Fit for PinkShieldAI** | **Not recommended** — language coverage too narrow for multilingual India |

---

## Open-Source Options

### Rasa

| Attribute | Details |
|---|---|
| **Focus** | Open-source conversational AI framework |
| **Indian languages** | Language-agnostic NLU; bring your own training data |
| **Voice** | No native voice; integrate with external ASR/TTS |
| **Pricing** | Open Source free; Rasa Pro ~₹17 lakh/year |
| **Pros** | Full control; no vendor lock-in; on-premise for regulated industries; customizable |
| **Cons** | Requires significant ML engineering; voice is DIY; maintenance burden |
| **Fit for PinkShieldAI** | **Good for dialog management** — pair with Sarvam/Azure for voice layers |

### Vocode

| Attribute | Details |
|---|---|
| **Focus** | Open-source library for voice AI agents; orchestrates STT → LLM → TTS |
| **Indian languages** | Depends on plugged-in services |
| **Voice** | Designed for real-time voice (interruptions, turn-taking, latency) |
| **Pricing** | Free; pay for underlying services |
| **Pros** | Open source; voice-first; LLM-native architecture |
| **Cons** | Early-stage; small community; limited Indian language testing |
| **Fit for PinkShieldAI** | **Good orchestration layer** — if we build custom with LLM + STT/TTS |

### LiveKit

| Attribute | Details |
|---|---|
| **Focus** | Open-source WebRTC platform with AI Agents framework |
| **Voice** | Excellent real-time audio infrastructure; low latency |
| **Pricing** | Self-hosted free; LiveKit Cloud usage-based |
| **Pros** | Production-grade real-time audio; active community; telephony integration |
| **Cons** | Transport-layer; need to build NLU/dialog separately |
| **Fit for PinkShieldAI** | **Infrastructure layer** — great for real-time voice transport |

---

## LLM-Based Architecture (Claude/GPT as the Brain)

### Recommended Architecture

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐     ┌─────────────┐
│  Telephony   │────▶│  STT Layer   │────▶│  LLM Brain    │────▶│  TTS Layer  │
│  (Exotel /   │     │  (Sarvam /   │     │  (Claude /    │     │  (Sarvam /  │
│   Twilio)    │◀────│   Azure)     │◀────│   GPT-4o)     │◀────│   Azure)    │
└─────────────┘     └──────────────┘     └───────────────┘     └─────────────┘
                                                │
                                         ┌──────┴──────┐
                                         │ Questionnaire│
                                         │ Engine +     │
                                         │ Risk Model   │
                                         └─────────────┘
```

### Component Options

#### STT (Speech-to-Text)

| Service | Indian Languages | Latency | Pricing |
|---|---|---|---|
| **Sarvam AI** | 22 Indian languages (Saaras v3) | Moderate | ₹30/hour |
| **Azure Speech** | 15+ Indian languages | Low | ~₹85/audio hour |
| **Google Cloud Speech** | 9–10 Indian languages | Low | ~₹0.50–2.00/15 sec |
| **Deepgram** | Hindi, Indian English | Low (streaming) | ₹0.37–0.50/min |
| **Bhashini** | 12–15+ languages | Variable | Free/low-cost |

#### TTS (Text-to-Speech)

| Service | Indian Languages | Quality | Pricing |
|---|---|---|---|
| **Azure Neural TTS** | 15+ Indian languages | High | ~₹1,360/million chars |
| **Sarvam AI** | 11 Indian languages (Bulbul v3) | High (India-tuned) | ₹30/10K chars (₹3,000/million chars) |
| **Google Cloud TTS** | 9–10 Indian languages | High | ~₹340–1,360/million chars |
| **Amazon Polly** | Hindi + few others | Good | ~₹340/million chars |
| **ElevenLabs** | Limited Indian | Very high (English) | ₹425–28,000/month |

#### LLM (Reasoning Engine)

| LLM | Strengths | Considerations |
|---|---|---|
| **Claude (Anthropic)** | Strong reasoning, safety, long context, tool use | Best for complex clinical workflows; less Indian language training |
| **GPT-4o (OpenAI)** | Native multimodal (voice, text, vision) | Native voice mode could bypass STT/TTS; good reasoning |
| **Gemini (Google)** | Strong multilingual including Indian languages | Best Indian language understanding; GCP integration |
| **Llama 3.x (Meta)** | Open source; self-hostable; cost-effective | Requires hosting; Indian language performance improving |

#### Telephony (India)

| Provider | Notes |
|---|---|
| **Exotel** | India-focused cloud telephony; widely used by Indian enterprises |
| **Knowlarity** | Indian cloud communications; IVR, virtual numbers |
| **Ozonetel** | Contact center platform; India-focused |
| **Twilio** | Global; works in India but pricier; best developer experience |

### Estimated Cost per Hour of Voice Conversation

| Stack | Components | Cost/Hour |
|---|---|---|
| **Budget** | Sarvam STT + GPT-4o-mini + Google TTS Standard | ~₹42–68 |
| **Quality** | Sarvam STT + Claude Sonnet + Azure Neural TTS | ~₹300–380 |
| **Premium** | Azure STT + Claude Sonnet + Azure Neural HD TTS | ~₹340–510 |

A typical breast cancer risk assessment takes 5–10 minutes. At the "Quality" stack, that's **₹25–63 per assessment** — well within a per-assessment SaaS pricing model of ₹50–200 to the insurer.

### Cost per 1 Lakh Assessments (at Quality stack, ~7 min avg)

| Item | Cost |
|---|---|
| Sarvam STT (11,667 hrs) | ~₹3.5 lakh |
| Claude Sonnet LLM | ~₹25–30 lakh |
| Azure Neural TTS | ~₹5–8 lakh |
| **Total** | **~₹35–42 lakh** |
| **Per assessment** | **~₹35–42** |
| **Charge to insurer** | **₹100–200/assessment** |
| **Gross margin** | **~60–80%** |

### Latency Budget (Target: <1.5s end-to-end)

| Stage | Time |
|---|---|
| STT (streaming) | 200–500ms |
| LLM (TTFT, streaming) | 300–800ms |
| TTS (streaming) | 200–400ms |
| Network | 50–200ms |
| **Total** | **750ms–1,900ms** |

Achievable under 1.5s with streaming pipelines and optimized infrastructure.

---

## Recommendation for PinkShieldAI

### Short-term (MVP / Pilot)

| Component | Choice | Rationale |
|---|---|---|
| **Channel** | WhatsApp (via Gupshup/Haptik) + Web chat | Highest adoption; lowest friction; no voice complexity initially |
| **LLM** | Claude API | Best reasoning for clinical questionnaire; safety alignment; tool use for adaptive flow |
| **Language** | English + Hindi | Cover ~60% of urban health insurance buyers |
| **Orchestration** | Custom Python backend | We have the team for it; maximum control over questionnaire logic |

### Medium-term (Scale)

| Component | Choice | Rationale |
|---|---|---|
| **Voice** | Sarvam AI (STT/TTS) + Claude (reasoning) | Best Indian language quality + best reasoning |
| **Telephony** | Exotel | India-focused; enterprise-grade; affordable |
| **Languages** | Add Tamil, Telugu, Kannada, Bengali, Marathi | Cover top insurance markets: Maharashtra, Karnataka, TN, AP/Telangana, WB |
| **Platform** | Vocode or LiveKit for real-time orchestration | Handles voice conversation complexity (interruptions, latency) |

### Long-term (Platform)

| Component | Choice | Rationale |
|---|---|---|
| **Platform** | Yellow.ai or custom | Enterprise multi-channel with full CRM/insurer integration |
| **Voice** | Azure Speech + Sarvam AI (hybrid) | Broadest language coverage with India-tuned quality |
| **Fallback** | Bhashini APIs | For languages not covered by primary stack |
| **Languages** | All 10+ major Indian languages | Full market coverage |

### Comparative Summary

| Platform | Best For | Indian Lang Depth | Voice Quality | Enterprise Ready | Cost |
|---|---|---|---|---|---|
| **Gnani.ai** | End-to-end voice automation for India | Excellent (20+) | High | Yes | Enterprise (custom) |
| **Yellow.ai** | Enterprise omnichannel | Very Good (15+) | Good | Yes | Enterprise (custom) |
| **Sarvam AI** | Indian language AI-first (100M+ convos) | Excellent (22 ASR / 11 TTS) | High (India-tuned) | Yes (SBI Life, UIDAI) | ₹30/hr STT |
| **Google CCAI** | Global scale + Indian support | Good (9–10) | Good | Yes | ~₹120–325/hr (STT) |
| **Azure Bot + Speech** | Broadest language + LLM | Excellent (15+) | High | Yes | ~₹85/hr (STT) |
| **Haptik** | WhatsApp-first India | Very Good (15+) | Moderate | Yes | Enterprise (custom) |
| **Custom (LLM + STT/TTS)** | Maximum flexibility | Depends on stack | High | DIY | ₹42–510/hr (stack-dependent) |
| **Rasa + services** | Full control, on-premise | DIY | DIY | With effort | ₹17L/yr (Pro) + infra |
| **Bhashini** | Government/public sector | Good (12–15+) | Moderate | Limited | Free |
