from pathlib import Path

import pytest

from content_agents.services.publishers.markdown import MarkdownPublisher


@pytest.mark.unit
def test_markdown_publisher_writes_file(tmp_path: Path) -> None:
    publisher = MarkdownPublisher(output_dir=tmp_path)
    result = publisher.publish(
        "Saved to markdown",
        media_urls=["https://example.com/image.png"],
    )

    assert result.success is True
    assert result.mode == "mock"
    assert result.tweet_id is not None

    output_path = Path(result.tweet_id)
    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "Saved to markdown" in content
    assert "https://example.com/image.png" in content
