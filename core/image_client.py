# core/image_client.py
import base64
import random
import time
import requests
from core import config


def generate_image(prompt, seed=None, steps=50, width=1024, height=1024,
                   cfg_scale=3.5, timeout=90, retries=3):
    """Appelle le modèle image NVIDIA (FLUX.1-dev). Retourne les bytes décodés.

    Réessaie sur les erreurs serveur 5xx (le tier gratuit en renvoie parfois).
    """
    if seed is None:
        seed = random.randint(0, 2**31 - 1)
    headers = {
        "Authorization": f"Bearer {config.get_api_key()}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "mode": "base",
        "cfg_scale": cfg_scale,
        "width": width,
        "height": height,
        "seed": seed,
        "steps": steps,
    }
    for attempt in range(retries):
        response = requests.post(
            config.IMAGE_INVOKE_URL, headers=headers, json=payload, timeout=timeout
        )
        if response.status_code >= 500 and attempt < retries - 1:
            time.sleep(2)
            continue
        break
    response.raise_for_status()
    body = response.json()
    artifacts = body.get("artifacts") or []
    if not artifacts or "base64" not in artifacts[0]:
        raise ValueError("Réponse image invalide : aucun artifact base64 trouvé.")
    return base64.b64decode(artifacts[0]["base64"])
