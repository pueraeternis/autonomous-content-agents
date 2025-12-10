import random

from src.content_agents.core.logger import logger
from src.content_agents.graph.state import AgentState
from src.content_agents.services.history import history_service
from src.content_agents.services.news_fetcher import news_service


def collector_node(state: AgentState) -> dict:
    """
    Collector Agent:
    Finds a rubric that hasn't been checked yet and fetches news.
    Filters out articles that have already been published (deduplication).
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

    raw_articles = news_service.fetch_news_from_rubric(selected_rubric)

    fresh_articles = [art for art in raw_articles if not history_service.is_processed(art.url)]

    if not fresh_articles:
        logger.info("All articles in this rubric were already processed.", rubric=topic)
        return {
            "topic": topic,
            "articles": [],
            "tried_rubrics": [topic],
            "selected_article": None,
            "draft": None,
            "critique_history": [],
            "iteration_count": 0,
        }

    logger.info("Found fresh articles", count=len(fresh_articles), rubric=topic)

    return {
        "topic": topic,
        "articles": fresh_articles,
        "tried_rubrics": [topic],
        "selected_article": None,
        "draft": None,
        "critique_history": [],
        "iteration_count": 0,
    }
