"""
agents/writer.py — Report Writer Agent

Job: Read raw_data + analysis from state
     → use Azure OpenAI to write a full professional investment report
     → write to state["report_draft"]

This agent uses ONLY Azure OpenAI — no tools needed.
It's the creative agent that turns numbers into a readable report.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()


def get_llm():
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0.3,  # slight creativity for better prose
    )


def writer_agent(state: dict) -> dict:
    """
    Writes a full professional investment analysis report.
    Returns updated state with report_draft filled in.
    """
    raw_data     = state["raw_data"]
    analysis     = state["analysis"]
    ticker       = state["ticker"]
    company_name = state["company_name"]

    print(f"\n[Writer] Writing report for {company_name} ({ticker})...")

    # Extract all data for the report
    price        = raw_data["price"]
    ratios       = raw_data["ratios"]
    history      = raw_data["history"]
    news         = raw_data["news"]
    daily_change = analysis["daily_change"]
    price_target = analysis["price_target"]
    valuation    = analysis["valuation"]
    interpret    = analysis["interpretation"]

    # Format news headlines
    news_text = "\n".join([
        f"- {item.get('title', 'N/A')} ({item.get('publisher', 'N/A')})"
        for item in news[:3]
    ])

    llm = get_llm()

    report = llm.invoke([
        SystemMessage(content=(
            "You are a professional investment analyst writing a report for retail investors. "
            "Write clearly, use specific numbers, and structure the report with these exact sections:\n"
            "1. Executive Summary\n"
            "2. Current Market Position\n"
            "3. Financial Health\n"
            "4. Recent News & Sentiment\n"
            "5. Valuation & Price Target\n"
            "6. Investment Recommendation\n\n"
            "Be specific with all numbers. Write in professional but accessible language."
        )),
        HumanMessage(content=(
            f"Write a full investment analysis report for {company_name} ({ticker}).\n\n"
            f"PRICE DATA:\n"
            f"- Current Price: ${price.get('current_price', 'N/A')}\n"
            f"- Previous Close: ${price.get('previous_close', 'N/A')}\n"
            f"- Daily Change: {daily_change['growth_rate_percent']}% ({daily_change['direction']})\n"
            f"- 52-Week High: ${price.get('52_week_high', 'N/A')}\n"
            f"- 52-Week Low: ${price.get('52_week_low', 'N/A')}\n"
            f"- Market Cap: ${price.get('market_cap', 'N/A'):,}\n\n"
            f"FINANCIAL RATIOS:\n"
            f"- PE Ratio: {ratios.get('pe_ratio', 'N/A')}\n"
            f"- EPS: ${ratios.get('eps', 'N/A')}\n"
            f"- Profit Margin: {ratios.get('profit_margins', 0):.1%}\n"
            f"- Gross Margin: {ratios.get('gross_margins', 0):.1%}\n"
            f"- Return on Equity: {ratios.get('return_on_equity', 0):.1%}\n"
            f"- Dividend Yield: {ratios.get('dividend_yield', 'N/A')}\n\n"
            f"6-MONTH PERFORMANCE:\n"
            f"- Start Price: ${history.get('start_price', 'N/A')}\n"
            f"- End Price: ${history.get('end_price', 'N/A')}\n"
            f"- Change: {history.get('percentage_change', 'N/A')}% ({history.get('trend', 'N/A')})\n\n"
            f"ANALYST INTERPRETATION:\n{interpret}\n\n"
            f"VALUATION:\n"
            f"- Score: {valuation['valuation_score']}/100\n"
            f"- Rating: {valuation['rating']}\n"
            f"- 12-Month Price Target: ${price_target['price_target_12mo']}\n"
            f"- Upside: {price_target['upside_percent']}%\n"
            f"- Recommendation: {price_target['recommendation']}\n\n"
            f"RECENT NEWS:\n{news_text}"
        )),
    ])

    report_draft = report.content
    print(f"[Writer] ✅ Done! Report written ({len(report_draft)} characters)")

    return {
        "report_draft": report_draft,
        "next_agent":   "risk_review",
        "messages":     [f"Writer: Completed report draft for {ticker}"],
    }
