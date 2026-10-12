"""Claude tool definitions for PinkShieldAI.

8 tools that Claude can call during the assessment conversation:
- record_answer: Save a questionnaire response
- get_next_question: Get the next unanswered question
- flag_urgent_referral: Flag for immediate clinical referral
- compute_risk_score: Calculate risk from collected answers
- get_session_state: Get progress summary
- clarify_question: Get help text for a question
- switch_language: Note language preference
- end_session: End the assessment early
"""

from .._types import ToolDef

TOOL_DEFINITIONS: list[ToolDef] = [
    {
        "name": "record_answer",
        "description": "Record the user's answer to a questionnaire factor. Call this for every answer the user gives. The value must match the expected data type and options for the factor.",
        "input_schema": {
            "type": "object",
            "properties": {
                "factor_id": {
                    "type": "string",
                    "description": "The factor ID (e.g. '1.1', '1.4b')",
                },
                "value": {
                    "type": "string",
                    "description": "The normalized answer value (e.g. '45' for age, 'yes'/'no' for booleans, option value for categoricals)",
                },
                "raw_utterance": {
                    "type": "string",
                    "description": "The user's original words, preserved for context",
                },
            },
            "required": ["factor_id", "value"],
        },
    },
    {
        "name": "get_next_question",
        "description": "Get the next unanswered question in the assessment. Returns the question text, data type, valid options, and clarification help. Returns assessment_complete when all Tier 1 questions are answered.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "flag_urgent_referral",
        "description": "Flag this session for urgent clinical referral. Use IMMEDIATELY if the user reports any breast symptoms (lump, discharge, pain, skin changes) or any other urgent clinical finding.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Brief reason for the referral (e.g. 'breast lump reported', 'nipple discharge')",
                },
                "details": {
                    "type": "string",
                    "description": "Additional details from the conversation",
                },
            },
            "required": ["reason"],
        },
    },
    {
        "name": "compute_risk_score",
        "description": "Compute the final breast cancer risk score from all collected answers. Call this when get_next_question returns assessment_complete. Returns risk level, probability, key risk factors, protective factors, and recommendations.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_session_state",
        "description": "Get the current session state including progress, answered questions, and their values. Useful for context when the conversation resumes or to check what has been collected so far.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "clarify_question",
        "description": "Get clarification text for a specific question. Use when the user asks what a question means or why it's being asked.",
        "input_schema": {
            "type": "object",
            "properties": {
                "factor_id": {
                    "type": "string",
                    "description": "The factor ID to get clarification for",
                },
            },
            "required": ["factor_id"],
        },
    },
    {
        "name": "switch_language",
        "description": "Note the user's language preference. MVP supports English only for questions, but this records the preference for future multilingual support.",
        "input_schema": {
            "type": "object",
            "properties": {
                "language": {
                    "type": "string",
                    "description": "Language code (e.g. 'en', 'hi', 'ta', 'te', 'bn')",
                },
            },
            "required": ["language"],
        },
    },
    {
        "name": "end_session",
        "description": "End the assessment session early. Use when the user wants to stop or is no longer willing to continue.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Why the session is ending (e.g. 'user_ended', 'timeout')",
                },
            },
            "required": ["reason"],
        },
    },
]

TOOLS_BY_NAME = {t["name"]: t for t in TOOL_DEFINITIONS}
