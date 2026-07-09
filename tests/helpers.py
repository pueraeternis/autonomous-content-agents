"""Test helpers for constructing graph state."""

from typing import cast

from content_agents.graph.state import AgentState
from content_agents.graph.state import create_initial_state as _create_initial_state

__all__ = ["AgentState", "create_initial_state", "make_initial_state"]


def create_initial_state(**overrides: object) -> AgentState:
    state = dict(_create_initial_state())
    for key, value in overrides.items():
        state[key] = value
    return cast(AgentState, state)


make_initial_state = create_initial_state
