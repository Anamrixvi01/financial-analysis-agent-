# Multi-Agent Financial Analysis System

A production-grade multi-agent AI system that generates professional investment analysis reports using real live financial data.

## What It Does
- Accepts a stock ticker (e.g. AAPL, MSFT, TSLA)
- Fetches live financial data via Yahoo Finance
- Runs 4 specialized AI agents in sequence via LangGraph
- Generates a professional investment analysis report
- Accessible via FastAPI REST endpoint

## Architecture

```
User → FastAPI → LangGraph Supervisor
                       ↓
              ┌─────────────────────┐
              │  Data Fetcher Agent │ ← Yahoo Finance tools
              │  Analyzer Agent     │ ← Calculator tools + LLM
              │  Writer Agent       │ ← Generates report prose
              │  Risk Review Agent  │ ← Adds disclaimers + QA
              └─────────────────────┘
                       ↓
                 Final Report → User
```

## Tech Stack
| Component | Technology |
|---|---|
| Orchestration | LangGraph (supervisor pattern) |
| LLM | Azure OpenAI gpt-4o |
| Financial data | yfinance (Yahoo Finance) |
| Long-term memory | Azure AI Search |
| Tracing | LangSmith |
| API | FastAPI |
| Deployment | Render.com |

## Setup

```bash
# 1. Clone and install
git clone https://github.com/Anamrixvi01/financial-analysis-agent
cd financial-analysis-agent
pip install -r requirements.txt

# 2. Configure environment
cp .env.template .env
# Fill in your Azure OpenAI + Azure AI Search + LangSmith keys

# 3. Test connection
python test_connection.py

# 4. Run the API
uvicorn main:app --reload

# 5. Analyze a stock
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

## Project Structure
```
financial-analysis-agent/
├── main.py              ← FastAPI entry point
├── graph.py             ← LangGraph StateGraph
├── state.py             ← Shared TypedDict state
├── memory.py            ← Checkpointer + Azure AI Search
├── agents/
│   ├── supervisor.py
│   ├── data_fetcher.py
│   ├── analyzer.py
│   ├── writer.py
│   └── risk_review.py
├── tools/
│   ├── yahoo_finance.py
│   └── calculator.py
├── tests/
│   ├── test_tools.py
│   └── test_graph.py
├── requirements.txt
└── .env.template
```

## Live Demo
🔗 [Live URL — coming after deployment]

## Portfolio
Built as Project 2 in an AI Engineering curriculum. Project 1: [RAG Chatbot](https://rag-chatbotrix.onrender.com)
