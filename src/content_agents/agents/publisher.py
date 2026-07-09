from typing import Any

from content_agents.core.config import settings
from content_agents.core.logger import logger
from content_agents.graph.state import AgentState
from content_agents.services.history import history_service
from content_agents.services.publishers.factory import get_publisher


def _smart_truncate(content: str, max_length: int) -> str:
    """
    Truncate text to max_length using specific rules:
    1. Cut at the last period (.) within the limit.
    2. If no period, cut at the last comma (,) and replace with (.).
    3. If no comma, cut at the last space and add (.).
    """
    if len(content) <= max_length:
        return content

    candidate = content[:max_length]

    last_dot = candidate.rfind(".")
    if last_dot != -1:
        return candidate[: last_dot + 1]

    last_comma = candidate.rfind(",")
    if last_comma != -1:
        return candidate[:last_comma] + "."

    safe_slice = content[: max_length - 1]
    last_space = safe_slice.rfind(" ")
    if last_space != -1:
        return safe_slice[:last_space] + "."

    return content[: max_length - 1] + "."


def publisher_node(state: AgentState) -> dict[str, Any]:
    """
    Publish Agent:
    Takes the approved draft and pushes it to X (Twitter).
    Saves the processed article URL to history to prevent duplicates.
    Includes a SMART safety net for character limits.
    """
    logger.info("Publisher Agent starting...")

    draft = state.get("draft")
    article = state.get("selected_article")

    if not draft:
        logger.error("No draft to publish.")
        return {"termination_reason": "publish_failed"}

    content = draft.content
    max_len = settings.twitter_max_length

    if len(content) > max_len:
        original_len = len(content)
        content = _smart_truncate(content, max_len)

        logger.warning(
            "Draft exceeded limits. Smart truncated applied.",
            original=original_len,
            new=len(content),
            result_snippet=content[-30:],
        )

    result = get_publisher().publish(
        text=content,
        media_urls=draft.media_files,
    )

    if result.success:
        # Mark article processed on both live and mock publish to preserve dedup workflow.
        if article and article.url:
            history_service.add(article.url)
        else:
            logger.warning(
                "Published tweet but couldn't find source URL to save in history."
            )

        termination_reason = "published" if result.mode == "live" else "mock_published"
        logger.info(
            "Content cycle finished successfully.",
            mode=result.mode,
            tweet_id=result.tweet_id,
        )

        return {
            "final_tweet_id": result.tweet_id,
            "publish_mode": result.mode,
            "termination_reason": termination_reason,
        }

    logger.error("Publishing failed.")
    return {"termination_reason": "publish_failed"}
