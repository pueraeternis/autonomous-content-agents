from unittest.mock import MagicMock, patch

import pytest

from content_agents.agents.publisher import publisher_node
from content_agents.schemas.data_types import NewsArticle, PublishResult, TweetDraft
from tests.helpers import create_initial_state


@pytest.mark.unit
def test_publisher_no_draft_sets_publish_failed() -> None:
    state = create_initial_state(draft=None)

    update = publisher_node(state)

    assert update == {"termination_reason": "publish_failed"}


@pytest.mark.unit
def test_publisher_live_failure_sets_publish_failed() -> None:
    draft = TweetDraft(content="Hello world", reasoning="test")
    article = NewsArticle(
        title="T",
        content="C",
        url="https://example.com/a",
        source="S",
        published_at="2024-01-01",
    )
    state = create_initial_state(draft=draft, selected_article=article)
    mock_result = PublishResult(mode="live", tweet_id=None, success=False)
    mock_publisher = MagicMock()
    mock_publisher.publish.return_value = mock_result

    with patch(
        "content_agents.agents.publisher.get_publisher",
        return_value=mock_publisher,
    ):
        update = publisher_node(state)

    assert update == {"termination_reason": "publish_failed"}


@pytest.mark.unit
def test_publisher_mock_mode_sets_publish_mode() -> None:
    draft = TweetDraft(content="Hello world", reasoning="test")
    article = NewsArticle(
        title="T",
        content="C",
        url="https://example.com/a",
        source="S",
        published_at="2024-01-01",
    )
    state = create_initial_state(draft=draft, selected_article=article)

    mock_result = PublishResult(mode="mock", tweet_id=None, success=True)
    mock_publisher = MagicMock()
    mock_publisher.publish.return_value = mock_result

    with (
        patch(
            "content_agents.agents.publisher.get_publisher",
            return_value=mock_publisher,
        ),
        patch("content_agents.agents.publisher.history_service.add") as mock_add,
    ):
        update = publisher_node(state)

    assert update["publish_mode"] == "mock"
    assert update["final_tweet_id"] is None
    assert update["termination_reason"] == "mock_published"
    mock_add.assert_called_once_with(article.url)


@pytest.mark.unit
def test_publisher_live_mode_sets_tweet_id() -> None:
    draft = TweetDraft(content="Hello world", reasoning="test")
    article = NewsArticle(
        title="T",
        content="C",
        url="https://example.com/b",
        source="S",
        published_at="2024-01-01",
    )
    state = create_initial_state(draft=draft, selected_article=article)

    mock_result = PublishResult(mode="live", tweet_id="12345", success=True)
    mock_publisher = MagicMock()
    mock_publisher.publish.return_value = mock_result

    with (
        patch(
            "content_agents.agents.publisher.get_publisher",
            return_value=mock_publisher,
        ),
        patch("content_agents.agents.publisher.history_service.add"),
    ):
        update = publisher_node(state)

    assert update["publish_mode"] == "live"
    assert update["final_tweet_id"] == "12345"
    assert update["termination_reason"] == "published"
