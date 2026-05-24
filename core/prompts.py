"""Prompt construction logic for brand and image generation."""

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


def build_image_prompt(brand_text, style="photoréaliste, éclairage studio"):
    """Construit le prompt image à partir de l'identité de marque générée.

    Args:
        brand_text (str): Texte contenant l'identité de marque générée
        style (str): Style visuel souhaité (défaut: photoréaliste)

    Returns:
        str: Prompt image pour un modèle text-to-image
    """
    truncated_text = brand_text[:500]
    return (
        f"Visuel publicitaire de marque, {style}. Composition épurée et "
        f"professionnelle, haute qualité, adapté à un post de lancement. "
        f"Éléments de marque : {truncated_text}"
    )
