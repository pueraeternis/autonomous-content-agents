from src.content_agents.core.logger import logger
from src.content_agents.graph.state import AgentState
from src.content_agents.services.twitter_client import twitter_service


def publisher_node(state: AgentState) -> dict:
    """
    Publish Agent:
    Takes the approved draft and pushes it to X (Twitter).
    """
    logger.info("Publisher Agent starting...")

    draft = state.get("draft")
    if not draft:
        logger.error("No draft to publish.")
        return {}

    # Publish
    tweet_id = twitter_service.post_tweet(
        text=draft.content,
        media_urls=draft.media_files,
    )

    if tweet_id:
        logger.info("Content cycle finished successfully.", tweet_id=tweet_id)
        return {"final_tweet_id": tweet_id}
    logger.error("Publishing failed.")
    return {}
