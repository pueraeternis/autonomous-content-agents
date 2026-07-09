from unittest.mock import MagicMock

import pytest

from content_agents.schemas.data_types import PublishResult
from content_agents.services.twitter_client import TwitterClient


@pytest.mark.unit
def test_post_tweet_mock_mode_returns_explicit_result() -> None:
    client = TwitterClient.__new__(TwitterClient)
    client.client = None

    result = client.post_tweet("hello")

    assert result == PublishResult(mode="mock", tweet_id=None, success=True)


@pytest.mark.unit
def test_post_tweet_live_failure_returns_unsuccessful_result() -> None:
    client = TwitterClient.__new__(TwitterClient)
    mock_tweepy = MagicMock()
    client.client = mock_tweepy  # type: ignore[assignment]
    mock_tweepy.create_tweet.side_effect = RuntimeError("API down")

    result = client.post_tweet("hello")

    assert result.mode == "live"
    assert result.success is False
    assert result.tweet_id is None
