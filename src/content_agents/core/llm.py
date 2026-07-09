from langchain_openai import ChatOpenAI

from content_agents.core.config import settings
from content_agents.engineering.replay import ReplayContext
from content_agents.engineering.replay_llm import ReplayLLM


def get_llm(
    temperature: float = 0.7, *, role: str | None = None
) -> ChatOpenAI | ReplayLLM:
    """
    Return a configured LLM client connecting to our local vLLM instance.

    Args:
        temperature: Creativity of the model (0.0 to 1.0).
                     Use 0.0 for extraction/critique, 0.7+ for writing.
        role: Agent role for replay snapshots (editor, writer, critic).

    """
    replay = ReplayContext.active()
    if replay is not None and role is not None:
        outputs = replay.snapshot.llm_outputs.get(role)
        if outputs:
            return ReplayLLM(outputs, role=role)

    return ChatOpenAI(  # type: ignore[call-arg]
        model=settings.model_name,
        openai_api_key=settings.openai_api_key.get_secret_value(),
        openai_api_base=settings.openai_api_base,
        temperature=temperature,
        max_tokens=2048,
        stop=["<end_of_turn>", "<eos>"],
    )
