"""
tools/alpha_vantage.py — Alpha Vantage Financial Data Tool

Fetches live stock data using the official Alpha Vantage REST API.
Replaces yahoo_finance.py, which gets blocked on cloud hosts (Render, AWS)
since yfinance scrapes Yahoo's site rather than using an official API.

Same function names + return shapes as yahoo_finance.py — drop-in replacement.
"""

import os
import requests
import time
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://www.alphavantage.co/query"
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")




def _get(params: dict, retries: int = 2) -> dict:
    """Internal helper: makes the API call, retrying if rate-limited."""
    params["apikey"] = API_KEY
    for attempt in range(retries + 1):
        response = requests.get(BASE_URL, params=params, timeout=15)
        data = response.json()
        print(f"[DEBUG-AV] {params.get('function')} (attempt {attempt+1}): {data}")
        if "Information" not in data and "Note" not in data:
            return data
        if attempt < retries:
            time.sleep(15)
    return datas

@tool
def get_stock_price(ticker: str) -> dict:
    """
    Get the current stock price and basic trading info for a ticker.
    Example: get_stock_price("AAPL")
    """
    try:
        data = _get({"function": "GLOBAL_QUOTE", "symbol": ticker})
        quote = data.get("Global Quote", {})

        if not quote:
            return {"error": "No quote data returned", "ticker": ticker}

        current_price = float(quote.get("05. price", 0))
        previous_close = float(quote.get("08. previous close", 0))

        return {
            "ticker": ticker.upper(),
            "company_name": ticker.upper(),
            "current_price": current_price,
            "previous_close": previous_close,
            "52_week_high": "N/A",
            "52_week_low": "N/A",
            "market_cap": "N/A",
            "currency": "USD",
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}


@tool
def get_financial_ratios(ticker: str) -> dict:
    """
    Get key financial ratios for a ticker: PE ratio, EPS, revenue, profit margins.
    Example: get_financial_ratios("AAPL")
    """
    try:
        data = _get({"function": "OVERVIEW", "symbol": ticker})

        if not data or "Symbol" not in data:
            return {"error": "No overview data returned", "ticker": ticker}

        def safe_float(key, default=0):
            val = data.get(key, "None")
            try:
                return float(val)
            except (ValueError, TypeError):
                return default

        revenue = safe_float("RevenueTTM")

        return {
            "ticker": ticker.upper(),
            "pe_ratio": safe_float("PERatio"),
            "forward_pe": safe_float("ForwardPE"),
            "eps": safe_float("EPS"),
            "revenue": revenue,
            "gross_margins": (safe_float("GrossProfitTTM") / revenue) if revenue else 0,
            "profit_margins": safe_float("ProfitMargin"),
            "return_on_equity": safe_float("ReturnOnEquityTTM"),
            "debt_to_equity": "N/A",
            "dividend_yield": safe_float("DividendYield"),
            "company_name": data.get("Name", ticker.upper()),
            "52_week_high": safe_float("52WeekHigh"),
            "52_week_low": safe_float("52WeekLow"),
            "market_cap": safe_float("MarketCapitalization"),
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}


@tool
def get_recent_news(ticker: str) -> list:
    """
    Get recent news headlines for a ticker.
    Example: get_recent_news("AAPL")
    """
    try:
        data = _get({"function": "NEWS_SENTIMENT", "tickers": ticker, "limit": 5})
        feed = data.get("feed", [])

        if not feed:
            return [{"title": "No recent news found", "publisher": "N/A", "summary": "N/A"}]

        return [
            {
                "title": item.get("title", "N/A"),
                "publisher": item.get("source", "N/A"),
                "summary": item.get("summary", "N/A"),
            }
            for item in feed[:5]
        ]
    except Exception as e:
        return [{"error": str(e)}]


@tool
def get_price_history(ticker: str) -> dict:
    """
    Get 6-month price history for trend analysis.
    Returns start price, end price, and percentage change.
    Example: get_price_history("AAPL")
    """
    try:
        data = _get({"function": "TIME_SERIES_DAILY", "symbol": ticker, "outputsize": "full"})
        series = data.get("Time Series (Daily)", {})

        if not series:
            return {"error": "No price history found", "ticker": ticker}

        dates = sorted(series.keys())
        six_months_ago_index = max(0, len(dates) - 126)

        start_date = dates[six_months_ago_index]
        end_date = dates[-1]

        start_price = round(float(series[start_date]["4. close"]), 2)
        end_price = round(float(series[end_date]["4. close"]), 2)
        pct_change = round(((end_price - start_price) / start_price) * 100, 2)

        return {
            "ticker": ticker.upper(),
            "period": "6 months",
            "start_price": start_price,
            "end_price": end_price,
            "percentage_change": pct_change,
            "trend": "UP" if pct_change > 0 else "DOWN",
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}


# ── All tools in one list (imported by agents) ────────────────────────────────
alpha_vantage_tools = [
    get_stock_price,
    get_financial_ratios,
    get_recent_news,
    get_price_history,
]