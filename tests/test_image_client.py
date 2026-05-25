# tests/test_image_client.py
import base64
import io
from unittest.mock import MagicMock, patch
import pytest
from PIL import Image
from core import image_client


def _png_b64(color):
    """Renvoie une image PNG 8x8 unie encodée en base64 (str)."""
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), color).save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _resp_ok(b64):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"artifacts": [{"base64": b64}]}
    resp.raise_for_status.return_value = None
    return resp


@patch("core.image_client.config.get_api_key", return_value="nvapi-test")
@patch("core.image_client.requests.post")
def test_generate_image_decodes_base64(mock_post, mock_key):
    raw = b"\x89PNG fake image bytes"
    encoded = base64.b64encode(raw).decode()
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"artifacts": [{"base64": encoded}]}
    resp.raise_for_status.return_value = None
    mock_post.return_value = resp

    result = image_client.generate_image("un logo bleu")
    assert result == raw


@patch("core.image_client.config.get_api_key", return_value="nvapi-test")
@patch("core.image_client.requests.post")
def test_generate_image_raises_on_missing_artifacts(mock_post, mock_key):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"artifacts": []}
    resp.raise_for_status.return_value = None
    mock_post.return_value = resp

    with pytest.raises(ValueError, match="artifact"):
        image_client.generate_image("x")


@patch("core.image_client.config.get_api_key", return_value="nvapi-test")
@patch("core.image_client.requests.post")
def test_generate_image_forwards_explicit_seed(mock_post, mock_key):
    import base64 as _b64
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"artifacts": [{"base64": _b64.b64encode(b"x").decode()}]}
    resp.raise_for_status.return_value = None
    mock_post.return_value = resp

    image_client.generate_image("logo", seed=42)
    _, kwargs = mock_post.call_args
    assert kwargs["json"]["seed"] == 42


@patch("core.image_client.time.sleep", return_value=None)
@patch("core.image_client.config.get_api_key", return_value="nvapi-test")
@patch("core.image_client.requests.post")
def test_generate_image_retries_on_server_error(mock_post, mock_key, mock_sleep):
    err = MagicMock()
    err.status_code = 500
    ok = MagicMock()
    ok.status_code = 200
    ok.json.return_value = {"artifacts": [{"base64": base64.b64encode(b"img").decode()}]}
    ok.raise_for_status.return_value = None
    mock_post.side_effect = [err, ok]

    result = image_client.generate_image("logo", retries=3)
    assert result == b"img"
    assert mock_post.call_count == 2


@patch("core.image_client.time.sleep", return_value=None)
@patch("core.image_client.config.get_api_key", return_value="nvapi-test")
@patch("core.image_client.requests.post")
def test_generate_image_retries_on_black_then_returns_valid(mock_post, mock_key, mock_sleep):
    black = _resp_ok(_png_b64((0, 0, 0)))
    good = _resp_ok(_png_b64((200, 40, 30)))
    mock_post.side_effect = [black, good]

    result = image_client.generate_image("logo", retries=3)
    assert result == base64.b64decode(good.json.return_value["artifacts"][0]["base64"])
    assert mock_post.call_count == 2


@patch("core.image_client.time.sleep", return_value=None)
@patch("core.image_client.config.get_api_key", return_value="nvapi-test")
@patch("core.image_client.requests.post")
def test_generate_image_raises_when_always_black(mock_post, mock_key, mock_sleep):
    mock_post.return_value = _resp_ok(_png_b64((0, 0, 0)))

    with pytest.raises(ValueError, match="noire"):
        image_client.generate_image("logo", retries=2)
