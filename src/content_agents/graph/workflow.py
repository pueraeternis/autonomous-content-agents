from langgraph.graph import END, StateGraph

from src.content_agents.agents.collector import collector_node
from src.content_agents.agents.critic import critic_node
from src.content_agents.agents.editor import editor_node
from src.content_agents.agents.publisher import publisher_node
from src.content_agents.agents.writer import writer_node
from src.content_agents.core.logger import logger
from src.content_agents.graph.state import AgentState

MAX_ITERATIONS = 3


def check_news_availability(state: AgentState) -> str:
    articles = state.get("articles", [])
    if articles:
        return "editor"

    if state.get("topic") == "None":
        logger.warning("🏁 No news found in any rubric. Add more sources!")
        return "end"

    logger.info("🔄 No news in this rubric. Retrying with another...")
    return "collector"


def should_publish(state: AgentState) -> str:
    critique_history = state.get("critique_history", [])
    iteration = state.get("iteration_count", 0)

    if not critique_history:
        return "critic"
    if critique_history[-1].is_approved:
        return "publisher"
    if iteration < MAX_ITERATIONS:
        return "writer"
    return "end"


workflow = StateGraph(AgentState)

workflow.add_node("collector", collector_node)
workflow.add_node("editor", editor_node)
workflow.add_node("writer", writer_node)
workflow.add_node("critic", critic_node)
workflow.add_node("publisher", publisher_node)

workflow.set_entry_point("collector")

workflow.add_conditional_edges(
    "collector",
    check_news_availability,
    {
        "editor": "editor",
        "collector": "collector",
        "end": END,
    },
)

workflow.add_edge("editor", "writer")
workflow.add_edge("writer", "critic")

workflow.add_conditional_edges(
    "critic",
    should_publish,
    {
        "writer": "writer",
        "publisher": "publisher",
        "end": END,
        "critic": "critic",
    },
)

workflow.add_edge("publisher", END)

app = workflow.compile()
