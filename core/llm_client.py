# core/llm_client.py
from openai import OpenAI
from core import config


def _make_client():
    return OpenAI(base_url=config.NVIDIA_BASE_URL, api_key=config.get_api_key())


def generate_brand(messages, model=None, temperature=0.7):
    """Appelle le LLM NVIDIA en streaming. Génère les morceaux de texte."""
    client = _make_client()
    stream = client.chat.completions.create(
        model=model or config.LLM_MODEL,
        messages=messages,
        temperature=temperature,
        top_p=0.9,
        max_tokens=1024,
        stream=True,
    )
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
