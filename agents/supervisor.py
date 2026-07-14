"""
agents/supervisor.py — Supervisor Agent

Job: Read next_agent from state and route to the correct agent.
     This is the traffic controller of the entire system.
     It does NOT do any analysis — it just decides who runs next.

Routing table:
    "data_fetcher" → data_fetcher_agent
    "analyzer"     → analyzer_agent
    "writer"       → writer_agent
    "risk_review"  → risk_review_agent
    "FINISH"       → END (LangGraph stops)
"""


def supervisor_agent(state: dict) -> str:
    """
    Reads next_agent from state and returns the name of the next node.
    LangGraph uses this return value to route the graph.
    """
    next_agent = state.get("next_agent", "FINISH")
    print(f"\n[Supervisor] Routing to → {next_agent}")
    return next_agent
