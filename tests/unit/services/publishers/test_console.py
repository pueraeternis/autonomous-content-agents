import pytest

from content_agents.schemas.data_types import PublishResult
from content_agents.services.publishers.console import ConsolePublisher


@pytest.mark.unit
def test_console_publisher_returns_success(capsys: pytest.CaptureFixture[str]) -> None:
    publisher = ConsolePublisher()
    result = publisher.publish(
        "Hello from console", media_urls=["https://example.com/a.png"]
    )

    captured = capsys.readouterr()
    assert result == PublishResult(mode="mock", tweet_id=None, success=True)
    assert "Hello from console" in captured.out
    assert "https://example.com/a.png" in captured.out
