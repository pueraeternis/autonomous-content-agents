from src.content_agents.core.logger import logger
from src.content_agents.graph.state import AgentState
from src.content_agents.services.news_fetcher import news_service


def collector_node(_state: AgentState) -> dict:
    """
    Collector Agent:
    1. Selects a rubric (topic) based on weights.
    2. Fetches fresh news from RSS.
    3. Updates the state with articles and the chosen topic.
    """
    logger.info("Collector Agent starting...")

    # 1. Select Rubric
    rubric = news_service.select_rubric()

    if not rubric:
        logger.warning("No rubric selected or sources file empty.")
        return {
            "articles": [],
            "topic": "General AI",
            "iteration_count": 0,
        }

    topic = rubric["rubric"]

    # 2. Fetch News
    articles = news_service.fetch_news_from_rubric(rubric)

    if not articles:
        logger.info("No fresh news found for rubric", rubric=topic)

    logger.info("Collector finished", topic=topic, articles_count=len(articles))

    # 3. Return State Update
    return {
        "topic": topic,
        "articles": articles,
        "iteration_count": 0,
        "draft": None,
        "critique_history": [],
        "final_tweet_id": None,
    }
