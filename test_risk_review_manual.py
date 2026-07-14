# test_risk_review_manual.py
from agents.risk_review import risk_review_agent

fake_state = {
    "ticker": "AAPL",
    "company_name": "Apple Inc",
    "report_draft": (
        "Apple Inc (AAPL) is currently trading at $210.50. The company shows "
        "strong profit margins and a positive 6-month trend. Valuation score "
        "suggests a BUY, though the 12-month price target implies a HOLD stance "
        "given the elevated current price."
    ),
    "raw_data": {
        "ratios": {
            "pe_ratio": 29.5,
            "debt_to_equity": 45.0,
            "profit_margins": 0.26,
        }
    },
    "analysis": {
        "valuation": {"rating": "BUY"},
        "price_target": {"recommendation": "HOLD"},
    },
}

result = risk_review_agent(fake_state)
print("\n--- RISK REVIEW OUTPUT ---")
print(result)