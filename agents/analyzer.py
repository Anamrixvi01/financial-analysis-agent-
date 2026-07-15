"""
agents/analyzer.py — Analyzer Agent

Job: Read raw_data from state → use calculator tools for precise math
     → use Azure OpenAI to interpret the numbers
     → write results to state["analysis"]

This agent uses BOTH calculator tools AND Azure OpenAI.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from tools.calculator import (
    calculate_growth_rate,
    calculate_price_target,
    calculate_valuation_score,
)
from memory import retrieve_past_reports

load_dotenv()


def get_llm():
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0,
    )


def analyzer_agent(state: dict) -> dict:
    """
    Analyzes raw financial data using calculator tools + Azure OpenAI.
    Returns updated state with analysis filled in.
    """
    raw_data     = state["raw_data"]
    ticker       = state["ticker"]
    company_name = state["company_name"]

    print(f"\n[Analyzer] Analyzing {company_name} ({ticker})...")

    # ── Guard: only abort if price data itself failed ─────────────────────────
    if "error" in raw_data.get("price", {}):
        print(f"[Analyzer] ⚠️ Could not fetch price data for {ticker}")
        return {
            "analysis": {"error": "Unable to fetch live market data for this ticker. Please try again shortly."},
            "next_agent": "FINISH",
            "messages": [f"Analyzer: Aborted — no data available for {ticker}"],
        }

    # ── Step 0: Check long-term memory for past reports ──────────────────────
    past_reports = retrieve_past_reports(ticker, top=1)
    if past_reports:
        last = past_reports[0]
        history_context = (
            f"Previous analysis on {last['date']}: "
            f"Recommendation was {last['recommendation']}."
        )
    else:
        history_context = "No prior analysis found — this is a first-time analysis."

    print(f"[Analyzer] Memory check: {history_context}")

    # ── Step 1: Extract numbers from raw_data ────────────────────────────────
    price   = raw_data["price"]
    ratios  = raw_data["ratios"]
    history = raw_data["history"]

    current_price  = price.get("current_price", 0) or 0
    previous_close = price.get("previous_close", 0) or 0
    pe_ratio       = ratios.get("pe_ratio", 0) or 0
    profit_margin  = ratios.get("profit_margins", 0) or 0
    eps            = ratios.get("eps", 0) or 0

    if not isinstance(pe_ratio, (int, float)):
        pe_ratio = 0
    if not isinstance(profit_margin, (int, float)):
        profit_margin = 0

    # ── Step 2: Use calculator tools (guaranteed precise math) ───────────────
    daily_change = calculate_growth_rate.invoke({
        "current_value":  current_price,
        "previous_value": previous_close,
    })

    price_target = calculate_price_target.invoke({
        "current_price": current_price,
        "pe_ratio":      pe_ratio,
        "eps_growth":    0.10,
    })

    revenue_growth = history.get("percentage_change", 0) or 0
    if not isinstance(revenue_growth, (int, float)):
        revenue_growth = 0

    valuation = calculate_valuation_score.invoke({
        "pe_ratio":       pe_ratio,
        "profit_margin":  profit_margin,
        "revenue_growth": revenue_growth / 100,
    })

    # ── Step 3: Ask Azure OpenAI to interpret the numbers ────────────────────
    llm = get_llm()

    interpretation = llm.invoke([
        SystemMessage(content=(
            "You are a senior financial analyst. "
            "Given the following calculated metrics, write a concise 3-sentence "
            "interpretation. Be specific with numbers. No fluff. "
            "If prior analysis history is provided, briefly note whether today's "
            "conclusion aligns with or differs from it."
        )),
        HumanMessage(content=(
            f"Company: {company_name} ({ticker})\n"
            f"Current Price: ${current_price}\n"
            f"PE Ratio: {pe_ratio}\n"
            f"Profit Margin: {profit_margin:.1%}\n"
            f"Daily Change: {daily_change.get('growth_rate_percent', 'N/A')}%\n"
            f"6-Month Trend: {history.get('percentage_change', 'N/A')}% ({history.get('trend', 'N/A')})\n"
            f"12-Month Price Target: ${price_target.get('price_target_12mo', 'N/A')}\n"
            f"Valuation Score: {valuation['valuation_score']}/100 — {valuation['rating']}\n"
            f"Recommendation: {price_target.get('recommendation', 'N/A')}\n"
            f"Historical Context: {history_context}"
        )),
    ])

    # ── Step 4: Package everything into analysis ──────────────────────────────
    analysis = {
        "daily_change":    daily_change,
        "price_target":    price_target,
        "valuation":       valuation,
        "interpretation":  interpretation.content,
        "history_context": history_context,
    }

    print(f"[Analyzer] ✅ Done! Valuation: {valuation['rating']}, Target: ${price_target.get('price_target_12mo', 'N/A')}")

    return {
        "analysis":   analysis,
        "next_agent": "writer",
        "messages":   [f"Analyzer: Completed analysis for {ticker}. Rating: {valuation['rating']}"],
    }