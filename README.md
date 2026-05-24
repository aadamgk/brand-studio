# 🚀 Brand Studio

Interface web qui génère une identité de marque (nom, slogan, post de lancement)
et le visuel publicitaire associé, en chaînant deux modèles via l'API **NVIDIA NIM**.

Projet individuel — Mastère Data Scientist YNOV, cours Deep Learning.

## Technologies
- **Python 3.10+**
- **Streamlit** — interface
- **NVIDIA NIM** — LLM (compatible OpenAI, via `openai`) + génération d'image (via `requests`)
- **pytest** — tests

## Installation
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
cp .env.example .env           # puis renseigner NVIDIA_API_KEY
```

## Lancer
```bash
streamlit run app.py
```

## Tests
```bash
pytest -v
```

## Architecture
- `app.py` — UI Streamlit
- `core/prompts.py` — construction des prompts (logique pure)
- `core/llm_client.py` — client LLM (streaming)
- `core/image_client.py` — client image (base64)
- `core/config.py` — config et clé API

## Hébergement
Déployé sur Streamlit Community Cloud. La clé `NVIDIA_API_KEY` est configurée
dans les *Secrets* de l'app (jamais dans le code).

## Démo
<lien vidéo à ajouter>
