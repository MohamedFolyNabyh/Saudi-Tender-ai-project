from langgraph.graph import END
from langgraph.graph import StateGraph

from app.graph.state import GraphState


from app.agents.rag_agent import RAGAgent
from app.agents.sql_agent import SQLAgent
from app.agents.report_agent import ReportAgent
from app.agents.risk_agent import RiskAgent
from app.agents.compare_agent import CompareAgent
from app.agents.supervisor_agent import SupervisorAgent

builder = StateGraph(GraphState)

builder.add_node(
    "supervisor",
    SupervisorAgent.run
)

builder.add_node(
    "rag",
    RAGAgent.run
)

builder.add_node(
    "sql",
    SQLAgent.run
)

builder.add_node(
    "report",
    ReportAgent.run
)

builder.add_node(
    "risk",
    RiskAgent.run
)

builder.add_node(
    "compare",
    CompareAgent.run
)

builder.set_entry_point(
    "supervisor"
)

def router(state):

    return state["intent"]


builder.add_conditional_edges(

    "supervisor",

    router,
    {
    "rag": "rag",
    "report": "report",
    "sql": "sql",
    "risk": "risk",
    "compare": "compare"
    }


)



builder.add_edge(
    "rag",
    END
)

builder.add_edge(
    "sql",
    END
)

builder.add_edge(
    "report",
    END
)


graph = builder.compile()