from langchain_openai import ChatOpenAI

from src.content_agents.core.config import settings


def get_llm(temperature: float = 0.7) -> ChatOpenAI:
    """
    Return a configured LLM client connecting to our local vLLM instance.

    Args:
        temperature: Creativity of the model (0.0 to 1.0).
                     Use 0.0 for extraction/critique, 0.7+ for writing.

    """
    return ChatOpenAI(
        model=settings.model_name,
        openai_api_key=settings.openai_api_key.get_secret_value(),
        openai_api_base=settings.openai_api_base,
        temperature=temperature,
        max_tokens=2048,
        stop=["<end_of_turn>", "<eos>"],
    )
