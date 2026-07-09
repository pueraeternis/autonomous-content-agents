# Engineering Workflow

This guide is for developers working on the LangGraph workflow itself — visualization, replay, inspection, publisher adapters, and verification. End-user deployment instructions remain in the [README](../README.md).

---

## Prerequisites

- [uv](https://docs.astral.sh/uv/) for dependency management
- Local vLLM for full LLM execution (optional for unit tests)
- No Twitter credentials required for engineering demos

---

## Live Mode

Run the production workflow against live RSS feeds:

```bash
uv run python -m content_agents.main
```

Daemon mode (unchanged):

```bash
uv run python -m content_agents.main --loop --interval 3600
```

---

## Replay Mode

Replay mode executes the workflow using a saved input snapshot instead of live RSS feeds. This makes debugging and demonstrations reproducible without network access.

```bash
uv run python -m content_agents.main \
  --replay snapshots/ai_breakthrough.json \
  --publisher console
```

Replay characteristics:

- Fixed rubric and articles from the snapshot (no `feedparser` calls)
- Isolated URL history (does not modify `data/history.json`)
- LLM output may still vary between runs; input-side replay is deterministic

Failure-path demo (all articles already processed):

```bash
uv run python -m content_agents.main --replay snapshots/all_processed.json
```

---

## Snapshot Format

Snapshots live in [`snapshots/`](../snapshots/) and use version `1` of the `WorkflowSnapshot` schema.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | yes | Must be `"1"` |
| `description` | string | no | Human-readable note |
| `topic` | string | yes | Rubric name (must match a rubric in `data/sources.json`) |
| `articles` | `NewsArticle[]` | yes | Articles returned instead of live RSS |
| `processed_urls` | `string[]` | no | URLs treated as already published during replay |

Example:

```json
{
  "version": "1",
  "description": "Happy-path replay input",
  "topic": "Major Releases (Must-Know)",
  "articles": [
    {
      "title": "Breakthrough in local inference",
      "content": "Researchers announced a new technique...",
      "url": "https://example.com/article-ai-breakthrough",
      "source": "Tech News",
      "published_at": "2026-01-15T10:00:00+00:00",
      "image_url": null
    }
  ],
  "processed_urls": []
}
```

Validate snapshots in unit tests:

```bash
uv run pytest tests/unit/engineering/test_snapshot.py -v
```

---

## Publisher Switching

Publishing is decoupled from the workflow via a lightweight `Publisher` protocol. The workflow graph does not change when switching adapters.

| Adapter | Config | Behavior |
|-------|--------|----------|
| `twitter` (default) | `PUBLISHER=twitter` | Posts to X/Twitter; mock mode without credentials |
| `console` | `PUBLISHER=console` | Prints approved content to stdout |
| `markdown` | `PUBLISHER=markdown` | Writes to `examples/outputs/publish_<timestamp>.md` |

CLI override (one-shot):

```bash
uv run python -m content_agents.main \
  --replay snapshots/ai_breakthrough.json \
  --publisher markdown
```

Implementation: [`src/content_agents/services/publishers/`](../src/content_agents/services/publishers/).

---

## Workflow Visualization

Generate the workflow graph from the compiled LangGraph (not hand-maintained):

```bash
uv run aca-visualize
```

Output: [`docs/assets/workflow.mmd`](assets/workflow.mmd)

Optional PNG (best-effort; may fail without render dependencies):

```bash
uv run aca-visualize --png docs/assets/workflow.png
```

CI verifies the committed Mermaid file stays in sync with the compiled graph.

The generated diagram shows actual conditional edges from LangGraph. Router semantics (e.g. "articles found") are documented in prose in [ARCHITECTURE.md](ARCHITECTURE.md), not as edge labels in the graph.

---

## Workflow Inspection

Stream per-node state updates during execution:

```bash
uv run python -m content_agents.main \
  --replay snapshots/ai_breakthrough.json \
  --publisher console \
  --inspect
```

This uses `app.stream(stream_mode="updates")` and logs each node transition. It is a lightweight inspection aid — not a tracing or observability stack.

---

## Console Output Sample

Example output from `--publisher console`:

```text
--- Published Content ---
Big AI news today: researchers unveiled a faster local inference stack.
-------------------------
```

---

## Testing

```bash
# Unit tests (matches CI)
uv run pytest

# Engineering-specific tests
uv run pytest tests/unit/engineering/ tests/unit/services/publishers/ -v

# Full replay workflow test (mocked LLM, no network)
uv run pytest tests/unit/graph/test_replay_workflow.py -v

# Integration tests (manual; requires external services)
uv run pytest -m integration
```

---

## Verify Repository (CI Parity)

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
uv run aca-visualize
git diff --exit-code docs/assets/workflow.mmd
```

---

## Asset Regeneration

| Asset | Command |
|-------|---------|
| Workflow graph | `uv run aca-visualize` |
| Snapshot files | Edit JSON in `snapshots/`, validate with `pytest tests/unit/engineering/test_snapshot.py` |
| Example markdown output | `uv run python -m content_agents.main --replay snapshots/ai_breakthrough.json --publisher markdown` |

---

## Related Documentation

- [Architecture](ARCHITECTURE.md) — system design and state model
- [README](../README.md) — deployment and end-user setup
- [ADR 001: LangGraph](adr/001-use-langgraph.md)
- [ADR 002: vLLM](adr/002-local-inference-vllm.md)
