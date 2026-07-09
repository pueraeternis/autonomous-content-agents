from pathlib import Path
from unittest.mock import patch

import pytest

from content_agents.agents.collector import collector_node
from content_agents.schemas.data_types import NewsArticle
from content_agents.services.history import history_service
from tests.helpers import create_initial_state


def _sources() -> list[dict[str, object]]:
    return [
        {
            "rubric": "AI",
            "weight": 1.0,
            "sources": [{"title": "AI Feed", "feed": "https://example.com/ai.rss"}],
        },
        {
            "rubric": "ML",
            "weight": 1.0,
            "sources": [{"title": "ML Feed", "feed": "https://example.com/ml.rss"}],
        },
    ]


@pytest.mark.unit
def test_collector_no_sources_sets_terminal_topic() -> None:
    state = create_initial_state()

    with patch(
        "content_agents.agents.collector.news_service.load_sources", return_value=[]
    ):
        update = collector_node(state)

    assert update["topic"] == "None"
    assert update["articles"] == []
    assert update["termination_reason"] == "no_news"


@pytest.mark.unit
def test_collector_retries_when_all_urls_already_processed(
    tmp_history_file: Path,
) -> None:
    stale_article = NewsArticle(
        title="Stale",
        content="C",
        url="https://example.com/stale",
        source="S",
        published_at="2024-01-01",
    )
    history_service.add(stale_article.url)

    state = create_initial_state()
    ai_rubric = _sources()[0]

    with (
        patch(
            "content_agents.agents.collector.news_service.load_sources",
            return_value=_sources(),
        ),
        patch(
            "content_agents.agents.collector.random.choices",
            return_value=[ai_rubric],
        ),
        patch(
            "content_agents.agents.collector.news_service.fetch_news_from_rubric",
            return_value=[stale_article],
        ),
    ):
        update = collector_node(state)

    assert update["articles"] == []
    assert update["topic"] == "AI"
    assert update["tried_rubrics"] == ["AI"]
    assert update.get("termination_reason") is None


@pytest.mark.unit
def test_collector_finds_fresh_articles_after_stale_rubric(
    tmp_history_file: Path,
) -> None:
    stale_article = NewsArticle(
        title="Stale",
        content="C",
        url="https://example.com/stale",
        source="S",
        published_at="2024-01-01",
    )
    fresh_article = NewsArticle(
        title="Fresh",
        content="C",
        url="https://example.com/fresh",
        source="S",
        published_at="2024-01-02",
    )
    history_service.add(stale_article.url)

    state = create_initial_state(tried_rubrics=["AI"])
    ml_rubric = _sources()[1]

    with (
        patch(
            "content_agents.agents.collector.news_service.load_sources",
            return_value=_sources(),
        ),
        patch(
            "content_agents.agents.collector.random.choices",
            return_value=[ml_rubric],
        ),
        patch(
            "content_agents.agents.collector.news_service.fetch_news_from_rubric",
            return_value=[fresh_article],
        ),
    ):
        update = collector_node(state)

    assert update["articles"] == [fresh_article]
    assert update["topic"] == "ML"
    assert update["tried_rubrics"] == ["ML"]


@pytest.mark.unit
def test_collector_exhausts_rubrics_sets_no_news() -> None:
    state = create_initial_state(tried_rubrics=["AI", "ML"])

    with patch(
        "content_agents.agents.collector.news_service.load_sources",
        return_value=_sources(),
    ):
        update = collector_node(state)

    assert update["topic"] == "None"
    assert update["articles"] == []
    assert update["termination_reason"] == "no_news"
