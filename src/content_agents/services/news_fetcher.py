import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from src.content_agents.core.logger import logger
from src.content_agents.schemas.data_types import NewsArticle


class NewsFetcherService:
    """
    Service responsible for fetching, parsing, and cleaning news from RSS feeds.
    Includes logic for weighted rubric selection.
    """

    def __init__(self, sources_path: str = "data/sources.json", time_window_hours: int = 24) -> None:
        self.sources_path = Path(sources_path)
        self.time_window_hours = time_window_hours
        self._sources_cache = None

    def _load_sources(self) -> list[dict]:
        """Load sources from JSON with caching."""
        if self._sources_cache:
            return self._sources_cache

        if not self.sources_path.exists():
            logger.error("Sources file not found", path=str(self.sources_path))
            return []

        try:
            with open(self.sources_path, encoding="utf-8") as f:
                self._sources_cache = json.load(f)
            return self._sources_cache
        except Exception as e:
            logger.error("Failed to parse sources JSON", error=str(e))
            return []

    def select_rubric(self) -> dict | None:
        """Select a rubric based on defined weights."""
        rubrics = self._load_sources()
        if not rubrics:
            return None

        weights = [r.get("weight", 1.0) for r in rubrics]
        try:
            selected = random.choices(rubrics, weights=weights, k=1)[0]
            logger.info("Rubric selected", rubric=selected["rubric"])
            return selected
        except IndexError:
            return None

    def _clean_html(self, html_content: str) -> str:
        """Remove HTML tags to save context window tokens."""
        if not html_content:
            return ""
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator="\n").strip()

    def _extract_image(self, entry: dict) -> str | None:
        """
        Attempt to find an image URL in RSS entry (media_content, enclosure, or summary).
        Crucial for Gemma 3 Multimodal capabilities.
        """
        # 1. Check 'media_content' (standard for many blogs)
        if "media_content" in entry:
            for media in entry["media_content"]:
                if "image" in media.get("type", "") or ("medium" in media and media["medium"] == "image"):
                    return media["url"]

        # 2. Check 'links' (enclosures)
        if "links" in entry:
            for link in entry["links"]:
                if link.get("rel") == "enclosure" and "image" in link.get("type", ""):
                    return link["href"]

        # 3. Last resort: parse <img> tag from summary
        if "summary" in entry:
            soup = BeautifulSoup(entry["summary"], "html.parser")
            img = soup.find("img")
            if img and img.get("src"):
                return img["src"]

        return None

    def fetch_news_from_rubric(self, rubric: dict) -> list[NewsArticle]:
        """Parse all feeds in the given rubric and filters by time."""
        articles = []
        now = datetime.now(UTC)

        for source in rubric.get("sources", []):
            feed_url = source.get("feed")
            source_name = source.get("title")

            try:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries:
                    # Parse date safely
                    published_at = None
                    # 1. Try 'published' field
                    if "published" in entry:
                        try:
                            published_at = date_parser.parse(entry.published)
                            if published_at.tzinfo is None:
                                published_at = published_at.replace(tzinfo=UTC)
                        except (ValueError, TypeError, OverflowError) as e:
                            logger.debug("Failed to parse 'published' date", error=str(e), raw=entry.get("published"))

                    # 2. Fallback to 'updated' field
                    if not published_at and "updated" in entry:
                        try:
                            published_at = date_parser.parse(entry.updated)
                            if published_at and published_at.tzinfo is None:
                                published_at = published_at.replace(tzinfo=UTC)
                        except (ValueError, TypeError, OverflowError) as e:
                            logger.debug("Failed to parse 'updated' date", error=str(e), raw=entry.get("updated"))

                    # Skip if no date or too old
                    if not published_at:
                        continue

                    if (now - published_at) > timedelta(hours=self.time_window_hours):
                        continue

                    # Extract content
                    content = self._clean_html(entry.get("summary", "") or entry.get("description", ""))

                    article = NewsArticle(
                        title=entry.get("title", "No Title"),
                        content=content[:5000],  # Limit content size
                        url=entry.get("link", ""),
                        source=source_name,
                        published_at=published_at.isoformat(),
                        image_url=self._extract_image(entry),
                    )
                    articles.append(article)

            except Exception as e:
                logger.warning("Failed to fetch feed", source=source_name, error=str(e))
                continue

        logger.info("Fetched articles", count=len(articles), rubric=rubric["rubric"])
        return articles


# Singleton instance for ease of use
news_service = NewsFetcherService()
