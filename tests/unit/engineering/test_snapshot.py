import json
from pathlib import Path

import pytest

from content_agents.engineering.snapshot import WorkflowSnapshot
from content_agents.schemas.data_types import NewsArticle


@pytest.mark.unit
def test_workflow_snapshot_round_trip(tmp_path: Path) -> None:
    snapshot = WorkflowSnapshot(
        description="test snapshot",
        topic="Major Releases (Must-Know)",
        articles=[
            NewsArticle(
                title="Test",
                content="Body",
                url="https://example.com/a",
                source="Example",
                published_at="2026-01-01T00:00:00+00:00",
            )
        ],
        processed_urls=["https://example.com/old"],
    )
    path = tmp_path / "snapshot.json"
    snapshot.save(path)

    loaded = WorkflowSnapshot.load(path)
    assert loaded == snapshot


@pytest.mark.unit
def test_committed_snapshots_validate() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    for name in ("ai_breakthrough.json", "all_processed.json"):
        snapshot = WorkflowSnapshot.load(repo_root / "snapshots" / name)
        assert snapshot.version == "1"
        assert snapshot.topic
        assert isinstance(snapshot.articles, list)

    happy_path = WorkflowSnapshot.load(repo_root / "snapshots" / "ai_breakthrough.json")
    assert "editor" in happy_path.llm_outputs
    assert "writer" in happy_path.llm_outputs
    assert "critic" in happy_path.llm_outputs


@pytest.mark.unit
def test_snapshot_rejects_invalid_version(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(
        json.dumps(
            {
                "version": "2",
                "topic": "AI",
                "articles": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        WorkflowSnapshot.load(path)
