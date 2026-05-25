# 🚀 Brand Studio

Interface web qui génère une identité de marque (nom, slogan, post de lancement)
et le visuel publicitaire associé, en chaînant deux modèles via l'API **NVIDIA NIM**.

**🔗 Application en ligne :** https://brand-studio-gc4x2fxfnfoyp4lsjezoa7.streamlit.app/

## Technologies
- **Python 3.10+**
- **Streamlit** — interface web (thème éditorial personnalisé, mise en page en deux cartes : identité → visuel)
- **NVIDIA NIM** — accès aux modèles génératifs (API compatible OpenAI pour le texte, via `openai` ; appel REST pour l'image, via `requests`)
- **Pillow** — validation des images (garde-fou anti-image noire)

## Modèles utilisés
Les deux modèles sont servis via l'API **NVIDIA NIM** (`https://integrate.api.nvidia.com` pour le texte, `https://ai.api.nvidia.com` pour l'image) :

| Étape | Modèle | Rôle |
|-------|--------|------|
| Texte | **`meta/llama-3.1-70b-instruct`** (LLM Llama 3.1, 70 B) | Génère l'identité de marque : nom, slogan, post de lancement (réponse en streaming) |
| Image | **`black-forest-labs/flux.1-dev`** (FLUX.1-dev, text-to-image) | Compose le visuel publicitaire à partir de l'identité générée |

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

## Architecture
- `app.py` — UI Streamlit (formulaire → identité de marque en streaming → visuel publicitaire)
- `core/prompts.py` — construction des prompts (logique pure ; le prompt image est nettoyé de tout Markdown/hashtag/emoji, sinon FLUX renvoie une image noire)
- `core/llm_client.py` — client LLM (streaming)
- `core/image_client.py` — client image (décodage base64, retry sur 5xx, garde-fou anti-image noire)
- `core/config.py` — config et clé API

## Hébergement
Déployé sur **Streamlit Community Cloud** :
https://brand-studio-gc4x2fxfnfoyp4lsjezoa7.streamlit.app/

La clé `NVIDIA_API_KEY` est configurée dans les *Secrets* de l'app
(jamais dans le code).

## Démo
Vidéo de démonstration : [`docs/demo.mp4`](docs/demo.mp4)
