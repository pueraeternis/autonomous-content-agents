from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

import pytest

from content_agents.engineering.replay import ReplayContext
from content_agents.graph.workflow import app
from content_agents.services.publishers.factory import set_publisher_override
from content_agents.services.publishers.markdown import MarkdownPublisher
from tests.helpers import create_initial_state


@pytest.mark.unit
def test_replay_workflow_completes_with_console_publisher() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    snapshot_path = repo_root / "snapshots" / "ai_breakthrough.json"

    set_publisher_override("console")
    try:
        with ReplayContext(snapshot_path):
            final_state = cast(Any, app.invoke(cast(Any, create_initial_state())))
    finally:
        set_publisher_override(None)

    assert final_state["termination_reason"] == "mock_published"
    assert final_state["publish_mode"] == "mock"
    assert final_state["draft"] is not None
    assert "inference stack" in final_state["draft"].content


@pytest.mark.unit
def test_replay_workflow_completes_with_markdown_publisher(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    snapshot_path = repo_root / "snapshots" / "ai_breakthrough.json"

    set_publisher_override("markdown")
    try:
        with (
            ReplayContext(snapshot_path),
            patch(
                "content_agents.agents.publisher.get_publisher",
                return_value=MarkdownPublisher(output_dir=tmp_path),
            ),
        ):
            final_state = cast(Any, app.invoke(cast(Any, create_initial_state())))
    finally:
        set_publisher_override(None)

    assert final_state["termination_reason"] == "mock_published"
    assert final_state["final_tweet_id"] is not None
    output_path = Path(final_state["final_tweet_id"])
    assert output_path.exists()
    assert "inference stack" in output_path.read_text(encoding="utf-8")
