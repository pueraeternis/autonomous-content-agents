from pathlib import Path

import pytest

from content_agents.core.llm import get_llm
from content_agents.engineering.replay import ReplayContext
from content_agents.engineering.replay_llm import ReplayLLM
from content_agents.engineering.snapshot import WorkflowSnapshot
from content_agents.schemas.data_types import NewsArticle


@pytest.mark.unit
def test_replay_llm_returns_recorded_outputs_in_order() -> None:
    llm = ReplayLLM(
        ['{"index": 0}', '{"index": 1}'],
        role="editor",
    )

    first = llm.invoke([])
    second = llm.invoke([])

    assert first.content == '{"index": 0}'
    assert second.content == '{"index": 1}'


@pytest.mark.unit
def test_replay_llm_raises_when_outputs_exhausted() -> None:
    llm = ReplayLLM(['{"index": 0}'], role="editor")
    llm.invoke([])

    with pytest.raises(RuntimeError, match="exhausted"):
        llm.invoke([])


@pytest.mark.unit
def test_get_llm_uses_snapshot_outputs_during_replay(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    WorkflowSnapshot(
        topic="AI",
        articles=[
            NewsArticle(
                title="Test",
                content="Body",
                url="https://example.com/a",
                source="Example",
                published_at="2026-01-01T00:00:00+00:00",
            )
        ],
        llm_outputs={"editor": ['{"index": 0, "reasoning": "replay"}']},
    ).save(snapshot_path)

    with ReplayContext(snapshot_path):
        llm = get_llm(temperature=0.1, role="editor")
        assert isinstance(llm, ReplayLLM)
        response = llm.invoke([])

    assert response.content == '{"index": 0, "reasoning": "replay"}'


@pytest.mark.unit
def test_get_llm_falls_back_to_live_client_without_replay() -> None:
    from langchain_openai import ChatOpenAI

    from content_agents.core.config import settings

    llm = get_llm(temperature=0.1, role="editor")
    assert isinstance(llm, ChatOpenAI)
    assert llm.model_name == settings.model_name
