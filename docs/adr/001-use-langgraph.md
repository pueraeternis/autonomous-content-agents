# ADR 001: Adoption of LangGraph for Orchestration

## Status
Accepted

## Context
We needed a framework to manage multiple AI agents working together. Traditional options included:
1.  **LangChain (Chains):** Good for linear sequences, bad for loops and complex logic.
2.  **AutoGPT / CrewAI:** High-level abstractions, but often lack fine-grained control over state and prompts.
3.  **Raw Python:** Maximum control, but requires reinventing state management and error handling.

## Decision
We chose **LangGraph**.

## Consequences
*   **Positive:**
    *   Native support for **cycles** (Writer <-> Critic loops), which are essential for self-correction.
    *   Explicit **State Schema**: We define exactly what data is passed, preventing "context pollution".
    *   **Control:** We define the edges and conditional logic (router), rather than relying on a "black box" planner.
*   **Negative:**
    *   Slightly higher learning curve than standard chains.
    *   Requires strict type definitions (which aligns with our goal of robustness).