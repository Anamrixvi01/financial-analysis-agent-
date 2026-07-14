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

@app.get("/debug-env")
def debug_env():
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    return {
        "AZURE_SEARCH_ENDPOINT_raw": repr(endpoint),
        "AZURE_SEARCH_ENDPOINT_length": len(endpoint) if endpoint else 0,
        "AZURE_SEARCH_KEY_present": bool(key),
        "AZURE_SEARCH_KEY_length": len(key) if key else 0,
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