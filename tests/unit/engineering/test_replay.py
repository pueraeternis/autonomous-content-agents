from pathlib import Path
from unittest.mock import patch

import pytest

from content_agents.agents.collector import collector_node
from content_agents.engineering.replay import ReplayContext
from content_agents.engineering.snapshot import WorkflowSnapshot
from content_agents.schemas.data_types import NewsArticle
from content_agents.services.history import history_service
from tests.helpers import create_initial_state


@pytest.mark.unit
def test_replay_context_returns_snapshot_articles(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    WorkflowSnapshot(
        topic="Major Releases (Must-Know)",
        articles=[
            NewsArticle(
                title="Replay article",
                content="Replay body",
                url="https://example.com/replay",
                source="Replay Source",
                published_at="2026-01-01T00:00:00+00:00",
            )
        ],
    ).save(snapshot_path)

    sources = [
        {
            "rubric": "Major Releases (Must-Know)",
            "weight": 1.0,
            "sources": [{"title": "Test", "feed": "https://example.com/rss"}],
        }
    ]

    with (
        ReplayContext(snapshot_path),
        patch(
            "content_agents.agents.collector.news_service.load_sources",
            return_value=sources,
        ),
    ):
        update = collector_node(create_initial_state())

    assert update["topic"] == "Major Releases (Must-Know)"
    assert len(update["articles"]) == 1
    assert update["articles"][0].url == "https://example.com/replay"


@pytest.mark.unit
def test_replay_context_uses_isolated_history(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    WorkflowSnapshot(
        topic="Major Releases (Must-Know)",
        articles=[
            NewsArticle(
                title="Processed article",
                content="Body",
                url="https://example.com/processed",
                source="Replay Source",
                published_at="2026-01-01T00:00:00+00:00",
            )
        ],
        processed_urls=["https://example.com/processed"],
    ).save(snapshot_path)

    original_file = history_service.history_file
    sources = [
        {
            "rubric": "Major Releases (Must-Know)",
            "weight": 1.0,
            "sources": [],
        }
    ]

    try:
        with ReplayContext(snapshot_path):
            assert history_service.is_processed("https://example.com/processed")
            with patch(
                "content_agents.agents.collector.news_service.load_sources",
                return_value=sources,
            ):
                update = collector_node(create_initial_state())

        assert update["articles"] == []
        assert update["topic"] == "Major Releases (Must-Know)"
    finally:
        history_service.use_file(original_file)


@pytest.mark.unit
def test_replay_second_collector_pass_terminates_no_news(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    WorkflowSnapshot(
        topic="Major Releases (Must-Know)",
        articles=[],
    ).save(snapshot_path)

    sources = [
        {
            "rubric": "Major Releases (Must-Know)",
            "weight": 1.0,
            "sources": [],
        }
    ]

    with (
        ReplayContext(snapshot_path),
        patch(
            "content_agents.agents.collector.news_service.load_sources",
            return_value=sources,
        ),
    ):
        first = collector_node(create_initial_state())
        second = collector_node(
            create_initial_state(tried_rubrics=first["tried_rubrics"])
        )

    assert second["topic"] == "None"
    assert second["termination_reason"] == "no_news"
