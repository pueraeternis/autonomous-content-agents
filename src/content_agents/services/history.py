import json
from pathlib import Path

from content_agents.core.logger import logger

DEFAULT_HISTORY_FILE = Path("data/history.json")


class HistoryManager:
    def __init__(self, history_file: Path | str = DEFAULT_HISTORY_FILE) -> None:
        self.history_file = Path(history_file)
        self.processed_urls: set[str] = set()
        self._load()

    def use_file(self, history_file: Path | str) -> None:
        """Point the manager at a different history file and reload."""
        self.history_file = Path(history_file)
        self.processed_urls = set()
        self._load()

    def _load(self) -> None:
        """Load processed URLs from disk."""
        if not self.history_file.exists():
            return

        try:
            with open(self.history_file, encoding="utf-8") as f:
                data = json.load(f)
                self.processed_urls = set(data.get("urls", []))
        except Exception as e:
            logger.warning("Failed to load history file", error=str(e))

    def _save(self) -> None:
        """Save current state to disk."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
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
