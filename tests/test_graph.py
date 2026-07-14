"""
tests/test_graph.py — Test the full LangGraph pipeline

This tests the REAL LangGraph system — not manual agent calls.
LangGraph now controls the routing automatically.

Usage: python tests/test_graph.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph import run_analysis


def test_graph(ticker: str = "AAPL"):
    print(f"\n{'='*60}")
    print(f"  LANGGRAPH PIPELINE TEST — {ticker}")
    print(f"{'='*60}")

    # Run the full pipeline via LangGraph
    final_state = run_analysis(ticker)

    # Print results
    print(f"\n{'='*60}")
    print(f"  FINAL REPORT — {final_state['company_name']} ({ticker})")
    print(f"{'='*60}")
    print(final_state["final_report"])

    if final_state["risk_flags"]:
        print(f"\n⚠️  Risk Flags ({len(final_state['risk_flags'])}):")
        for flag in final_state["risk_flags"]:
            print(f"   • {flag}")

    print(f"\n{'='*60}")
    print(f"  PIPELINE COMPLETE ✅")
    print(f"  Agent message log:")
    for msg in final_state["messages"]:
        print(f"   → {msg}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Try with MSFT this time!
    test_graph("MSFT")
