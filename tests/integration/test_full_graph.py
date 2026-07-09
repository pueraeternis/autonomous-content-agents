from typing import Any, cast

import pytest

from content_agents.graph.workflow import app
from tests.helpers import create_initial_state


@pytest.mark.integration
@pytest.mark.network
@pytest.mark.vllm
@pytest.mark.slow
def test_full_autonomous_cycle() -> None:
    """
    End-to-End Test:
    Runs the full graph. Expects the flow to move between agents.
    """
    print("\nStarting Autonomous Agent Cycle...\n")

    final_state = app.invoke(cast(Any, create_initial_state()))

    print(f"\nFinal Topic: {final_state['topic']}")
    assert final_state["topic"] != ""

    draft = final_state["draft"]
    assert draft is not None
    print(f"\nFinal Draft Content:\n{draft.content}")

    history = final_state["critique_history"]
    print(f"\nCritique Rounds: {len(history)}")

    for i, crit in enumerate(history):
        status = "Approved" if crit.is_approved else "Rejected"
        print(f"   Round {i + 1}: {status} (Score: {crit.score})")
        print(f"   Feedback: {crit.feedback[:100]}...")

    if final_state["iteration_count"] > 0:
        print(
            f"\nThe agent rewrote the text {final_state['iteration_count']} times based on feedback."
        )
    else:
        print("\nPerfect on the first try!")

    if len(history) > 0:
        last_critique = history[-1]
        assert last_critique.score is not None

    publish_mode = final_state.get("publish_mode")
    if publish_mode == "live":
        assert final_state.get("final_tweet_id")
    elif publish_mode == "mock":
        assert final_state.get("final_tweet_id") is None
        assert final_state.get("termination_reason") == "mock_published"
