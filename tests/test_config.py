# tests/test_config.py
import importlib
import pytest
from core import config


def test_get_api_key_reads_env(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-test123")
    assert config.get_api_key() == "nvapi-test123"


def test_get_api_key_missing_raises(monkeypatch):
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="Clé API NVIDIA"):
        config.get_api_key()


def test_constants_present():
    assert config.NVIDIA_BASE_URL.startswith("https://")
    assert config.LLM_MODEL
    assert config.IMAGE_INVOKE_URL.startswith("https://")
