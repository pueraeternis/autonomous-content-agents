import pytest

from content_agents.services.publishers.console import ConsolePublisher
from content_agents.services.publishers.factory import (
    get_publisher,
    set_publisher_override,
)
from content_agents.services.publishers.markdown import MarkdownPublisher
from content_agents.services.publishers.twitter import TwitterPublisher


@pytest.mark.unit
def test_get_publisher_console() -> None:
    set_publisher_override("console")
    try:
        publisher = get_publisher()
        assert isinstance(publisher, ConsolePublisher)
    finally:
        set_publisher_override(None)


@pytest.mark.unit
def test_get_publisher_markdown() -> None:
    set_publisher_override("markdown")
    try:
        publisher = get_publisher()
        assert isinstance(publisher, MarkdownPublisher)
    finally:
        set_publisher_override(None)


@pytest.mark.unit
def test_get_publisher_twitter_reuses_singleton() -> None:
    set_publisher_override("twitter")
    try:
        first = get_publisher()
        second = get_publisher()
        assert isinstance(first, TwitterPublisher)
        assert first is second
    finally:
        set_publisher_override(None)


@pytest.mark.unit
def test_get_publisher_explicit_name_overrides_settings() -> None:
    set_publisher_override("console")
    try:
        publisher = get_publisher("markdown")
        assert isinstance(publisher, MarkdownPublisher)
    finally:
        set_publisher_override(None)
