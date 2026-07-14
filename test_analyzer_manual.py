# test_analyzer_manual.py
from agents.analyzer import analyzer_agent
from memory import save_report

# Fake state, as if Data Fetcher already ran
fake_state = {
    "ticker": "AAPL",
    "company_name": "Apple Inc",
    "raw_data": {
        "price": {
            "current_price": 210.50,
            "previous_close": 208.30,
        },
        "ratios": {
            "pe_ratio": 29.5,
            "profit_margins": 0.26,
            "eps": 6.5,
        },
        "history": {
            "percentage_change": 12.3,
            "trend": "upward",
        },
    },
}

result = analyzer_agent(fake_state)
print("\n--- ANALYZER OUTPUT ---")
print(result)


save_report(
    ticker="AAPL",
    report_text="Test report: AAPL rated BUY at $195, strong Q2 earnings.",
    recommendation="BUY"
)
print("Fake report saved.")