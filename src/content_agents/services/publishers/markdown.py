"""Markdown file publisher adapter for engineering demos."""

from datetime import UTC, datetime
from pathlib import Path

from content_agents.core.logger import logger
from content_agents.schemas.data_types import PublishResult

DEFAULT_OUTPUT_DIR = Path("examples/outputs")


class MarkdownPublisher:
    """Write approved content to a Markdown file."""

    def __init__(self, output_dir: Path | str = DEFAULT_OUTPUT_DIR) -> None:
        self.output_dir = Path(output_dir)

    def publish(self, text: str, media_urls: list[str] | None = None) -> PublishResult:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        output_path = self.output_dir / f"publish_{timestamp}.md"

        lines = ["# Published Content", "", text]
        if media_urls:
            lines.extend(["", "## Media", ""])
            lines.extend(f"- {url}" for url in media_urls)

        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        logger.info("Markdown publish complete", path=str(output_path))

        return PublishResult(mode="mock", tweet_id=str(output_path), success=True)
