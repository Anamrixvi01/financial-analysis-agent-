"""
agents/risk_review.py — Risk Review Agent

Job: Read report_draft from state
     → check for risks, red flags, missing disclaimers
     → add professional disclaimers
     → write final polished report to state["final_report"]

This is the LAST agent — it's the quality gate before the report reaches the user.
"""
from memory import save_report
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
        temperature=0,
    )


def risk_review_agent(state: dict) -> dict:
    """
    Reviews the report draft for risks and adds disclaimers.
    Returns updated state with final_report and risk_flags filled in.
    """
    report_draft = state["report_draft"]
    ticker       = state["ticker"]
    company_name = state["company_name"]
    ratios       = state["raw_data"]["ratios"]
    ratios       = state["raw_data"]["ratios"]
    analysis     = state["analysis"]

    # ── Determine the official recommendation to save to memory ──────────────
    official_recommendation = analysis["price_target"]["recommendation"]

    print(f"\n[Risk Review] Reviewing report for {company_name} ({ticker})...")

    # ── Step 1: Identify risk flags automatically ─────────────────────────────
    risk_flags = []

    pe_ratio      = ratios.get("pe_ratio", 0) or 0
    debt_equity   = ratios.get("debt_to_equity", 0) or 0
    profit_margin = ratios.get("profit_margins", 0) or 0

    if pe_ratio > 40:
        risk_flags.append(f"HIGH VALUATION: PE ratio of {pe_ratio:.1f} is above 40 — stock may be overvalued")
    if debt_equity > 100:
        risk_flags.append(f"HIGH DEBT: Debt-to-equity ratio of {debt_equity:.1f} indicates significant leverage")
    if profit_margin < 0.05:
        risk_flags.append(f"LOW MARGINS: Profit margin of {profit_margin:.1%} is below 5% — thin profitability")

    # ── Step 2: Ask Azure OpenAI to finalize the report ──────────────────────
    llm = get_llm()

    risk_text = "\n".join(risk_flags) if risk_flags else "No major risk flags identified."

    final = llm.invoke([
        SystemMessage(content=(
            "You are a compliance officer and senior risk analyst. "
            "Your job is to review an investment report, add any missing risk warnings, "
            "and append a professional disclaimer at the end. "
            "Do NOT rewrite the report — keep it intact and just add a RISK FACTORS section "
            "and DISCLAIMER at the end."
        )),
        HumanMessage(content=(
            f"Review this investment report for {company_name} ({ticker}) "
            f"and add risk factors + disclaimer.\n\n"
            f"IDENTIFIED RISK FLAGS:\n{risk_text}\n\n"
            f"ORIGINAL REPORT:\n{report_draft}\n\n"
            f"Please append:\n"
            f"1. A RISK FACTORS section mentioning the identified flags above\n"
            f"2. A standard DISCLAIMER: "
            f"'This report is for informational purposes only and does not constitute "
            f"financial advice. Past performance is not indicative of future results. "
            f"Always consult a qualified financial advisor before making investment decisions.'"
        )),
    ])

    final_report = final.content
    print(f"[Risk Review] ✅ Done! Risk flags: {len(risk_flags)}. Final report ready.")

    save_report(
        ticker=ticker,
        report_text=final_report,
        recommendation=official_recommendation,
        )
    print(f"[Risk Review] 💾 Report saved to long-term memory (recommendation: {official_recommendation})")

    return {
        "final_report": final_report,
        "risk_flags":   risk_flags,
        "next_agent":   "FINISH",
        "messages":     [f"Risk Review: Report finalized for {ticker}. {len(risk_flags)} risk flags added."],
    }
