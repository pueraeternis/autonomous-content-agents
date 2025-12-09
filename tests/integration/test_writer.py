import pytest

from src.content_agents.agents.collector import collector_node
from src.content_agents.agents.writer import writer_node
from src.content_agents.schemas.data_types import TweetDraft


def test_writer_flow() -> None:
    """
    Full flow test: Collector -> Writer.
    Checks if Gemma 3 can generate a structured JSON draft from real news.
    """
    state = {
        "topic": "",
        "articles": [],
        "draft": None,
        "critique_history": [],
        "iteration_count": 0,
        "final_tweet_id": None,
    }

    state_after_collect = collector_node(state)

    if not state_after_collect["articles"]:
        pytest.skip("No articles found to test writer.")

    update = writer_node(state_after_collect)
    draft = update.get("draft")

    assert draft is not None, "Writer returned None draft"
    assert isinstance(draft, TweetDraft), "Result is not a TweetDraft Pydantic model"
    assert len(draft.content) > 10, "Tweet content is too short"  # noqa: PLR2004
    assert len(draft.reasoning) > 0, "Reasoning is missing"

    print(f"\n📝 Generated Draft:\n{draft.content}")
    print(f"\n🤔 Reasoning:\n{draft.reasoning}")
    if draft.media_files:
        print(f"\n🖼 Media attached: {draft.media_files}")
