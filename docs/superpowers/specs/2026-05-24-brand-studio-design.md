# Brand Studio — Design / Spec

**Date :** 2026-05-24
**Auteur :** Ahmat (Mastère Data Scientist YNOV — Deep Learning, instructeur : Antoine Vacavant)
**Statut :** Validé — prêt pour le plan d'implémentation

## 1. Objectif

Construire une interface web pour interagir avec une IA générative, dans le cadre du projet individuel noté du cours Deep Learning. Le concept retenu est le **Brand Studio** : un assistant de création de marque qui **chaîne deux modalités** —

1. un **LLM** génère l'identité textuelle d'un produit (nom de marque, slogan, post de lancement) ;
2. un **modèle de génération d'image** produit automatiquement le visuel publicitaire correspondant.

L'intérêt pédagogique et la valeur de démonstration viennent du **chaînage des deux modèles** : le texte généré alimente le prompt de l'image.

## 2. Contraintes (issues du brief)

- Modèle chargé via **NVIDIA NIM** (API compatible OpenAI, nécessite une clé API).
- Interface utilisateur en **Streamlit**.
- Produit hébergé si possible.
- Livrables : code Python, lien d'hébergement, README (technos), vidéos de démo.
- La clé API ne doit **jamais** figurer dans le code source (`.env` ignoré par git en local, `st.secrets` en production).

## 3. Décisions de cadrage

| Décision | Choix | Raison |
|---|---|---|
| Backend | **NVIDIA NIM** | Crédits gratuits, gros modèles, fiable, pas de dépendance au GPU local (Windows 11) |
| Modalités | **Texte + Image (multimodal)** | Effet « waouh » en démo, démontre la maîtrise de deux APIs |
| Concept | **Brand Studio** (nom/slogan/post → visuel) | Cas d'usage « produit réel », plus marquant qu'un chatbot générique. Concept potentiellement affinable plus tard sans changer l'architecture. |
| Échéance | Détendue (1-2 semaines) | Permet des fonctionnalités bonus |
| Niveau Python | À l'aise | Code expliqué au fil de l'eau, pas besoin de tout vulgariser |
| Hébergement | **Streamlit Community Cloud** | Gratuit, simple, coche la case « hébergement » |

## 4. Détail technique des deux APIs NVIDIA NIM

> Point clé : NVIDIA NIM expose **deux APIs distinctes**.

- **Chat / LLM** : compatible OpenAI. `base_url = https://integrate.api.nvidia.com/v1`, package `openai`, **streaming** supporté. Modèle type : un Llama instruct.
- **Image** : endpoint REST séparé (`requests`). On POST un JSON `{prompt, ...}` et on récupère l'image en **base64** dans `artifacts[0].base64`. Modèle type : FLUX.1-dev ou SDXL.

Conséquence : deux clients isolés dans le code (un par modalité).

## 5. Architecture

```
┌─────────────────────────────────────────────┐
│            Interface Streamlit (app.py)        │
│   Saisie produit → bouton "Générer le brand"  │
└───────────────┬───────────────────────────────┘
                │
        ┌───────┴────────┐
        ▼                ▼
┌──────────────┐   ┌──────────────┐
│ llm_client.py│   │image_client.py│
│ (openai SDK) │   │  (requests)   │
│  streaming   │   │  base64 → img │
└──────┬───────┘   └──────┬───────┘
       │                  │
       └────► NVIDIA NIM API ◄──┘
          (clé dans .env / secrets)
```

### Flux d'utilisation
1. L'utilisateur décrit son produit/idée + options (ton de marque, secteur, public cible).
2. Clic → `llm_client` appelle le LLM en streaming : nom de marque + slogan + post de lancement (affichage en direct).
3. L'app construit automatiquement un prompt visuel à partir du texte généré → `image_client` génère le visuel publicitaire, affiché à côté du texte.
4. L'utilisateur peut régénérer texte ou image **indépendamment**.

## 6. Composants

```
brand-studio/
├── app.py                  # Interface Streamlit (UI uniquement)
├── core/
│   ├── llm_client.py       # Client chat NVIDIA (openai SDK, streaming)
│   ├── image_client.py     # Client image NVIDIA (requests, base64)
│   ├── prompts.py          # Construction des prompts (texte + image)
│   └── config.py           # Clé API + constantes (modèles, URLs)
├── tests/
│   ├── test_prompts.py     # Tests de la logique de prompts (sans réseau)
│   └── test_clients.py     # Tests des clients (API mockée)
├── .env.example            # Modèle de config (sans la vraie clé)
├── .gitignore              # ignore .env, __pycache__, etc.
├── requirements.txt        # streamlit, openai, requests, python-dotenv, pytest
└── README.md               # technos, install, run, démo
```

| Fichier | Responsabilité | Dépend de |
|---|---|---|
| `config.py` | Lit la clé API (`.env`/`st.secrets`), expose modèles et URLs | python-dotenv |
| `llm_client.py` | `generate_brand(messages) → stream de texte`. Une seule fonction publique. | openai, config |
| `image_client.py` | `generate_image(prompt) → bytes PNG`. Décode le base64. | requests, config |
| `prompts.py` | `build_brand_prompt(...)` et `build_image_prompt(brand_text)`. Pure logique, **sans réseau**. | rien |
| `app.py` | Affichage, saisie, boutons, état de session. **Aucune logique API directe.** | streamlit, core/* |

### Principes de conception
- `prompts.py` ne fait aucun appel réseau → testable sans clé API ; c'est là que vit la valeur métier (prompt engineering).
- Chaque client expose **une seule fonction publique** → mockable, remplaçable si on change de fournisseur.
- `app.py` ne contient que de l'UI et de la gestion d'état (`st.session_state`) → changer le concept ne touche qu'à `app.py` et `prompts.py`.

## 7. Flux de données

```
[Formulaire app.py]  brief = {produit, secteur, ton, public_cible}
        │
        ▼  prompts.build_brand_prompt(brief) → messages[] (system + user)
        ▼  llm_client.generate_brand(messages) → yield chunks (st.write_stream)
        ▼  brand_text → st.session_state
        │
        ▼  [clic "Illustrer"]  prompts.build_image_prompt(brand_text) → prompt visuel
        ▼  image_client.generate_image(prompt) → bytes PNG
        ▼  st.image(...) + bouton télécharger
```

**État de session** : `st.session_state` conserve `brand_text` et `image_bytes` pour que régénérer l'image ne relance pas le texte (et inversement) — nécessaire car Streamlit réexécute tout le script à chaque interaction.

## 8. Gestion d'erreurs

| Situation | Comportement |
|---|---|
| Clé API absente/invalide | Message clair : « Configure ta clé NVIDIA dans `.env` » — pas de stack trace brute |
| Timeout / erreur réseau | `try/except` → `st.error(...)` + bouton « Réessayer », pas de crash |
| Réponse image vide/mal formée | Vérifier que `artifacts[0].base64` existe avant décodage |
| Champ produit vide | Bouton désactivé + message « Décris d'abord ton produit » |

## 9. Stratégie de tests (TDD)

- **`test_prompts.py`** (cœur, sans réseau) : vérifie que `build_brand_prompt` inclut produit/ton/secteur dans les messages, et que `build_image_prompt` extrait un prompt visuel cohérent. Rapide, déterministe, sans clé.
- **`test_clients.py`** : appels NVIDIA **mockés**. Vérifie que `generate_image` décode le base64 en bytes et que `generate_brand` enchaîne les chunks. Jamais d'appel réel dans les tests.
- Tests écrits **avant** l'implémentation (TDD), en priorité pour `prompts.py`.

## 10. Hébergement

**Streamlit Community Cloud** (gratuit) : push GitHub → connexion du repo → clé NVIDIA dans les *Secrets* de l'app.

## 11. Livrables (rappel)

- [ ] Code Python (repo GitHub)
- [ ] Lien d'hébergement (Streamlit Cloud)
- [ ] README (technos, install, run)
- [ ] Vidéo(s) de démo

## 12. Hors périmètre (YAGNI)

- Authentification utilisateur
- Base de données / persistance entre sessions
- Multi-langue de l'interface (FR uniquement au départ)
- Modèles locaux Hugging Face (on reste full API NVIDIA)

## 13. Idées bonus (si le temps le permet)

- Choix du style visuel (plusieurs presets de prompt image)
- Plusieurs propositions de nom/slogan en parallèle
- Export d'un « kit de marque » (texte + image) en PDF/ZIP
- Réglages avancés (température LLM, seed image)
