"""Prompt construction logic for brand and image generation."""

import re

SYSTEM_PROMPT = (
    "Tu es un directeur de création expert en branding. À partir de la "
    "description d'un produit, tu proposes une identité de marque percutante. "
    "Réponds en français, de façon structurée, avec EXACTEMENT ces trois "
    "sections en titre Markdown :\n"
    "## Nom de marque\n## Slogan\n## Post de lancement"
)


def build_brand_prompt(brief):
    """Construit les messages (system + user) pour le LLM à partir du brief.

    Args:
        brief (dict): Dictionnaire contenant les clés optionnelles:
            - produit: description du produit
            - secteur: secteur d'activité
            - ton: ton de marque souhaité
            - public_cible: public cible

    Returns:
        list: Liste de deux messages [system, user] pour le LLM
    """
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


def extract_brand_name(brand_text):
    """Extrait le nom de marque depuis le texte Markdown généré par le LLM.

    Cherche la section ``## Nom de marque`` et renvoie la première ligne de
    contenu non vide qui suit, nettoyée du Markdown. À défaut de section, prend
    la première ligne de texte exploitable.

    Args:
        brand_text (str): Texte de marque (Markdown) renvoyé par le LLM.

    Returns:
        str: Nom de marque nettoyé (chaîne vide si introuvable).
    """
    lines = (brand_text or "").splitlines()
    for i, line in enumerate(lines):
        if re.search(r"nom de marque", line, re.IGNORECASE):
            for following in lines[i + 1:]:
                cleaned = _strip_markdown(following)
                if cleaned:
                    return cleaned[:80]
            break
    # Fallback : première ligne de texte nettoyée.
    for line in lines:
        cleaned = _strip_markdown(line)
        if cleaned:
            return cleaned[:80]
    return ""


def _strip_markdown(text):
    """Supprime les artefacts Markdown, hashtags et emojis d'une chaîne.

    Le modèle image (FLUX.1-dev) renvoie une image NOIRE lorsqu'on lui passe du
    Markdown brut, des hashtags ou des emojis : ce nettoyage est indispensable.
    """
    text = re.sub(r"https?://\S+", " ", text)            # URLs
    text = re.sub(r"#\w+", " ", text)                     # hashtags
    text = re.sub(r"[#>*_`~\[\]()\"]", " ", text)         # tokens Markdown
    text = re.sub(r"[^\w\s\-.,!?:éèêëàâäîïôöùûüçœ]", " ", text, flags=re.IGNORECASE)  # emojis & symboles
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .:-")


def build_image_prompt(brand_text, style="photoréaliste, éclairage studio", produit=""):
    """Construit un prompt image PROPRE pour le modèle text-to-image.

    N'injecte jamais le Markdown brut du texte de marque (titres, gras,
    hashtags, emojis) : cela fait renvoyer une image noire par FLUX.1-dev. On ne
    garde que le nom de marque extrait et la description du produit.

    Args:
        brand_text (str): Identité de marque générée (Markdown).
        style (str): Style visuel souhaité.
        produit (str): Description du produit, pour ancrer le visuel.

    Returns:
        str: Prompt image propre, sans Markdown.
    """
    brand_name = extract_brand_name(brand_text)
    sujet = _strip_markdown(produit)[:120] or "le produit phare de la marque"
    marque = f" pour la marque {brand_name}" if brand_name else ""
    return (
        f"Photographie publicitaire de produit{marque}. "
        f"Sujet : {sujet}. Style : {style}. "
        f"Composition épurée et professionnelle, éclairage soigné, haute qualité, "
        f"cadrage centré, adaptée à une campagne de lancement. Sans texte ni logo."
    )
