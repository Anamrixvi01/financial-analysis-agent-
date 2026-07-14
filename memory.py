# memory.py
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_KEY")
index_name = "financial-reports-index"

search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(key))


def save_report(ticker: str, report_text: str, recommendation: str):
    """
    Save a completed financial report to long-term memory (Azure AI Search).
    Called by the Risk Review Agent after the final report is generated.
    """
    today = datetime.now(timezone.utc)
    doc = {
        "id": f"{ticker}_{today.strftime('%Y%m%d_%H%M%S')}",
        "ticker": ticker,
        "date": today.isoformat(),
        "report_text": report_text,
        "recommendation": recommendation,
    }
    result = search_client.upload_documents(documents=[doc])
    return result[0].succeeded


def retrieve_past_reports(ticker: str, top: int = 3):
    """
    Retrieve the most recent past reports for a given ticker.
    Called by the Analyzer Agent before running new analysis.
    Returns a list of dicts, most recent first.
    """
    results = search_client.search(
        search_text="*",
        filter=f"ticker eq '{ticker}'",
        order_by=["date desc"],
        top=top,
    )
    past_reports = []
    for r in results:
        past_reports.append({
            "date": r["date"],
            "recommendation": r["recommendation"],
            "report_text": r["report_text"],
        })
    return past_reports