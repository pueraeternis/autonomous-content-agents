from pathlib import Path
from unittest.mock import patch

import pytest

from content_agents.engineering.replay import ReplayContext
from content_agents.main import _execute_workflow
from content_agents.services.publishers.factory import set_publisher_override
from tests.helpers import create_initial_state


@pytest.mark.unit
def test_execute_workflow_inspect_mode_logs_node_updates() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    snapshot_path = repo_root / "snapshots" / "ai_breakthrough.json"

    set_publisher_override("console")
    try:
        with (
            patch("content_agents.main.logger.info") as mock_info,
            ReplayContext(snapshot_path),
        ):
            final_state = _execute_workflow(create_initial_state(), inspect=True)
    finally:
        set_publisher_override(None)

    assert final_state["termination_reason"] == "mock_published"
    node_update_calls = [
        call
        for call in mock_info.call_args_list
        if call.args == ("Node update",) and "workflow_update" in call.kwargs
    ]
    assert node_update_calls, "expected inspect mode to log per-node workflow updates"
    for call in node_update_calls:
        assert "event" not in call.kwargs
