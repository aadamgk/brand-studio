# tests/test_llm_client.py
from unittest.mock import MagicMock, patch
from core import llm_client


def _fake_chunk(text):
    chunk = MagicMock()
    chunk.choices[0].delta.content = text
    return chunk


@patch("core.llm_client.OpenAI")
@patch("core.llm_client.config.get_api_key", return_value="nvapi-test")
def test_generate_brand_yields_text_chunks(mock_key, mock_openai):
    fake_stream = [_fake_chunk("Bonjour "), _fake_chunk("le "), _fake_chunk("monde")]
    mock_openai.return_value.chat.completions.create.return_value = fake_stream

    messages = [{"role": "user", "content": "test"}]
    result = "".join(llm_client.generate_brand(messages))

    assert result == "Bonjour le monde"


@patch("core.llm_client.OpenAI")
@patch("core.llm_client.config.get_api_key", return_value="nvapi-test")
def test_generate_brand_skips_empty_deltas(mock_key, mock_openai):
    fake_stream = [_fake_chunk("A"), _fake_chunk(None), _fake_chunk("B")]
    mock_openai.return_value.chat.completions.create.return_value = fake_stream

    result = "".join(llm_client.generate_brand([{"role": "user", "content": "x"}]))
    assert result == "AB"
