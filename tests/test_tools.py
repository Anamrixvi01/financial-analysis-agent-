"""
tests/test_tools.py — Test Yahoo Finance + Calculator tools

Run this to see REAL live stock data flowing through your tools.
Usage: python tests/test_tools.py

You should see real numbers for AAPL — price, PE ratio, news headlines.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.yahoo_finance import get_stock_price, get_financial_ratios, get_recent_news, get_price_history
from tools.calculator import calculate_growth_rate, calculate_price_target, calculate_valuation_score


def test_yahoo_finance():
    print("\n" + "="*50)
    print("  YAHOO FINANCE TOOLS TEST")
    print("="*50)

    # Test 1 — Stock Price
    print("\n📈 Stock Price (AAPL):")
    result = get_stock_price.invoke({"ticker": "AAPL"})
    for k, v in result.items():
        print(f"   {k}: {v}")

    # Test 2 — Financial Ratios
    print("\n📊 Financial Ratios (AAPL):")
    result = get_financial_ratios.invoke({"ticker": "AAPL"})
    for k, v in result.items():
        print(f"   {k}: {v}")

    # Test 3 — Recent News
    print("\n📰 Recent News (AAPL):")
    result = get_recent_news.invoke({"ticker": "AAPL"})
    for i, article in enumerate(result, 1):
        print(f"   {i}. {article.get('title', 'N/A')} — {article.get('publisher', 'N/A')}")

    # Test 4 — Price History
    print("\n📉 6-Month Price History (AAPL):")
    result = get_price_history.invoke({"ticker": "AAPL"})
    for k, v in result.items():
        print(f"   {k}: {v}")


def test_calculator():
    print("\n" + "="*50)
    print("  CALCULATOR TOOLS TEST")
    print("="*50)

    # Test 1 — Growth Rate
    print("\n🧮 Growth Rate (100 → 150):")
    result = calculate_growth_rate.invoke({"current_value": 150.0, "previous_value": 100.0})
    for k, v in result.items():
        print(f"   {k}: {v}")

    # Test 2 — Price Target
    print("\n🎯 Price Target:")
    result = calculate_price_target.invoke({
        "current_price": 180.0,
        "pe_ratio": 28.0,
        "eps_growth": 0.12
    })
    for k, v in result.items():
        print(f"   {k}: {v}")

    # Test 3 — Valuation Score
    print("\n⭐ Valuation Score:")
    result = calculate_valuation_score.invoke({
        "pe_ratio": 28.0,
        "profit_margin": 0.25,
        "revenue_growth": 0.08
    })
    for k, v in result.items():
        print(f"   {k}: {v}")


if __name__ == "__main__":
    test_yahoo_finance()
    test_calculator()
    print("\n✅ All tools working!\n")
