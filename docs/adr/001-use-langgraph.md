# ADR 001: Adoption of LangGraph for Orchestration

## Status

Accepted

## Context

We needed a framework to manage multiple AI agents working together with cyclic feedback. Traditional options included:

1. **LangChain (Chains):** Good for linear sequences, bad for loops and complex routing.
2. **AutoGPT / CrewAI:** High-level abstractions, but often lack fine-grained control over state and prompts.
3. **Raw Python:** Maximum control, but requires reinventing state management and error handling.

## Decision

We chose **LangGraph** with a `StateGraph` compiled from five nodes and two conditional router functions.

The workflow uses a typed `AgentState` (`TypedDict`) with LangGraph reducers (`operator.add`) for list fields that accumulate across nodes (`tried_rubrics`, `critique_history`). Router functions (`check_news_availability`, `should_publish`) implement all branching logic explicitly.

The graph compiles without a checkpointer — each invocation starts with fresh state and runs to completion.

## Consequences

- **Positive:**
  - Native support for **cycles** (Writer–Critic loop), essential for iterative self-correction.
  - Explicit **state schema** prevents context pollution between nodes.
  - **Control:** edges and conditional logic are defined in code, not delegated to a planner.
  - Router functions are unit-testable independently of the graph.
- **Negative:**
  - Higher learning curve than standard chains.
  - Requires strict type definitions (aligns with project quality goals).
  - No built-in durable execution without adding a checkpointer (intentionally deferred).
