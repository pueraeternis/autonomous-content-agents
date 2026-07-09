from pathlib import Path

import pytest

from content_agents.engineering.visualize import export_workflow_mermaid


@pytest.mark.unit
def test_export_workflow_mermaid_contains_nodes(tmp_path: Path) -> None:
    output_path = tmp_path / "workflow.mmd"
    mermaid = export_workflow_mermaid(output_path)

    assert output_path.exists()
    assert "collector" in mermaid
    assert "editor" in mermaid
    assert "writer" in mermaid
    assert "critic" in mermaid
    assert "publisher" in mermaid
