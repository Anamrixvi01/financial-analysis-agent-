# main.py
import os
from dotenv import load_dotenv
load_dotenv()  # must run BEFORE importing graph, so LangSmith env vars are set first

from fastapi import FastAPI
from pydantic import BaseModel
from graph import build_graph

app = FastAPI(title="Multi-Agent Financial Analysis API")

# Compile the graph once at startup, reused across requests
compiled_graph = build_graph()


class AnalyzeRequest(BaseModel):
    ticker: str


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/debug-av-key")
def debug_av_key():
    key = os.getenv("ALPHA_VANTAGE_API_KEY")
    return {
        "key_present": bool(key),
        "key_length": len(key) if key else 0,
        "key_last_4": key[-4:] if key else None,
    }

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    ticker = request.ticker.upper()

    initial_state = {
        "messages":     [],
        "ticker":       ticker,
        "company_name": "",
        "raw_data":     {},
        "analysis":     {},
        "report_draft": "",
        "final_report": "",
        "risk_flags":   [],
        "next_agent":   "data_fetcher",
    }

    final_state = compiled_graph.invoke(initial_state)

    return {
        "ticker":       ticker,
        "final_report": final_state.get("final_report"),
        "risk_flags":   final_state.get("risk_flags"),
    }