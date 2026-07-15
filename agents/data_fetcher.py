"""
agents/data_fetcher.py — Data Fetcher Agent

Job: Fetch ALL financial data for the given ticker from Alpha Vantage.
     Write everything to state["raw_data"].
     Then hand off to Analyzer.

This agent does NOT use Azure OpenAI — it just calls tools.
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.alpha_vantage import (
    get_stock_price,
    get_financial_ratios,
    get_recent_news,
    get_price_history,
)


def data_fetcher_agent(state: dict) -> dict:
    """
    Fetches live financial data for the ticker in state.
    Returns updated state with raw_data filled in.
    """
    ticker = state["ticker"]
    print(f"\n[Data Fetcher] Fetching data for {ticker}...")

    # Call all 4 Alpha Vantage tools, spaced 1 second apart to respect
    # the free tier's "1 request per second" rate limit
    price_data = get_stock_price.invoke({"ticker": ticker})
    time.sleep(1)

    ratio_data = get_financial_ratios.invoke({"ticker": ticker})
    time.sleep(1)

    news_data = get_recent_news.invoke({"ticker": ticker})
    time.sleep(1)

    history_data = get_price_history.invoke({"ticker": ticker})

    # Package everything into raw_data
    raw_data = {
        "price":    price_data,
        "ratios":   ratio_data,
        "news":     news_data,
        "history":  history_data,
    }

    print(f"[Data Fetcher] ✅ Done! Got price: ${price_data.get('current_price', 'N/A')}")

    # Return updated state fields
    return {
        "raw_data":     raw_data,
        "company_name": price_data.get("company_name", ticker),
        "next_agent":   "analyzer",
        "messages":     [f"Data Fetcher: Fetched all data for {ticker}"],
    }