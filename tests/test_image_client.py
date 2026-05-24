# tests/test_image_client.py
import base64
from unittest.mock import MagicMock, patch
import pytest
from core import image_client


@patch("core.image_client.config.get_api_key", return_value="nvapi-test")
@patch("core.image_client.requests.post")
def test_generate_image_decodes_base64(mock_post, mock_key):
    raw = b"\x89PNG fake image bytes"
    encoded = base64.b64encode(raw).decode()
    resp = MagicMock()
    resp.json.return_value = {"artifacts": [{"base64": encoded}]}
    resp.raise_for_status.return_value = None
    mock_post.return_value = resp

    result = image_client.generate_image("un logo bleu")
    assert result == raw


@patch("core.image_client.config.get_api_key", return_value="nvapi-test")
@patch("core.image_client.requests.post")
def test_generate_image_raises_on_missing_artifacts(mock_post, mock_key):
    resp = MagicMock()
    resp.json.return_value = {"artifacts": []}
    resp.raise_for_status.return_value = None
    mock_post.return_value = resp

    with pytest.raises(ValueError, match="artifact"):
        image_client.generate_image("x")
