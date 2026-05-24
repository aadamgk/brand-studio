# Brand Studio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construire une appli Streamlit "Brand Studio" qui chaîne un LLM (identité de marque) et un modèle d'image (visuel publicitaire) via l'API NVIDIA NIM.

**Architecture:** UI Streamlit (`app.py`) qui orchestre deux clients isolés — `llm_client` (SDK `openai`, streaming) et `image_client` (`requests`, décodage base64) — pilotés par une logique de prompts pure (`prompts.py`) et une configuration centralisée (`config.py`). La clé API reste hors du code (`.env` / `st.secrets`).

**Tech Stack:** Python 3.10+, Streamlit, openai, requests, python-dotenv, pytest.

---

## File Structure

| Fichier | Responsabilité |
|---|---|
| `core/config.py` | Clé API + constantes (base_url, modèles, URL image). Aucune logique métier. |
| `core/prompts.py` | Construction des messages LLM et du prompt image. **Pure, sans réseau.** |
| `core/llm_client.py` | `generate_brand(messages) → générateur de chunks de texte`. |
| `core/image_client.py` | `generate_image(prompt) → bytes PNG`. Décode le base64. |
| `app.py` | UI Streamlit + gestion d'état. **Aucun appel API direct.** |
| `tests/test_prompts.py` | Tests de `prompts.py` (sans réseau, sans clé). |
| `tests/test_llm_client.py` | Tests de `llm_client.py` (SDK openai mocké). |
| `tests/test_image_client.py` | Tests de `image_client.py` (requests mocké). |
| `requirements.txt`, `.env.example`, `README.md` | Setup, config, doc. |

> **Note sur l'API image NVIDIA :** l'URL exacte et la forme du payload varient selon le modèle. Le plan code contre le format documenté (`artifacts[0].base64`) et garde l'URL/le modèle dans `config.py`. **À l'exécution de la Task 4, vérifier l'URL réelle sur la page du modèle (build.nvidia.com) et ajuster `IMAGE_INVOKE_URL` si besoin.**

---

## Task 1: Scaffolding du projet

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `core/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Créer `requirements.txt`**

```text
streamlit>=1.40
openai>=1.40
requests>=2.31
python-dotenv>=1.0
pytest>=8.0
```

- [ ] **Step 2: Créer `.env.example`**

```text
# Copie ce fichier en .env et remplace par ta vraie clé NVIDIA (jamais commitée)
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

- [ ] **Step 3: Créer les packages Python vides**

Créer `core/__init__.py` (contenu vide) et `tests/__init__.py` (contenu vide).

- [ ] **Step 4: Créer et activer l'environnement, installer les dépendances**

Run (PowerShell) :
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```
Expected: installation sans erreur, `pytest --version` fonctionne.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .env.example core/__init__.py tests/__init__.py
git commit -m "chore: project scaffolding and dependencies"
```

---

## Task 2: Configuration (`config.py`)

**Files:**
- Create: `core/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Écrire le test qui échoue**

```python
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
```

- [ ] **Step 2: Lancer le test pour vérifier l'échec**

Run: `pytest tests/test_config.py -v`
Expected: FAIL (`AttributeError: module 'core.config' has no attribute 'get_api_key'`)

- [ ] **Step 3: Écrire l'implémentation minimale**

```python
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
```

- [ ] **Step 4: Lancer le test pour vérifier le succès**

Run: `pytest tests/test_config.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add core/config.py tests/test_config.py
git commit -m "feat: centralized config with API key loading"
```

---

## Task 3: Logique de prompts (`prompts.py`) — le cœur

**Files:**
- Create: `core/prompts.py`
- Test: `tests/test_prompts.py`

- [ ] **Step 1: Écrire les tests qui échouent**

```python
# tests/test_prompts.py
from core import prompts


def test_build_brand_prompt_structure():
    brief = {"produit": "casque audio", "secteur": "tech",
             "ton": "premium", "public_cible": "jeunes pros"}
    messages = prompts.build_brand_prompt(brief)
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


def test_build_brand_prompt_includes_brief_fields():
    brief = {"produit": "casque audio", "secteur": "tech",
             "ton": "premium", "public_cible": "jeunes pros"}
    user = prompts.build_brand_prompt(brief)[1]["content"]
    assert "casque audio" in user
    assert "tech" in user
    assert "premium" in user
    assert "jeunes pros" in user


def test_build_brand_prompt_handles_empty_optional_fields():
    brief = {"produit": "appli de méditation"}
    user = prompts.build_brand_prompt(brief)[1]["content"]
    assert "appli de méditation" in user
    assert "non précisé" in user  # secteur vide → défaut


def test_build_image_prompt_contains_style_and_brand():
    img_prompt = prompts.build_image_prompt("Marque : ZenFlow", style="minimaliste")
    assert "minimaliste" in img_prompt
    assert "ZenFlow" in img_prompt


def test_build_image_prompt_truncates_long_text():
    long_text = "x" * 2000
    img_prompt = prompts.build_image_prompt(long_text)
    assert len(img_prompt) < 1000
```

- [ ] **Step 2: Lancer les tests pour vérifier l'échec**

Run: `pytest tests/test_prompts.py -v`
Expected: FAIL (`ModuleNotFoundError` ou `AttributeError`)

- [ ] **Step 3: Écrire l'implémentation**

```python
# core/prompts.py
SYSTEM_PROMPT = (
    "Tu es un directeur de création expert en branding. À partir de la "
    "description d'un produit, tu proposes une identité de marque percutante. "
    "Réponds en français, de façon structurée, avec EXACTEMENT ces trois "
    "sections en titre Markdown :\n"
    "## Nom de marque\n## Slogan\n## Post de lancement"
)


def build_brand_prompt(brief):
    """Construit les messages (system + user) pour le LLM à partir du brief."""
    produit = (brief.get("produit") or "").strip()
    secteur = (brief.get("secteur") or "").strip()
    ton = (brief.get("ton") or "").strip()
    public = (brief.get("public_cible") or "").strip()

    user_content = (
        f"Produit / idée : {produit}\n"
        f"Secteur : {secteur or 'non précisé'}\n"
        f"Ton de marque souhaité : {ton or 'libre'}\n"
        f"Public cible : {public or 'grand public'}\n\n"
        "Génère le nom de marque, le slogan et le post de lancement."
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def build_image_prompt(brand_text, style="photoréaliste, éclairage studio"):
    """Construit le prompt image à partir de l'identité de marque générée."""
    return (
        f"Visuel publicitaire de marque, {style}. Composition épurée et "
        f"professionnelle, haute qualité, adapté à un post de lancement. "
        f"Éléments de marque : {brand_text[:500]}"
    )
```

- [ ] **Step 4: Lancer les tests pour vérifier le succès**

Run: `pytest tests/test_prompts.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add core/prompts.py tests/test_prompts.py
git commit -m "feat: brand and image prompt construction (pure logic)"
```

---

## Task 4: Client LLM (`llm_client.py`)

**Files:**
- Create: `core/llm_client.py`
- Test: `tests/test_llm_client.py`

- [ ] **Step 1: Écrire le test qui échoue (SDK openai mocké)**

```python
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
```

- [ ] **Step 2: Lancer le test pour vérifier l'échec**

Run: `pytest tests/test_llm_client.py -v`
Expected: FAIL (`ModuleNotFoundError: core.llm_client`)

- [ ] **Step 3: Écrire l'implémentation**

```python
# core/llm_client.py
from openai import OpenAI
from core import config


def _make_client():
    return OpenAI(base_url=config.NVIDIA_BASE_URL, api_key=config.get_api_key())


def generate_brand(messages, model=None, temperature=0.7):
    """Appelle le LLM NVIDIA en streaming. Génère les morceaux de texte."""
    client = _make_client()
    stream = client.chat.completions.create(
        model=model or config.LLM_MODEL,
        messages=messages,
        temperature=temperature,
        top_p=0.9,
        max_tokens=1024,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
```

- [ ] **Step 4: Lancer le test pour vérifier le succès**

Run: `pytest tests/test_llm_client.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add core/llm_client.py tests/test_llm_client.py
git commit -m "feat: streaming LLM client for NVIDIA NIM"
```

---

## Task 5: Client image (`image_client.py`)

**Files:**
- Create: `core/image_client.py`
- Test: `tests/test_image_client.py`

- [ ] **Step 1: Écrire les tests qui échouent (requests mocké)**

```python
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
```

- [ ] **Step 2: Lancer les tests pour vérifier l'échec**

Run: `pytest tests/test_image_client.py -v`
Expected: FAIL (`ModuleNotFoundError: core.image_client`)

- [ ] **Step 3: Écrire l'implémentation**

```python
# core/image_client.py
import base64
import requests
from core import config


def generate_image(prompt, seed=0, steps=30, timeout=60):
    """Appelle le modèle image NVIDIA. Retourne les bytes de l'image décodée."""
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
```

- [ ] **Step 4: Lancer les tests pour vérifier le succès**

Run: `pytest tests/test_image_client.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Vérifier l'URL réelle de l'API image**

Ouvrir la page du modèle sur build.nvidia.com (ex. FLUX.1-dev), copier l'exemple `requests`, et **ajuster `IMAGE_INVOKE_URL` et le payload dans `config.py`/`image_client.py` si la forme réelle diffère** (certains modèles utilisent un champ `text_prompts` plutôt que `prompt`). Relancer les tests après ajustement.

- [ ] **Step 6: Commit**

```bash
git add core/image_client.py tests/test_image_client.py
git commit -m "feat: image client with base64 decoding for NVIDIA NIM"
```

---

## Task 6: Interface Streamlit (`app.py`)

**Files:**
- Create: `app.py`

> Pas de test automatisé pour l'UI — vérification manuelle (Step 3).

- [ ] **Step 1: Écrire `app.py`**

```python
# app.py
import streamlit as st
from core import prompts, llm_client, image_client

st.set_page_config(page_title="Brand Studio", page_icon="🚀", layout="wide")
st.title("🚀 Brand Studio")
st.caption("Décris ton produit — l'IA génère l'identité de marque et son visuel.")

# --- État de session ---
st.session_state.setdefault("brand_text", "")
st.session_state.setdefault("image_bytes", None)

# --- Formulaire ---
with st.sidebar:
    st.header("Ton produit")
    produit = st.text_area("Produit / idée", placeholder="ex : casque audio sans fil")
    secteur = st.text_input("Secteur", placeholder="ex : tech")
    ton = st.selectbox("Ton de marque", ["libre", "premium", "fun", "minimaliste", "écolo"])
    public = st.text_input("Public cible", placeholder="ex : jeunes pros")
    style = st.selectbox("Style du visuel",
                         ["photoréaliste, éclairage studio", "minimaliste, fond uni",
                          "illustration colorée", "3D moderne"])
    go = st.button("✨ Générer la marque", type="primary", disabled=not produit.strip())

col_text, col_img = st.columns(2)

# --- Génération du texte (streaming) ---
if go:
    brief = {"produit": produit, "secteur": secteur, "ton": ton, "public_cible": public}
    messages = prompts.build_brand_prompt(brief)
    with col_text:
        st.subheader("Identité de marque")
        try:
            brand_text = st.write_stream(llm_client.generate_brand(messages))
            st.session_state.brand_text = brand_text
            st.session_state.image_bytes = None  # reset image, on régénère ensuite
        except Exception as e:
            st.error(f"Erreur lors de la génération du texte : {e}")

# --- Affichage texte mémorisé ---
elif st.session_state.brand_text:
    with col_text:
        st.subheader("Identité de marque")
        st.markdown(st.session_state.brand_text)

# --- Génération / affichage de l'image ---
with col_img:
    st.subheader("Visuel publicitaire")
    if st.session_state.brand_text:
        if st.button("🎨 Générer / régénérer le visuel"):
            img_prompt = prompts.build_image_prompt(st.session_state.brand_text, style=style)
            try:
                with st.spinner("Génération de l'image…"):
                    st.session_state.image_bytes = image_client.generate_image(img_prompt)
            except Exception as e:
                st.error(f"Erreur lors de la génération de l'image : {e}")
        if st.session_state.image_bytes:
            st.image(st.session_state.image_bytes, use_container_width=True)
            st.download_button("⬇️ Télécharger", st.session_state.image_bytes,
                               file_name="brand_visual.png", mime="image/png")
    else:
        st.info("Génère d'abord une identité de marque.")
```

- [ ] **Step 2: Lancer l'appli**

Run: `streamlit run app.py`
Expected: l'appli s'ouvre dans le navigateur sans erreur d'import. Sans clé API, un message d'erreur clair apparaît lors de la génération (pas de crash).

- [ ] **Step 3: Vérification manuelle avec une vraie clé**

Créer `.env` à partir de `.env.example` avec une vraie clé NVIDIA. Saisir un produit, cliquer "Générer la marque" → le texte s'affiche en streaming. Cliquer "Générer le visuel" → l'image s'affiche. Vérifier que régénérer l'image ne relance pas le texte.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: Streamlit Brand Studio interface"
```

---

## Task 7: README et préparation de l'hébergement

**Files:**
- Create: `README.md`
- Create: `.streamlit/config.toml` (optionnel, thème)

- [ ] **Step 1: Écrire `README.md`**

```markdown
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
```

- [ ] **Step 2: Lancer la suite de tests complète**

Run: `pytest -v`
Expected: tous les tests passent (config, prompts, llm_client, image_client).

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: README with setup, architecture and hosting"
```

- [ ] **Step 4: Déploiement (manuel, hors session)**

Pousser le repo sur GitHub, connecter le repo sur share.streamlit.io, ajouter `NVIDIA_API_KEY` dans les Secrets de l'app. Récupérer le lien public pour les livrables.

---

## Définition de "terminé"
- [ ] `pytest -v` : tous les tests passent
- [ ] `streamlit run app.py` fonctionne localement avec une vraie clé
- [ ] Texte généré en streaming + image générée à partir du texte
- [ ] Gestion d'erreurs visible dans l'UI (clé absente, erreur réseau)
- [ ] README complet, repo sur GitHub, app hébergée, clé hors du code
- [ ] Vidéo de démo enregistrée
