import random

from src.content_agents.core.logger import logger
from src.content_agents.graph.state import AgentState
from src.content_agents.services.news_fetcher import news_service


def collector_node(state: AgentState) -> dict:
    """
    Collector Agent:
    Finds a rubric that hasn't been checked yet and fetches news.
    """
    logger.info("Collector Agent looking for fresh sources...")

    all_sources = news_service.load_sources()
    if not all_sources:
        return {"articles": []}

    tried = state.get("tried_rubrics", [])
    available_rubrics = [r for r in all_sources if r["rubric"] not in tried]

    if not available_rubrics:
        logger.warning("All rubrics checked. No news found.")
        return {"articles": [], "topic": "None"}

    weights = [r.get("weight", 1.0) for r in available_rubrics]
    selected_rubric = random.choices(available_rubrics, weights=weights, k=1)[0]
    topic = selected_rubric["rubric"]

    logger.info("Checking rubric", rubric=topic)

    articles = news_service.fetch_news_from_rubric(selected_rubric)

    return {
        "topic": topic,
        "articles": articles,
        "tried_rubrics": [topic],
        "selected_article": None,
        "draft": None,
        "critique_history": [],
        "iteration_count": 0,
    }
