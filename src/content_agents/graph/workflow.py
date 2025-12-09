from langgraph.graph import END, StateGraph

from src.content_agents.agents.collector import collector_node
from src.content_agents.agents.critic import critic_node
from src.content_agents.agents.writer import writer_node
from src.content_agents.core.logger import logger
from src.content_agents.graph.state import AgentState

MAX_ITERATIONS = 3


def should_publish(state: AgentState) -> str:
    """
    Conditional edge logic:
    Determines whether to publish, retry writing, or stop.
    """
    critique_history = state.get("critique_history", [])
    iteration = state.get("iteration_count", 0)

    if not critique_history:
        return "critic"

    last_critique = critique_history[-1]

    if last_critique.is_approved:
        logger.info("Draft approved! Ready to publish.")
        return "publisher"  # Placeholder (or END)

    if iteration < MAX_ITERATIONS:
        logger.info("Draft rejected. Retrying...", iteration=iteration + 1)
        return "writer"

    logger.warning("Max iterations reached. Stopping.")
    return "end"


def increment_iteration(state: AgentState) -> dict:
    return {"iteration_count": state["iteration_count"] + 1}


# --- Build the Graph ---
workflow = StateGraph(AgentState)

# Nodes
workflow.add_node("collector", collector_node)
workflow.add_node("writer", writer_node)
workflow.add_node("critic", critic_node)
# workflow.add_node("publisher", publisher_node)  # To be added later

# Entry point
workflow.set_entry_point("collector")

# Linear flow: Collector -> Writer -> Critic
workflow.add_edge("collector", "writer")
workflow.add_edge("writer", "critic")

# Conditional edges after Critic
workflow.add_conditional_edges(
    "critic",
    should_publish,
    {
        "writer": "writer",  # Retry
        "publisher": END,  # Success
        "end": END,  # Failure
    },
)

app = workflow.compile()
