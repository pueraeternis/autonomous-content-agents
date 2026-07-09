from langgraph.graph import END, StateGraph

from content_agents.agents.collector import collector_node
from content_agents.agents.critic import critic_node
from content_agents.agents.editor import editor_node
from content_agents.agents.publisher import publisher_node
from content_agents.agents.writer import writer_node
from content_agents.core.logger import logger
from content_agents.graph.constants import MAX_ITERATIONS
from content_agents.graph.state import AgentState


def check_news_availability(state: AgentState) -> str:
    articles = state.get("articles", [])
    if articles:
        return "editor"

    if state.get("topic") == "None":
        logger.warning("No news found in any rubric. Add more sources!")
        return "end"

    logger.info("No news in this rubric. Retrying with another...")
    return "collector"


def should_publish(state: AgentState) -> str:
    critique_history = state.get("critique_history", [])
    iteration = state.get("iteration_count", 0)
    draft = state.get("draft")

    if not critique_history:
        return "end"

    last = critique_history[-1]
    if last.is_approved:
        return "publisher" if draft else "end"

    if draft is None:
        return "end"

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
    },
)

workflow.add_edge("publisher", END)

app = workflow.compile()
