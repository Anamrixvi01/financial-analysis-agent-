"""
tools/yahoo_finance.py — Yahoo Finance Tool

Fetches live stock data for any ticker using yfinance.
This is what gives our agents REAL data instead of hallucinated numbers.

The @tool decorator turns each function into a LangChain tool
that agents can call by name.
"""

import yfinance as yf
import requests
from langchain_core.tools import tool


def get_yf_session():
    """
    Returns a requests session with a realistic browser User-Agent.
    Yahoo Finance sometimes blocks requests from cloud/datacenter IPs
    (like Render, AWS) that don't look like a real browser.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    })
    return session


@tool
def get_stock_price(ticker: str) -> dict:
    """
    Get the current stock price and basic trading info for a ticker.
    Example: get_stock_price("AAPL")
    """
    try:
        stock = yf.Ticker(ticker, session=get_yf_session())
        info = stock.info

        return {
            "ticker": ticker.upper(),
            "company_name": info.get("longName", "N/A"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice", "N/A"),
            "previous_close": info.get("previousClose", "N/A"),
            "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "currency": info.get("currency", "USD"),
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
        stock = yf.Ticker(ticker, session=get_yf_session())
        info = stock.info

        return {
            "ticker": ticker.upper(),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "forward_pe": info.get("forwardPE", "N/A"),
            "eps": info.get("trailingEps", "N/A"),
            "revenue": info.get("totalRevenue", "N/A"),
            "gross_margins": info.get("grossMargins", "N/A"),
            "profit_margins": info.get("profitMargins", "N/A"),
            "return_on_equity": info.get("returnOnEquity", "N/A"),
            "debt_to_equity": info.get("debtToEquity", "N/A"),
            "dividend_yield": info.get("dividendYield", "N/A"),
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}


@tool
def get_recent_news(ticker: str) -> list:
    """
    Get the 5 most recent news headlines for a ticker.
    Example: get_recent_news("AAPL")
    """
    try:
        stock = yf.Ticker(ticker, session=get_yf_session())
        news = stock.news[:5]  # latest 5 articles

        return [
            {
                "title": item.get("content", {}).get("title", "N/A"),
                "publisher": item.get("content", {}).get("provider", {}).get("displayName", "N/A"),
                "summary": item.get("content", {}).get("summary", "N/A"),
            }
            for item in news
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
        stock = yf.Ticker(ticker, session=get_yf_session())
        hist = stock.history(period="6mo")

        if hist.empty:
            return {"error": "No price history found"}

        start_price = round(hist["Close"].iloc[0], 2)
        end_price = round(hist["Close"].iloc[-1], 2)
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
yahoo_finance_tools = [
    get_stock_price,
    get_financial_ratios,
    get_recent_news,
    get_price_history,
]