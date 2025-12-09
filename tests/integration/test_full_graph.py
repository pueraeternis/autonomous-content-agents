from src.content_agents.graph.workflow import app


def test_full_autonomous_cycle() -> None:
    """
    End-to-End Test:
    Runs the full graph. Expects the flow to move between agents.
    """
    print("\n🚀 Starting Autonomous Agent Cycle...\n")

    initial_state = {
        "topic": "",
        "articles": [],
        "draft": None,
        "critique_history": [],
        "iteration_count": 0,
        "final_tweet_id": None,
    }

    final_state = app.invoke(initial_state)

    # 1. Topic must be selected
    print(f"\n✅ Final Topic: {final_state['topic']}")
    assert final_state["topic"] != ""

    # 2. Draft must exist
    draft = final_state["draft"]
    assert draft is not None
    print(f"\n📝 Final Draft Content:\n{draft.content}")

    # 3. Critique history
    history = final_state["critique_history"]
    print(f"\n🧐 Critique Rounds: {len(history)}")

    for i, crit in enumerate(history):
        status = "✅ Approved" if crit.is_approved else "❌ Rejected"
        print(f"   Round {i + 1}: {status} (Score: {crit.score})")
        print(f"   Feedback: {crit.feedback[:100]}...")

    # 4. Iterations
    if final_state["iteration_count"] > 0:
        print(f"\n🔄 The agent rewrote the text {final_state['iteration_count']} times based on feedback.")
    else:
        print("\n✨ Perfect on the first try!")

    # Final assertion: system logic executed correctly
    if len(history) > 0:
        last_critique = history[-1]
        assert last_critique.score is not None
