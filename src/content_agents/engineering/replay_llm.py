"""Recorded LLM responses for deterministic replay."""

from types import SimpleNamespace
from typing import Any


class ReplayLLM:
    """Return pre-recorded JSON responses in order during replay."""

    def __init__(self, outputs: list[str], *, role: str) -> None:
        self._outputs = outputs
        self._index = 0
        self._role = role

    def invoke(self, messages: Any) -> SimpleNamespace:
        if self._index >= len(self._outputs):
            msg = (
                f"Replay LLM for '{self._role}' exhausted "
                f"({self._index} calls, {len(self._outputs)} recorded outputs)"
            )
            raise RuntimeError(msg)
        content = self._outputs[self._index]
        self._index += 1
        return SimpleNamespace(content=content)
