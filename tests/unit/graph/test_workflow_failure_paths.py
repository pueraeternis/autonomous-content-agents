from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from content_agents.graph.workflow import app
from content_agents.schemas.data_types import NewsArticle
from tests.helpers import create_initial_state


@pytest.mark.unit
def test_workflow_terminates_when_no_sources() -> None:
    with patch(
        "content_agents.agents.collector.news_service.load_sources", return_value=[]
    ):
        final_state = app.invoke(cast(Any, create_initial_state()))

    assert final_state["termination_reason"] == "no_news"
    assert final_state["topic"] == "None"


@pytest.mark.unit
def test_workflow_terminates_when_writer_fails() -> None:
    article = NewsArticle(
        title="T",
        content="C",
        url="https://example.com/x",
        source="S",
        published_at="2024-01-01",
    )
    sources = [
        {
            "rubric": "AI",
            "weight": 1.0,
            "sources": [{"title": "Test", "feed": "https://example.com/rss"}],
        },
    ]

    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = Exception("LLM unavailable")

    with (
        patch(
            "content_agents.agents.collector.news_service.load_sources",
            return_value=sources,
        ),
        patch(
            "content_agents.agents.collector.news_service.fetch_news_from_rubric",
            return_value=[article],
        ),
        patch(
            "content_agents.agents.collector.history_service.is_processed",
            return_value=False,
        ),
        patch("content_agents.agents.editor.get_llm", return_value=mock_llm),
        patch("content_agents.agents.writer.get_llm", return_value=mock_llm),
        patch(
            "content_agents.agents.writer.download_image_as_base64", return_value=None
        ),
    ):
        final_state = app.invoke(cast(Any, create_initial_state()))

    assert final_state.get("draft") is None
    assert final_state.get("termination_reason") == "writer_failed"


@pytest.mark.unit
def test_workflow_terminates_at_max_iterations() -> None:
    article = NewsArticle(
        title="T",
        content="C",
        url="https://example.com/x",
        source="S",
        published_at="2024-01-01",
    )
    sources = [
        {
            "rubric": "AI",
            "weight": 1.0,
            "sources": [{"title": "Test", "feed": "https://example.com/rss"}],
        },
    ]

    editor_llm = MagicMock()
    editor_llm.invoke.return_value = MagicMock(
        content='{"index": 0, "reasoning": "Best story"}'
    )

    writer_llm = MagicMock()
    writer_llm.invoke.return_value = MagicMock(
        content='{"content": "Draft tweet", "reasoning": "Attempt", "media_files": []}'
    )

    critic_llm = MagicMock()
    critic_llm.invoke.return_value = MagicMock(
        content='{"score": 4, "feedback": "Needs work", "is_approved": false}'
    )

    with (
        patch(
            "content_agents.agents.collector.news_service.load_sources",
            return_value=sources,
        ),
        patch(
            "content_agents.agents.collector.news_service.fetch_news_from_rubric",
            return_value=[article],
        ),
        patch(
            "content_agents.agents.collector.history_service.is_processed",
            return_value=False,
        ),
        patch("content_agents.agents.editor.get_llm", return_value=editor_llm),
        patch("content_agents.agents.writer.get_llm", return_value=writer_llm),
        patch(
            "content_agents.agents.writer.download_image_as_base64", return_value=None
        ),
        patch("content_agents.agents.critic.get_llm", return_value=critic_llm),
    ):
        final_state = app.invoke(cast(Any, create_initial_state()))

    assert final_state["termination_reason"] == "max_iterations"
    assert final_state["iteration_count"] == 3
    assert final_state["critique_history"]
    assert final_state["critique_history"][-1].is_approved is False
