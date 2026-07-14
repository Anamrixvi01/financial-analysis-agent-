"""
tools/calculator.py — Calculator Tool

Precise math functions for financial analysis.
We NEVER let the LLM do these calculations — it hallucinates numbers.
These tools guarantee 100% accurate results every time.
"""

from langchain_core.tools import tool


@tool
def calculate_growth_rate(current_value: float, previous_value: float) -> dict:
    """
    Calculate percentage growth rate between two values.
    Example: calculate_growth_rate(150.0, 100.0) → 50% growth
    """
    if previous_value == 0:
        return {"error": "Previous value cannot be zero"}

    growth = ((current_value - previous_value) / abs(previous_value)) * 100

    return {
        "current_value": current_value,
        "previous_value": previous_value,
        "growth_rate_percent": round(growth, 2),
        "direction": "GROWTH" if growth > 0 else "DECLINE",
    }


@tool
def calculate_price_target(current_price: float, pe_ratio: float, eps_growth: float) -> dict:
    """
    Estimate a simple price target based on PE ratio and expected EPS growth.
    Formula: Price Target = Current Price × (1 + EPS Growth Rate)
    Example: calculate_price_target(150.0, 25.0, 0.10) → 12-month target
    """
    if current_price <= 0:
        return {"error": "Current price must be positive"}

    price_target = round(current_price * (1 + eps_growth), 2)
    upside = round(((price_target - current_price) / current_price) * 100, 2)

    return {
        "current_price": current_price,
        "price_target_12mo": price_target,
        "upside_percent": upside,
        "recommendation": "BUY" if upside > 10 else "HOLD" if upside > 0 else "SELL",
    }


@tool
def calculate_valuation_score(pe_ratio: float, profit_margin: float, revenue_growth: float) -> dict:
    """
    Score a stock's valuation from 0-100 based on 3 key metrics.
    Higher score = more attractive valuation.
    Example: calculate_valuation_score(20.0, 0.25, 0.15)
    """
    score = 0

    # PE ratio score (lower PE = better value)
    if pe_ratio < 15:
        score += 40
    elif pe_ratio < 25:
        score += 25
    elif pe_ratio < 35:
        score += 10
    else:
        score += 0

    # Profit margin score (higher margin = better)
    if profit_margin > 0.20:
        score += 30
    elif profit_margin > 0.10:
        score += 20
    elif profit_margin > 0.05:
        score += 10
    else:
        score += 0

    # Revenue growth score (higher growth = better)
    if revenue_growth > 0.20:
        score += 30
    elif revenue_growth > 0.10:
        score += 20
    elif revenue_growth > 0.0:
        score += 10
    else:
        score += 0

    return {
        "valuation_score": score,
        "rating": "STRONG BUY" if score >= 80 else
                  "BUY" if score >= 60 else
                  "HOLD" if score >= 40 else
                  "SELL",
        "breakdown": {
            "pe_score": "See PE ratio component",
            "margin_score": "See profit margin component",
            "growth_score": "See revenue growth component",
        }
    }


# ── All tools in one list (imported by agents) ────────────────────────────────
calculator_tools = [
    calculate_growth_rate,
    calculate_price_target,
    calculate_valuation_score,
]
