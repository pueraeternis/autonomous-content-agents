"""Publisher factory for selecting delivery adapters."""

from typing import Literal

from content_agents.core.config import settings
from content_agents.services.publishers.base import Publisher
from content_agents.services.publishers.console import ConsolePublisher
from content_agents.services.publishers.markdown import MarkdownPublisher
from content_agents.services.publishers.twitter import TwitterPublisher

PublisherName = Literal["twitter", "console", "markdown"]

_publisher_override: PublisherName | None = None
_twitter_publisher: TwitterPublisher | None = None


def set_publisher_override(name: PublisherName | None) -> None:
    """Override publisher selection for a single CLI run."""
    global _publisher_override
    _publisher_override = name


def _resolve_publisher_name() -> PublisherName:
    if _publisher_override is not None:
        return _publisher_override
    return settings.publisher


def get_publisher(name: PublisherName | None = None) -> Publisher:
    """Return the configured publisher adapter."""
    selected = name or _resolve_publisher_name()

    if selected == "console":
        return ConsolePublisher()
    if selected == "markdown":
        return MarkdownPublisher()
    if selected == "twitter":
        global _twitter_publisher
        if _twitter_publisher is None:
            _twitter_publisher = TwitterPublisher()
        return _twitter_publisher

    msg = f"Unknown publisher: {selected}"
    raise ValueError(msg)
