import pytest

from content_agents.agents.collector import collector_node
from content_agents.agents.writer import writer_node
from content_agents.schemas.data_types import TweetDraft
from tests.helpers import create_initial_state


@pytest.mark.integration
@pytest.mark.network
@pytest.mark.vllm
def test_writer_flow() -> None:
    """
    Full flow test: Collector -> Writer.
    Checks if Gemma 3 can generate a structured JSON draft from real news.
    """
    collected = collector_node(create_initial_state())

    if not collected.get("articles"):
        pytest.skip("No articles found to test writer.")

    state_after_collect = create_initial_state(
        topic=collected["topic"],
        articles=collected["articles"],
        tried_rubrics=collected.get("tried_rubrics", []),
        selected_article=collected["articles"][0],
    )
    update = writer_node(state_after_collect)
    draft = update.get("draft")

    assert draft is not None, "Writer returned None draft"
    assert isinstance(draft, TweetDraft), "Result is not a TweetDraft Pydantic model"
    assert len(draft.content) > 10, "Tweet content is too short"  # noqa: PLR2004
    assert len(draft.reasoning) > 0, "Reasoning is missing"

    print(f"\nGenerated Draft:\n{draft.content}")
    print(f"\nReasoning:\n{draft.reasoning}")
    if draft.media_files:
        print(f"\nMedia attached: {draft.media_files}")
