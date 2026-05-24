# core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
LLM_MODEL = "meta/llama-3.1-70b-instruct"
# URL du modèle image — à vérifier/ajuster sur build.nvidia.com lors de la Task 4
IMAGE_INVOKE_URL = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-dev"


def get_api_key():
    """Récupère la clé API : .env en local, st.secrets en production."""
    key = os.getenv("NVIDIA_API_KEY")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("NVIDIA_API_KEY")
        except Exception:
            key = None
    if not key:
        raise RuntimeError(
            "Clé API NVIDIA manquante. Définis NVIDIA_API_KEY dans .env "
            "(local) ou dans les Secrets de l'app (Streamlit Cloud)."
        )
    return key
