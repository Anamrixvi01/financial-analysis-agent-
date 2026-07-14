"""
state.py — Shared State for the Multi-Agent Financial Analysis System

This TypedDict is the "whiteboard" shared by ALL agents in the LangGraph graph.
Every agent reads from it and writes its output back to it.
The supervisor reads `next_agent` to decide who runs next.
"""

import operator
from typing import Annotated, TypedDict


class FinancialAnalysisState(TypedDict):
    # ── Conversation history ──────────────────────────────────────────────────
    # Annotated with operator.add so LangGraph APPENDS new messages
    # instead of overwriting. Each agent can add its own message.
    messages: Annotated[list, operator.add]

    # ── Input ─────────────────────────────────────────────────────────────────
    ticker: str          # e.g. "AAPL" — set once by the user, never changes
    company_name: str    # e.g. "Apple Inc" — filled by Data Fetcher agent

    # ── Agent outputs (filled in sequence) ───────────────────────────────────
    raw_data: dict       # Step 1: Data Fetcher fills this (price, ratios, news)
    analysis: dict       # Step 2: Analyzer fills this (growth, margins, PE)
    report_draft: str    # Step 3: Writer fills this (full prose report)
    final_report: str    # Step 4: Risk Review fills this (report + disclaimers)
    risk_flags: list     # Step 4: Risk Review adds any warnings here

    # ── Supervisor control ────────────────────────────────────────────────────
    # The supervisor writes the name of the next agent to run here.
    # LangGraph's conditional edge reads this to route the graph.
    # Values: "data_fetcher" | "analyzer" | "writer" | "risk_review" | "FINISH"
    next_agent: str
