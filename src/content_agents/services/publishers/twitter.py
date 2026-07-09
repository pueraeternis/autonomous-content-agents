"""Twitter/X publisher adapter."""

import tweepy

from content_agents.core.config import settings
from content_agents.core.logger import logger
from content_agents.schemas.data_types import PublishResult

_DIAGNOSTIC_RESPONSE_HEADERS = (
    "x-rate-limit-limit",
    "x-rate-limit-remaining",
    "x-rate-limit-reset",
    "x-transaction-id",
    "x-response-time",
    "date",
)


def _publish_error_context(exc: BaseException) -> dict[str, object]:
    context: dict[str, object] = {
        "error": str(exc),
        "exception_type": type(exc).__qualname__,
        "exception_repr": repr(exc),
    }

    response = getattr(exc, "response", None)
    if response is not None:
        context["response_status"] = getattr(response, "status_code", None) or getattr(
            response, "status", None
        )
        context["response_reason"] = getattr(response, "reason", None)

        response_body = getattr(response, "text", None)
        if not response_body:
            raw_body = getattr(response, "content", None)
            if isinstance(raw_body, bytes):
                response_body = raw_body.decode("utf-8", errors="replace")
            else:
                response_body = raw_body
        if response_body:
            context["response_body"] = response_body

        headers = getattr(response, "headers", None)
        if headers is not None:
            for header in _DIAGNOSTIC_RESPONSE_HEADERS:
                if header in headers:
                    context[f"response_header_{header.replace('-', '_')}"] = headers[
                        header
                    ]

    api_errors = getattr(exc, "api_errors", None)
    if api_errors:
        context["api_errors"] = api_errors

    api_codes = getattr(exc, "api_codes", None)
    if api_codes:
        context["api_codes"] = api_codes

    api_messages = getattr(exc, "api_messages", None)
    if api_messages:
        context["api_messages"] = api_messages

    return context


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

            response = self.client.create_tweet(text=text, user_auth=True)
            tweet_id = str(response.data["id"])

            logger.info("Tweet published successfully", tweet_id=tweet_id)
            return PublishResult(mode="live", tweet_id=tweet_id, success=True)
        except Exception as e:
            logger.error("Failed to publish tweet", **_publish_error_context(e))
            return PublishResult(mode="live", tweet_id=None, success=False)

    def post_tweet(
        self, text: str, media_urls: list[str] | None = None
    ) -> PublishResult:
        """Backward-compatible alias for publish()."""
        return self.publish(text=text, media_urls=media_urls)
