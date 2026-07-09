"""Replay context for deterministic workflow execution from snapshots."""

import json
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from types import TracebackType

from content_agents.engineering.snapshot import WorkflowSnapshot
from content_agents.services.history import history_service


class ReplayContext:
    """Activate replay mode with a workflow input snapshot."""

    _active: "ReplayContext | None" = None

    def __init__(self, snapshot_path: Path | str) -> None:
        self.snapshot_path = Path(snapshot_path)
        self.snapshot = WorkflowSnapshot.load(self.snapshot_path)
        self._temp_history_file: Path | None = None
        self._previous_history_file: Path | None = None

    @classmethod
    def active(cls) -> "ReplayContext | None":
        return cls._active

    def __enter__(self) -> "ReplayContext":
        ReplayContext._active = self
        self._previous_history_file = history_service.history_file

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as temp_file:
            json.dump({"urls": self.snapshot.processed_urls}, temp_file, indent=2)
            self._temp_history_file = Path(temp_file.name)

        history_service.use_file(self._temp_history_file)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._previous_history_file is not None:
            history_service.use_file(self._previous_history_file)

        if self._temp_history_file is not None and self._temp_history_file.exists():
            self._temp_history_file.unlink()

        ReplayContext._active = None


@contextmanager
def replay_session(snapshot_path: Path | str) -> Iterator[ReplayContext]:
    with ReplayContext(snapshot_path) as context:
        yield context
