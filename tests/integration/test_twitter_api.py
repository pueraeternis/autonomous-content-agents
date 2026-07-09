import time

import pytest
import tweepy

from content_agents.core.config import settings


@pytest.mark.integration
@pytest.mark.twitter
@pytest.mark.skipif(
    not (
        settings.twitter_api_key
        and settings.twitter_api_secret
        and settings.twitter_access_token
        and settings.twitter_access_secret
    ),
    reason="Twitter API keys missing in .env",
)
def test_twitter_post_lifecycle() -> None:
    """
    Real Integration Test for X (Twitter):
    1. Authenticate (API v2)
    2. Post a unique tweet
    3. Verify success
    4. Delete the tweet (Cleanup)
    """
    client = tweepy.Client(
        consumer_key=settings.twitter_api_key.get_secret_value(),  # type: ignore[union-attr]
        consumer_secret=settings.twitter_api_secret.get_secret_value(),  # type: ignore[union-attr]
        access_token=settings.twitter_access_token.get_secret_value(),  # type: ignore[union-attr]
        access_token_secret=settings.twitter_access_secret.get_secret_value(),  # type: ignore[union-attr]
    )

    tweet_text = f"Autonomous Agent Integration Test. Timestamp: {time.time()}"
    print(f"\nAttempting to post: {tweet_text}")

    try:
        response = client.create_tweet(text=tweet_text)
        tweet_id = response.data["id"]
        print(f"Tweet Posted! ID: {tweet_id}")
        assert tweet_id is not None
    except tweepy.TweepyException as e:
        pytest.fail(f"Failed to post tweet: {e}")

    try:
        print(f"Cleaning up (Deleting tweet {tweet_id})...")
        client.delete_tweet(tweet_id)
        print("Tweet deleted successfully.")
    except Exception as e:
        print(f"Failed to delete test tweet: {e}")
