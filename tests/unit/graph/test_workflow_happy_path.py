from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from content_agents.graph.workflow import app
from content_agents.schemas.data_types import NewsArticle, PublishResult
from tests.helpers import create_initial_state


def _mock_llm(json_body: str) -> MagicMock:
    llm = MagicMock()
    llm.invoke.return_value = MagicMock(content=json_body)
    return llm


@pytest.mark.unit
def test_workflow_completes_mock_publish_happy_path() -> None:
    article = NewsArticle(
        title="Breakthrough",
        content="Major AI advance announced today.",
        url="https://example.com/fresh",
        source="Tech News",
        published_at="2024-01-01",
    )
    sources = [
        {
            "rubric": "AI",
            "weight": 1.0,
            "sources": [{"title": "Test", "feed": "https://example.com/rss"}],
        },
    ]

    editor_llm = _mock_llm('{"index": 0, "reasoning": "Most impactful story"}')
    writer_llm = _mock_llm(
        '{"content": "Big AI news today.", "reasoning": "Strong hook", "media_files": []}'
    )
    critic_llm = _mock_llm(
        '{"score": 9, "feedback": "Ready to publish", "is_approved": true}'
    )
    publish_result = PublishResult(mode="mock", tweet_id=None, success=True)

    with (
        patch(
            "content_agents.agents.collector.news_service.load_sources",
            return_value=sources,
        ),
        patch(
            "content_agents.agents.collector.news_service.fetch_news_from_rubric",
            return_value=[article],
        ),
        patch(
            "content_agents.agents.collector.history_service.is_processed",
            return_value=False,
        ),
        patch("content_agents.agents.editor.get_llm", return_value=editor_llm),
        patch("content_agents.agents.writer.get_llm", return_value=writer_llm),
        patch(
            "content_agents.agents.writer.download_image_as_base64", return_value=None
        ),
        patch("content_agents.agents.critic.get_llm", return_value=critic_llm),
        patch(
            "content_agents.agents.publisher.twitter_service.post_tweet",
            return_value=publish_result,
        ),
        patch("content_agents.agents.publisher.history_service.add") as mock_add,
    ):
        final_state = app.invoke(cast(Any, create_initial_state()))

    assert final_state["publish_mode"] == "mock"
    assert final_state["termination_reason"] == "mock_published"
    assert final_state["final_tweet_id"] is None
    assert final_state["selected_article"] == article
    assert final_state["draft"] is not None
    assert final_state["draft"].content == "Big AI news today."
    assert final_state["iteration_count"] == 0
    assert final_state["tried_rubrics"] == ["AI"]
    assert len(final_state["critique_history"]) == 1
    assert final_state["critique_history"][0].is_approved is True
    mock_add.assert_called_once_with(article.url)
