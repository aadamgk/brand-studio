# core/image_client.py
import base64
import io
import random
import time
import requests
from core import config


def _is_black_image(img_bytes):
    """Indique si les octets décodent une image (quasi) entièrement noire.

    FLUX.1-dev renvoie parfois une image noire (filtre de sécurité ou prompt
    pollué). Best-effort : si les octets ne sont pas décodables ici, on ne
    bloque pas (renvoie False) — la validation reste à l'appelant.
    """
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        return max(channel_max for _, channel_max in im.getextrema()) < 8
    except Exception:
        return False


def generate_image(prompt, seed=None, steps=50, width=1024, height=1024,
                   cfg_scale=3.5, timeout=90, retries=3):
    """Appelle le modèle image NVIDIA (FLUX.1-dev). Retourne les bytes décodés.

    Réessaie sur les erreurs serveur 5xx (le tier gratuit en renvoie parfois)
    et sur les images noires (en relançant avec une nouvelle seed). Lève une
    ValueError explicite si l'image reste noire après les tentatives.
    """
    headers = {
        "Authorization": f"Bearer {config.get_api_key()}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    response = None
    for attempt in range(retries):
        payload = {
            "prompt": prompt,
            "mode": "base",
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "seed": seed if seed is not None else random.randint(0, 2**31 - 1),
            "steps": steps,
        }
        response = requests.post(
            config.IMAGE_INVOKE_URL, headers=headers, json=payload, timeout=timeout
        )
        if response.status_code >= 500 and attempt < retries - 1:
            time.sleep(2)
            continue
        response.raise_for_status()
        body = response.json()
        artifacts = body.get("artifacts") or []
        if not artifacts or "base64" not in artifacts[0]:
            raise ValueError("Réponse image invalide : aucun artifact base64 trouvé.")
        img_bytes = base64.b64decode(artifacts[0]["base64"])
        if _is_black_image(img_bytes) and attempt < retries - 1:
            time.sleep(1)
            continue
        if _is_black_image(img_bytes):
            raise ValueError(
                "Le modèle a renvoyé une image noire. Réessaie ou ajuste la "
                "description du produit."
            )
        return img_bytes
    response.raise_for_status()
    raise ValueError("Échec de génération de l'image après plusieurs tentatives.")
