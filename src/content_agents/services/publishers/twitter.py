"""Twitter/X publisher adapter."""

import tweepy

from content_agents.core.config import settings
from content_agents.core.logger import logger
from content_agents.schemas.data_types import PublishResult


class TwitterPublisher:
    """Adapter for X (Twitter) API v2."""

    def __init__(self) -> None:
        self.client: tweepy.Client | None = None
        self._authenticate()

    def _authenticate(self) -> None:
        if not (
            settings.twitter_api_key
            and settings.twitter_api_secret
            and settings.twitter_access_token
            and settings.twitter_access_secret
        ):
            logger.warning("Twitter credentials missing. Client remains inactive.")
            return

        try:
            self.client = tweepy.Client(
                consumer_key=settings.twitter_api_key.get_secret_value(),
                consumer_secret=settings.twitter_api_secret.get_secret_value(),
                access_token=settings.twitter_access_token.get_secret_value(),
                access_token_secret=settings.twitter_access_secret.get_secret_value(),
            )
            logger.info("Authenticated with Twitter API v2 successfully.")
        except Exception as e:
            logger.error("Failed to authenticate with Twitter", error=str(e))
            self.client = None

    def publish(self, text: str, media_urls: list[str] | None = None) -> PublishResult:
        if not self.client:
            logger.info("MOCK PUBLISH: Credentials missing.", text_snippet=text[:50])
            return PublishResult(mode="mock", tweet_id=None, success=True)

        try:
            if media_urls:
                logger.info(
                    "Media upload skipped (Twitter API Free Tier limitation)",
                    skipped_urls_count=len(media_urls),
                    urls=media_urls,
                )

            response = self.client.create_tweet(text=text)
            tweet_id = str(response.data["id"])

            logger.info("Tweet published successfully", tweet_id=tweet_id)
            return PublishResult(mode="live", tweet_id=tweet_id, success=True)
        except Exception as e:
            logger.error("Failed to publish tweet", error=str(e))
            return PublishResult(mode="live", tweet_id=None, success=False)

    def post_tweet(
        self, text: str, media_urls: list[str] | None = None
    ) -> PublishResult:
        """Backward-compatible alias for publish()."""
        return self.publish(text=text, media_urls=media_urls)
