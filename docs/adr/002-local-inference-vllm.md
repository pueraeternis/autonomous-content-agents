# ADR 002: Local Inference via vLLM

## Status

Accepted

## Context

The system requires a high-performance LLM for three agent nodes (Editor, Writer, Critic). We considered:

1. **SaaS APIs (OpenAI/Anthropic):** Easy to start, but recurring per-token costs, latency, and privacy concerns with article content.
2. **Local Inference (HuggingFace Transformers):** Flexible, but not optimized for production throughput.
3. **vLLM:** Optimized serving engine with PagedAttention and OpenAI-compatible API.

## Decision

We chose **vLLM** hosting **Google Gemma 3 27B**, accessed via LangChain's `ChatOpenAI` client pointed at vLLM's `/v1` endpoint.

## Consequences

- **Positive:**
  - **Privacy:** article content and drafts never leave the deployment infrastructure.
  - **Throughput:** vLLM provides efficient token generation on NVIDIA GPUs.
  - **Cost:** fixed infrastructure cost (GPU) vs variable per-token API billing.
  - **Compatibility:** OpenAI-compatible API allows swapping the LangChain client without code changes.
- **Negative:**
  - Requires significant hardware (~60GB VRAM for 27B bf16).
  - Docker container maintenance for the vLLM service.
  - Model upgrades require image restarts and HF cache management.
