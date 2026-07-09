"""Console publisher adapter for engineering demos."""

from content_agents.core.logger import logger
from content_agents.schemas.data_types import PublishResult


class ConsolePublisher:
    """Print approved content to stdout for local inspection."""

    def publish(self, text: str, media_urls: list[str] | None = None) -> PublishResult:
        logger.info(
            "CONSOLE PUBLISH",
            content=text,
            media_urls=media_urls or [],
        )
        print("\n--- Published Content ---")
        print(text)
        if media_urls:
            print("\nMedia URLs:")
            for url in media_urls:
                print(f"  - {url}")
        print("-------------------------\n")
        return PublishResult(mode="mock", tweet_id=None, success=True)
