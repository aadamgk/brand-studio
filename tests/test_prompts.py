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


def test_extract_brand_name_from_markdown_section():
    brand_text = "## Nom de marque\n**Lumina**\n\n## Slogan\n\"Éclairez\""
    assert prompts.extract_brand_name(brand_text) == "Lumina"


def test_extract_brand_name_fallback_first_line():
    assert prompts.extract_brand_name("ZenFlow tout court") == "ZenFlow tout court"


def test_build_image_prompt_strips_markdown_and_hashtags():
    """Cause racine du bug image noire : aucun artefact Markdown/hashtag/emoji
    ne doit fuiter dans le prompt image."""
    brand_text = (
        "## Nom de marque\n**Lumina**\n\n## Post de lancement\n"
        "Découvrez Lumina ! 🎧 #Lumina #CasqueAudio #RéductionDeBruit"
    )
    img_prompt = prompts.build_image_prompt(
        brand_text, style="photoréaliste", produit="casque audio"
    )
    assert "##" not in img_prompt
    assert "**" not in img_prompt
    assert "#" not in img_prompt
    assert "🎧" not in img_prompt
    assert "Lumina" in img_prompt
    assert "casque audio" in img_prompt


def test_build_image_prompt_includes_product():
    img_prompt = prompts.build_image_prompt(
        "## Nom de marque\nAqua", produit="bouteille réutilisable"
    )
    assert "bouteille réutilisable" in img_prompt
    assert "Aqua" in img_prompt
