#!/usr/bin/env python3
"""PinkShieldAI CLI — terminal chat client for breast cancer risk assessment."""

import sys

import httpx

DEFAULT_BASE_URL = "http://localhost:8100"

PINK = "\033[95m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_URL
    client = httpx.Client(base_url=base_url, timeout=60.0)

    print(f"\n{BOLD}{PINK}PinkShieldAI — Breast Cancer Risk Assessment{RESET}")
    print(f"{DIM}Connecting to {base_url}...{RESET}\n")

    # Health check
    try:
        resp = client.get("/health")
        resp.raise_for_status()
    except Exception as e:
        print(f"{RED}Cannot reach server at {base_url}: {e}{RESET}")
        print(f"Start the server first: cd backend && uvicorn src.main:app --port 8100")
        sys.exit(1)

    # Create session
    try:
        resp = client.post("/api/v1/sessions", json={"channel": "cli", "language": "en"})
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPStatusError as e:
        print(f"{RED}Failed to create session: {e.response.text}{RESET}")
        sys.exit(1)

    session_id = data["session_id"]
    print(f"{DIM}Session: {session_id}{RESET}\n")
    print(f"{PINK}Sakhi:{RESET} {data['response']}\n")

    # Chat loop
    while True:
        try:
            user_input = input(f"{CYAN}You:{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{DIM}Ending session...{RESET}")
            client.delete(f"/api/v1/sessions/{session_id}")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "bye"):
            client.delete(f"/api/v1/sessions/{session_id}")
            print(f"\n{PINK}Sakhi:{RESET} Take care! Remember, regular check-ups are important.\n")
            break

        try:
            resp = client.post(
                f"/api/v1/sessions/{session_id}/chat",
                json={"message": user_input},
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            print(f"{RED}Error: {e.response.text}{RESET}")
            continue

        print(f"\n{PINK}Sakhi:{RESET} {data['response']}\n")

        if data.get("session_status") in ("completed", "referred"):
            _show_result(client, session_id, data["session_status"])
            break

    client.close()


def _show_result(client: httpx.Client, session_id: str, status: str):
    """Fetch and display the risk assessment result."""
    if status == "referred":
        print(f"\n{RED}{BOLD}URGENT: This session was flagged for clinical referral.{RESET}")
        print(f"{RED}Please consult a doctor as soon as possible.{RESET}\n")

    try:
        resp = client.get(f"/api/v1/sessions/{session_id}/result")
        resp.raise_for_status()
        result = resp.json()
    except httpx.HTTPStatusError:
        return

    print(f"\n{BOLD}{'=' * 50}{RESET}")
    print(f"{BOLD}  Risk Assessment Result{RESET}")
    print(f"{'=' * 50}\n")

    level = result["risk_level"]
    color = {
        "low": GREEN, "average": GREEN, "moderate": YELLOW,
        "high": RED, "very_high": RED,
    }.get(level, RESET)

    print(f"  Risk Level: {color}{BOLD}{level.upper()}{RESET}")
    print(f"  Risk Score: {result['risk_probability']:.1%}\n")

    if result.get("key_risk_factors"):
        print(f"  {BOLD}Key Risk Factors:{RESET}")
        for rf in result["key_risk_factors"]:
            print(f"    {RED}- {rf['factor']}{RESET}: {rf['detail']}")

    if result.get("protective_factors"):
        print(f"\n  {BOLD}Protective Factors:{RESET}")
        for pf in result["protective_factors"]:
            print(f"    {GREEN}+ {pf['factor']}{RESET}: {pf['detail']}")

    if result.get("recommendations"):
        print(f"\n  {BOLD}Recommendations:{RESET}")
        for rec in result["recommendations"]:
            print(f"    - {rec}")

    print(f"\n{'=' * 50}\n")


if __name__ == "__main__":
    main()
