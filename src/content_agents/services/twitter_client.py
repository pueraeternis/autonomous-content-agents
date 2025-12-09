import tweepy

from src.content_agents.core.config import settings
from src.content_agents.core.logger import logger


class TwitterClient:
    """
    Adapter for X (Twitter) API v2.
    Handles authentication and posting logic.
    """

    def __init__(self) -> None:
        self.client = None
        self._authenticate()

    def _authenticate(self) -> None:
        """
        Authenticate using credentials from settings.
        If credentials are valid, initializes the tweepy Client.
        """
        if not (
            settings.twitter_api_key and settings.twitter_api_secret and settings.twitter_access_token and settings.twitter_access_secret
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

    def post_tweet(self, text: str, media_urls: list[str] | None = None) -> str | None:
        """
        Post a tweet.

        Args:
            text: The content of the tweet.
            media_urls: List of image URLs.

        Returns:
            str: Tweet ID if successful, None otherwise.

        """
        if not self.client:
            logger.info("MOCK PUBLISH: Credentials missing.", text_snippet=text[:50])
            return "mock-id-no-creds"

        try:
            if media_urls:
                logger.info(
                    "Media upload skipped (Twitter API Free Tier limitation)",
                    skipped_urls_count=len(media_urls),
                    urls=media_urls,
                )

            # Note: For the Free Tier, we focus on text-only posts.
            # The agent includes links in the text, so X will generate a preview card automatically.

            response = self.client.create_tweet(text=text)
            tweet_id = response.data["id"]

            logger.info("Tweet published successfully", tweet_id=tweet_id)
            return tweet_id

        except Exception as e:
            logger.error("Failed to publish tweet", error=str(e))
            return None


# Singleton instance
twitter_service = TwitterClient()
