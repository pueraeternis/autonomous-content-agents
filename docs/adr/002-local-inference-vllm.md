# ADR 002: Local Inference via vLLM

## Status
Accepted

## Context
The system requires a high-performance LLM. We considered:
1.  **SaaS APIs (OpenAI/Anthropic):** Easy to start, but high latency and recurring costs per token. Privacy concerns with data.
2.  **Local Inference (HuggingFace Transformers):** Slow, not optimized for production throughput.
3.  **vLLM:** Optimized serving engine with PagedAttention.

## Decision
We chose **vLLM** hosting **Google Gemma 3 27B**.

## Consequences
*   **Positive:**
    *   **Privacy:** No data leaves our infrastructure.
    *   **Throughput:** vLLM provides state-of-the-art token generation speed on NVIDIA GPUs.
    *   **Cost:** Fixed infrastructure cost (GPU rental) vs variable API costs. Useful for high-volume processing.
*   **Negative:**
    *   Requires significant hardware (A100/H100 GPU) to run 27B models efficiently.
    *   Maintenance overhead of managing the Docker container.