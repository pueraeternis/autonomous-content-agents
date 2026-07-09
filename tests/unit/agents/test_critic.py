import pytest

from content_agents.agents.critic import critic_node
from content_agents.core.config import settings
from content_agents.schemas.data_types import TweetDraft
from tests.helpers import create_initial_state


@pytest.mark.unit
def test_critic_rejects_missing_draft() -> None:
    state = create_initial_state(draft=None)

    update = critic_node(state)

    assert update["critique_history"]
    assert update["critique_history"][0].is_approved is False
    assert update["termination_reason"] == "writer_failed"


@pytest.mark.unit
def test_critic_sets_max_iterations_when_rejected_at_cap() -> None:
    overlong = "x" * (settings.twitter_max_length + 1)
    draft = TweetDraft(content=overlong, reasoning="too long")
    state = create_initial_state(draft=draft, iteration_count=3)

    update = critic_node(state)

    assert update["critique_history"][0].is_approved is False
    assert update["termination_reason"] == "max_iterations"
