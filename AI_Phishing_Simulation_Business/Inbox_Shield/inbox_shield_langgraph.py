"""NorthStar Inbox Shield - LangGraph PoC backed by xAI Grok 4.3.

Run with the bundled CEO-wire-fraud sample:
    python inbox_shield_langgraph.py

Or pass any text file containing an email:
    python inbox_shield_langgraph.py sample_email.txt

Requires XAI_API_KEY in the environment.
"""

from __future__ import annotations

import json
import os
import sys
import warnings
from pathlib import Path
from typing import Literal, Optional, TypedDict

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_xai import ChatXAI
    from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field, ValidationError


SYSTEM_PROMPT = """You are NorthStar Inbox Shield, an AI email analyst for business users.
Your job is to read an inbound email and return a structured JSON object
containing summary, action items, risk scoring, impersonation analysis,
and recommended next steps.

Follow these rules:
- Be concise and factual.
- Never invent details not present in the email.
- If information is missing, return null instead of guessing.
- Keep summaries under 3 sentences.
- Keep action items under 5 items.
- Action items must be defensive tasks for the recipient, not the actions
  requested by the sender. For example, say "Do not process the wire" or
  "Verify with the executive through a known phone number", not "Process the
  wire transfer".
- If recommended_action is "block", action_items must not tell the recipient
  to comply with the sender's request.
- Do not claim that a sender domain matches or does not match the real
  organization unless the legitimate domain is present in the email or provided
  as context. If you cannot verify the domain, say that domain legitimacy cannot
  be confirmed from the email content.
- Risk score must be between 0 and 100.
- Impersonation likelihood must be between 0 and 100.
- Always return valid JSON. No prose. No markdown fences. Just the JSON object.

Return your output in the following JSON format:

{
  "summary": "string",
  "action_items": [
    {
      "task": "string",
      "owner": "string | null",
      "due_date": "YYYY-MM-DD | null"
    }
  ],
  "risk_analysis": {
    "risk_score": number,
    "risk_factors": ["string"],
    "phishing_signals": ["string"],
    "urgency_signals": ["string"],
    "financial_risk": "low | medium | high"
  },
  "impersonation_analysis": {
    "impersonation_likelihood": number,
    "suspicious_elements": ["string"],
    "sender_legitimacy_notes": "string"
  },
  "recommended_action": "safe | needs_review | block"
}
"""


class ActionItem(BaseModel):
    task: str
    owner: Optional[str] = None
    due_date: Optional[str] = None


class RiskAnalysis(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    risk_factors: list[str]
    phishing_signals: list[str]
    urgency_signals: list[str]
    financial_risk: Literal["low", "medium", "high"]


class ImpersonationAnalysis(BaseModel):
    impersonation_likelihood: int = Field(ge=0, le=100)
    suspicious_elements: list[str]
    sender_legitimacy_notes: str


class InboxShieldResult(BaseModel):
    summary: str
    action_items: list[ActionItem]
    risk_analysis: RiskAnalysis
    impersonation_analysis: ImpersonationAnalysis
    recommended_action: Literal["safe", "needs_review", "block"]


class AgentState(TypedDict):
    email: str
    raw_response: str
    result: Optional[dict]
    error: Optional[str]
    retries: int


MAX_RETRIES = 2


def build_llm() -> ChatXAI:
    return ChatXAI(model=os.getenv("INBOX_SHIELD_MODEL", "grok-4.3"))


def analyzer_node(state: AgentState) -> AgentState:
    """Call Grok with the system prompt plus email and capture the raw response."""
    if state.get("error"):
        user_text = (
            f"Email to analyze:\n\n{state['email']}\n\n"
            f"Your previous response was rejected because: {state['error']}\n"
            f"Return ONLY the corrected JSON. No prose, no markdown fences."
        )
    else:
        user_text = f"Email to analyze:\n\n{state['email']}"

    response = build_llm().invoke(
        [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_text)]
    )
    return {**state, "raw_response": response.content.strip(), "error": None}


def validator_node(state: AgentState) -> AgentState:
    """Parse the raw response and validate against the Pydantic schema."""
    text = state["raw_response"].strip()

    if text.startswith("```"):
        text = text.strip("`").lstrip()
        if text.lower().startswith("json"):
            text = text[4:].lstrip()

    try:
        parsed = json.loads(text)
        validated = InboxShieldResult.model_validate(parsed)
        return {**state, "result": validated.model_dump(), "error": None}
    except (json.JSONDecodeError, ValidationError) as exc:
        return {
            **state,
            "result": None,
            "error": str(exc),
            "retries": state["retries"] + 1,
        }


def should_retry(state: AgentState) -> str:
    if state.get("result") is not None:
        return "done"
    if state["retries"] >= MAX_RETRIES:
        return "give_up"
    return "retry"


def give_up_node(state: AgentState) -> AgentState:
    """Return a conservative fallback so downstream tools still get JSON."""
    return {
        **state,
        "result": {
            "summary": "Unable to analyze - model returned invalid output after retries.",
            "action_items": [],
            "risk_analysis": {
                "risk_score": 50,
                "risk_factors": ["analyzer_failure"],
                "phishing_signals": [],
                "urgency_signals": [],
                "financial_risk": "medium",
            },
            "impersonation_analysis": {
                "impersonation_likelihood": 50,
                "suspicious_elements": [],
                "sender_legitimacy_notes": "Could not assess - model output rejected.",
            },
            "recommended_action": "needs_review",
        },
    }


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("analyze", analyzer_node)
    graph.add_node("validate", validator_node)
    graph.add_node("give_up", give_up_node)
    graph.add_edge(START, "analyze")
    graph.add_edge("analyze", "validate")
    graph.add_conditional_edges(
        "validate",
        should_retry,
        {"retry": "analyze", "give_up": "give_up", "done": END},
    )
    graph.add_edge("give_up", END)
    return graph.compile()


def analyze_email(email: str) -> dict:
    final = build_graph().invoke(
        {
            "email": email,
            "raw_response": "",
            "result": None,
            "error": None,
            "retries": 0,
        }
    )
    return final["result"]


SAMPLE_EMAIL = """From: "CEO Mark Thompson" <m.thompson@northstar-finance-llc.com>
To: accounting@yourcompany.ca
Date: 2026-05-22 14:32 UTC
Subject: URGENT - wire transfer needed before EOD

Hi,

I'm stuck in a board meeting and can't talk. I need you to wire $42,500 to our
new supplier today before 4pm. They've been waiting for this payment for two
weeks and we'll lose the contract if it doesn't go through.

Use these details:
  Beneficiary: Aurora Holdings Ltd.
  Bank: First Caribbean International
  Account: 8839-22-771-001
  SWIFT: FCIBKYKY

Don't call me, I can't pick up. Just confirm once it's done.

Mark
"""


def load_email_from_args() -> str:
    if len(sys.argv) <= 1:
        return SAMPLE_EMAIL

    path = Path(sys.argv[1])
    return path.read_text(encoding="utf-8")


def main() -> None:
    if not os.getenv("XAI_API_KEY"):
        print("XAI_API_KEY is not set in this shell.", file=sys.stderr)
        sys.exit(1)

    result = analyze_email(load_email_from_args())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
