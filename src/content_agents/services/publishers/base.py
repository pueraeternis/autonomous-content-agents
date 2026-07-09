"""Publisher protocol for interchangeable delivery adapters."""

from typing import Protocol

from content_agents.schemas.data_types import PublishResult


class Publisher(Protocol):
    """Lightweight interface for publishing approved content."""

    def publish(
        self, text: str, media_urls: list[str] | None = None
    ) -> PublishResult: ...
