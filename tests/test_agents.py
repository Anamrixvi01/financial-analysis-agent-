"""
tests/test_agents.py — Test all 4 agents running in sequence

This simulates the full pipeline WITHOUT LangGraph yet.
We manually pass state from one agent to the next.
In Step 4, LangGraph will do this automatically.

Usage: python tests/test_agents.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.data_fetcher import data_fetcher_agent
from agents.analyzer import analyzer_agent
from agents.writer import writer_agent
from agents.risk_review import risk_review_agent


def run_pipeline(ticker: str):
    print(f"\n{'='*60}")
    print(f"  FINANCIAL ANALYSIS PIPELINE — {ticker}")
    print(f"{'='*60}")

    # Starting state — only ticker is set
    state = {
        "messages":     [],
        "ticker":       ticker,
        "company_name": "",
        "raw_data":     {},
        "analysis":     {},
        "report_draft": "",
        "final_report": "",
        "risk_flags":   [],
        "next_agent":   "data_fetcher",
    }

    # ── Run agents in sequence ────────────────────────────────────────────────
    # Agent 1
    state.update(data_fetcher_agent(state))

    # Agent 2
    state.update(analyzer_agent(state))

    # Agent 3
    state.update(writer_agent(state))

    # Agent 4
    state.update(risk_review_agent(state))

    # ── Print final report ────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  FINAL REPORT")
    print(f"{'='*60}")
    print(state["final_report"])

    if state["risk_flags"]:
        print(f"\n⚠️  Risk Flags ({len(state['risk_flags'])}):")
        for flag in state["risk_flags"]:
            print(f"   • {flag}")

    print(f"\n{'='*60}")
    print(f"  PIPELINE COMPLETE ✅")
    print(f"  Messages log:")
    for msg in state["messages"]:
        print(f"   → {msg}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_pipeline("AAPL")
