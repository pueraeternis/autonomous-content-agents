"""Workflow input snapshot format for deterministic replay."""

import json
from pathlib import Path

from pydantic import BaseModel, Field

from content_agents.schemas.data_types import NewsArticle


class WorkflowSnapshot(BaseModel):
    """Versioned snapshot of workflow input for replay mode."""

    version: str = Field(default="1", pattern=r"^1$")
    description: str = ""
    topic: str
    articles: list[NewsArticle]
    processed_urls: list[str] = Field(default_factory=list)

    @classmethod
    def load(cls, path: Path | str) -> "WorkflowSnapshot":
        snapshot_path = Path(path)
        with open(snapshot_path, encoding="utf-8") as f:
            data = json.load(f)
        return cls.model_validate(data)

    def save(self, path: Path | str) -> None:
        snapshot_path = Path(path)
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2)
