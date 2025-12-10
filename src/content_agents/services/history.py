import json
from pathlib import Path

from src.content_agents.core.logger import logger

HISTORY_FILE = Path("data/history.json")


class HistoryManager:
    def __init__(self) -> None:
        self.processed_urls: set[str] = set()
        self._load()

    def _load(self) -> None:
        """Load processed URLs from disk."""
        if not HISTORY_FILE.exists():
            return

        try:
            with open(HISTORY_FILE, encoding="utf-8") as f:
                data = json.load(f)
                self.processed_urls = set(data.get("urls", []))
        except Exception as e:
            logger.warning("Failed to load history file", error=str(e))

    def _save(self) -> None:
        """Save current state to disk."""
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump({"urls": list(self.processed_urls)}, f, indent=2)
        except Exception as e:
            logger.error("Failed to save history", error=str(e))

    def is_processed(self, url: str) -> bool:
        """Check if the URL has already been processed."""
        return url in self.processed_urls

    def add(self, url: str) -> None:
        """Mark a URL as processed and persists to disk."""
        if url and url not in self.processed_urls:
            self.processed_urls.add(url)
            self._save()
            logger.info("URL added to history", url=url)


# Singleton
history_service = HistoryManager()
