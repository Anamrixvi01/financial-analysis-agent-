"""
agents/data_fetcher.py — Data Fetcher Agent

Job: Fetch ALL financial data for the given ticker from Alpha Vantage.
     Falls back to a cached demo response if the live call fails
     and the ticker has cached data available (for reliable live demos).
     Write everything to state["raw_data"].
     Then hand off to Analyzer.
"""

import sys
import os
import json
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.alpha_vantage import (
    get_stock_price,
    get_financial_ratios,
    get_recent_news,
    get_price_history,
)

CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo_cache.json")


def _load_demo_cache():
    try:
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def data_fetcher_agent(state: dict) -> dict:
    """
    Fetches live financial data for the ticker in state.
    Falls back to cached demo data if the live price fetch fails
    and this ticker exists in demo_cache.json.
    """
    ticker = state["ticker"]
    print(f"\n[Data Fetcher] Fetching data for {ticker}...")

    price_data = get_stock_price.invoke({"ticker": ticker})
    time.sleep(1)
    ratio_data = get_financial_ratios.invoke({"ticker": ticker})
    time.sleep(1)
    news_data = get_recent_news.invoke({"ticker": ticker})
    time.sleep(1)
    history_data = get_price_history.invoke({"ticker": ticker})

    # ── Fallback: if live price fetch failed, try the demo cache ──────────────
    if "error" in price_data:
        demo_cache = _load_demo_cache()
        cached = demo_cache.get(ticker.upper())
        if cached:
            print(f"[Data Fetcher] ⚠️ Live API failed — using cached demo data for {ticker}")
            price_data, ratio_data, news_data, history_data = (
                cached["price"], cached["ratios"], cached["news"], cached["history"]
            )
        else:
            print(f"[Data Fetcher] ⚠️ Live API failed and no cached demo data for {ticker}")

    raw_data = {
        "price":    price_data,
        "ratios":   ratio_data,
        "news":     news_data,
        "history":  history_data,
    }

    print(f"[Data Fetcher] ✅ Done! Got price: ${price_data.get('current_price', 'N/A')}")

    return {
        "raw_data":     raw_data,
        "company_name": price_data.get("company_name", ticker),
        "next_agent":   "analyzer",
        "messages":     [f"Data Fetcher: Fetched all data for {ticker}"],
    }