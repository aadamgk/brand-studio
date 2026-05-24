# core/image_client.py
import base64
import random
import requests
from core import config


def generate_image(prompt, seed=None, steps=30, timeout=60):
    """Appelle le modèle image NVIDIA. Retourne les bytes de l'image décodée."""
    if seed is None:
        seed = random.randint(0, 2**31 - 1)
    headers = {
        "Authorization": f"Bearer {config.get_api_key()}",
        "Accept": "application/json",
    }
    payload = {"prompt": prompt, "seed": seed, "steps": steps}
    response = requests.post(
        config.IMAGE_INVOKE_URL, headers=headers, json=payload, timeout=timeout
    )
    response.raise_for_status()
    body = response.json()
    artifacts = body.get("artifacts") or []
    if not artifacts or "base64" not in artifacts[0]:
        raise ValueError("Réponse image invalide : aucun artifact base64 trouvé.")
    return base64.b64decode(artifacts[0]["base64"])
