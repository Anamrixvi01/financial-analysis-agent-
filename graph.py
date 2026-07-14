"""
graph.py — LangGraph StateGraph

This is the brain of the entire system.
It connects all 4 agents + supervisor into one automated pipeline.

Flow:
    START
      ↓
    supervisor (reads next_agent)
      ↓
    data_fetcher → supervisor → analyzer → supervisor → writer → supervisor → risk_review
      ↓
    END
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph.graph import StateGraph, END
from state import FinancialAnalysisState
from agents.supervisor import supervisor_agent
from agents.data_fetcher import data_fetcher_agent
from agents.analyzer import analyzer_agent
from agents.writer import writer_agent
from agents.risk_review import risk_review_agent


def build_graph():
    """
    Builds and compiles the LangGraph StateGraph.
    Returns a compiled graph ready to run.
    """

    # ── Step 1: Create the graph with our shared state ────────────────────────
    graph = StateGraph(FinancialAnalysisState)

    # ── Step 2: Add all agent nodes ───────────────────────────────────────────
    # Each node has a name and a function to call
    graph.add_node("data_fetcher", data_fetcher_agent)
    graph.add_node("analyzer",     analyzer_agent)
    graph.add_node("writer",       writer_agent)
    graph.add_node("risk_review",  risk_review_agent)

    # ── Step 3: Set the entry point ───────────────────────────────────────────
    # LangGraph always starts here
    graph.set_entry_point("data_fetcher")

    # ── Step 4: Add conditional edges through supervisor ──────────────────────
    # After each agent finishes, supervisor decides who runs next
    # The routing map tells LangGraph: "if supervisor returns X, go to node Y"

    routing_map = {
        "data_fetcher": "data_fetcher",
        "analyzer":     "analyzer",
        "writer":       "writer",
        "risk_review":  "risk_review",
        "FINISH":       END,
    }

    graph.add_conditional_edges("data_fetcher", supervisor_agent, routing_map)
    graph.add_conditional_edges("analyzer",     supervisor_agent, routing_map)
    graph.add_conditional_edges("writer",       supervisor_agent, routing_map)
    graph.add_conditional_edges("risk_review",  supervisor_agent, routing_map)

    # ── Step 5: Compile and return ────────────────────────────────────────────
    compiled = graph.compile()
    print("[Graph] ✅ Graph compiled successfully!")
    return compiled


# ── Convenience function to run the graph ────────────────────────────────────
def run_analysis(ticker: str) -> dict:
    """
    Run the full financial analysis pipeline for a given ticker.
    Returns the final state with the complete report.
    """

    # Build the graph
    graph = build_graph()

    # Starting state — only ticker is provided by the user
    initial_state = {
        "messages":     [],
        "ticker":       ticker.upper(),
        "company_name": "",
        "raw_data":     {},
        "analysis":     {},
        "report_draft": "",
        "final_report": "",
        "risk_flags":   [],
        "next_agent":   "data_fetcher",
    }

    print(f"\n[Graph] Starting analysis for {ticker.upper()}...")

    # LangGraph runs the entire pipeline automatically
    final_state = graph.invoke(initial_state)

    return final_state
