# tests/test_graph.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from graph import build_graph


def make_fake_llm_response(text: str):
    """Helper: mimics what llm.invoke(...) returns — an object with .content"""
    fake_response = MagicMock()
    fake_response.content = text
    return fake_response


@patch("agents.risk_review.save_report")
@patch("agents.risk_review.get_llm")
@patch("agents.writer.get_llm")
@patch("agents.analyzer.retrieve_past_reports")
@patch("agents.analyzer.get_llm")
@patch("agents.data_fetcher.get_price_history")
@patch("agents.data_fetcher.get_recent_news")
@patch("agents.data_fetcher.get_financial_ratios")
@patch("agents.data_fetcher.get_stock_price")
def test_full_graph_flow(
    mock_get_stock_price,
    mock_get_financial_ratios,
    mock_get_recent_news,
    mock_get_price_history,
    mock_analyzer_llm,
    mock_retrieve_past_reports,
    mock_writer_llm,
    mock_risk_llm,
    mock_save_report,
):
    # ── Arrange: fake Yahoo Finance tool outputs ──────────────────────────────
    mock_get_stock_price.invoke.return_value = {
        "current_price": 210.50,
        "previous_close": 208.30,
        "company_name": "Apple Inc",
        "52_week_high": 220.0,
        "52_week_low": 150.0,
        "market_cap": 3_000_000_000_000,
    }
    mock_get_financial_ratios.invoke.return_value = {
        "pe_ratio": 29.5,
        "eps": 6.5,
        "profit_margins": 0.26,
        "gross_margins": 0.45,
        "return_on_equity": 0.30,
        "dividend_yield": 0.005,
        "debt_to_equity": 45.0,
    }
    mock_get_recent_news.invoke.return_value = [
        {"title": "Apple announces new product", "publisher": "Reuters"},
    ]
    mock_get_price_history.invoke.return_value = {
        "start_price": 190.0,
        "end_price": 210.5,
        "percentage_change": 10.8,
        "trend": "upward",
    }

    # ── Arrange: no prior memory history (first-time analysis) ───────────────
    mock_retrieve_past_reports.return_value = []

    # ── Arrange: fake LLM responses for each agent ────────────────────────────
    mock_analyzer_llm.return_value.invoke.return_value = make_fake_llm_response(
        "Apple shows strong fundamentals with solid growth."
    )
    mock_writer_llm.return_value.invoke.return_value = make_fake_llm_response(
        "## Executive Summary\nApple Inc is performing well this quarter."
    )
    mock_risk_llm.return_value.invoke.return_value = make_fake_llm_response(
        "## RISK FACTORS\nNo major risks identified.\n\n## DISCLAIMER\nFor informational purposes only."
    )

    # ── Act: run the real graph, with only external calls mocked ─────────────
    graph = build_graph()
    initial_state = {
        "messages":     [],
        "ticker":       "AAPL",
        "company_name": "",
        "raw_data":     {},
        "analysis":     {},
        "report_draft": "",
        "final_report": "",
        "risk_flags":   [],
        "next_agent":   "data_fetcher",
    }
    final_state = graph.invoke(initial_state)

    # ── Assert: graph completed and state flowed correctly through all agents ─
    assert final_state["ticker"] == "AAPL"
    assert final_state["company_name"] == "Apple Inc"
    assert final_state["raw_data"]["price"]["current_price"] == 210.50
    assert "interpretation" in final_state["analysis"]
    assert final_state["report_draft"] != ""
    assert final_state["final_report"] != ""
    assert final_state["next_agent"] == "FINISH"

    # ── Assert: memory save was actually called with correct data ────────────
    mock_save_report.assert_called_once()
    call_kwargs = mock_save_report.call_args.kwargs
    assert call_kwargs["ticker"] == "AAPL"


def test_supervisor_routing_logic():
    """
    Unit-style test for supervisor_agent in isolation — confirms it's a pure
    relay function (reads next_agent, returns it), not an LLM call.
    """
    from agents.supervisor import supervisor_agent

    state = {"next_agent": "writer"}
    result = supervisor_agent(state)
    assert result == "writer"

    state_finish = {"next_agent": "FINISH"}
    result_finish = supervisor_agent(state_finish)
    assert result_finish == "FINISH"

    # Default fallback when next_agent is missing
    state_missing = {}
    result_missing = supervisor_agent(state_missing)
    assert result_missing == "FINISH"