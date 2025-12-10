# System Architecture

## Overview
The **Autonomous Content Agents** system is designed as a modular, event-driven architecture using the **Actor Model** pattern (implemented via LangGraph). It operates as a directed cyclic graph where independent agents collaborate to produce high-quality content.

## High-Level Design (Hexagonal Architecture)

The application follows the Ports and Adapters pattern to decouple business logic from infrastructure.

*   **Core (Domain):** Contains the business rules (`AgentState`, `TweetDraft`, `NewsArticle`). It has NO dependencies on external frameworks.
*   **Agents (Application):** Orchestrates the flow (`Collector`, `Editor`, `Writer`, `Critic`). Depends on Core interfaces.
*   **Services (Adapters):** Concrete implementations of external systems (`NewsFetcher`, `TwitterClient`, `LLMFactory`).

## Data Flow

```mermaid
graph TD
    RSS[RSS Feeds] -->|Raw XML| Collector
    Collector -->|List[NewsArticle]| Editor
    Editor -->|Selected Article| Writer
    
    subgraph "Reasoning Loop"
        Writer -->|Draft| Critic
        Critic -- Reject --> Writer
        Critic -- Approve --> Publisher
    end
    
    Publisher -->|API v2| X[Twitter/X]
```

## Key Components

### 1. State Management
We use a shared `AgentState` (TypedDict) passed between nodes. This allows for stateless agent execution, making the system resilient to crashes (state can be persisted/restored).

### 2. The Feedback Loop
Unlike traditional "Chain" architectures (A -> B -> C), we implement a **Cyclic Graph**. The `Critic` node acts as a quality gate. If the content fails validation (length, factuality, style), the control flow loops back to the `Writer` with explicit feedback instructions.

### 3. Multimodality
The system leverages **Google Gemma 3 (27B)** native multimodal capabilities. Images are not just attachments; they are part of the prompt context, allowing the model to "see" the news and describe it accurately.
