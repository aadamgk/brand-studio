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
