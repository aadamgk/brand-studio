# app.py
import streamlit as st
from core import prompts, llm_client, image_client

st.set_page_config(
    page_title="Brand Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Thème — direction éditoriale : papier crème chaud, encre profonde, accent
# vermillon. Polices Fraunces (titres) + Manrope (texte).
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Manrope:wght@400;500;600;700&display=swap');

    :root {
        --bg: #F4F1EA;
        --surface: #FBFAF6;
        --ink: #1B1A17;
        --muted: #6E685D;
        --accent: #E5482E;
        --accent-ink: #B5371F;
        --border: #E4DECF;
        --radius: 18px;
    }

    .stApp { background: var(--bg); }
    header[data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 2.2rem; max-width: 1240px; }

    html, body, [data-testid="stMarkdownContainer"],
    .stTextInput input, .stTextArea textarea, .stSelectbox, button, p, label, span {
        font-family: 'Manrope', sans-serif;
        color: var(--ink);
    }
    h1, h2, h3, h4 {
        font-family: 'Fraunces', serif !important;
        letter-spacing: -0.02em;
        color: var(--ink);
    }

    /* Hero */
    .bs-kicker {
        font-family: 'Manrope', sans-serif;
        font-weight: 700;
        font-size: .78rem;
        letter-spacing: .22em;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: .35rem;
    }
    .bs-title {
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-size: 3.1rem;
        line-height: 1.02;
        margin: 0 0 .35rem 0;
    }
    .bs-sub {
        color: var(--muted);
        font-size: 1.04rem;
        max-width: 46ch;
        margin: 0;
    }
    .bs-rule {
        height: 3px; width: 64px; background: var(--accent);
        border-radius: 2px; margin: 1.4rem 0 1.8rem 0;
    }

    /* Section labels au-dessus des cartes */
    .bs-section {
        display: flex; align-items: baseline; gap: .6rem;
        margin: 0 0 .7rem .2rem;
    }
    .bs-section .num {
        font-family: 'Fraunces', serif; font-weight: 600;
        color: var(--accent); font-size: 1.05rem;
    }
    .bs-section .lbl {
        font-family: 'Manrope', sans-serif; font-weight: 700;
        text-transform: uppercase; letter-spacing: .14em;
        font-size: .8rem; color: var(--muted);
    }

    /* Cartes (st.container(border=True)) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--surface);
        border: 1px solid var(--border) !important;
        border-radius: var(--radius);
        padding: 6px 4px;
        box-shadow: 0 1px 2px rgba(27,26,23,.03);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }

    /* Champs */
    .stTextInput input, .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        background: #fff !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(229,72,46,.12) !important;
    }
    div[data-baseweb="select"] > div {
        border-radius: 12px !important;
        border-color: var(--border) !important;
        background: #fff !important;
    }

    /* Boutons */
    .stButton > button {
        border-radius: 999px;
        font-weight: 700;
        padding: .55rem 1.1rem;
        border: 1px solid var(--border);
        transition: transform .05s ease, box-shadow .15s ease;
    }
    .stButton > button:hover { transform: translateY(-1px); }
    [data-testid="stBaseButton-primary"] {
        background: var(--accent) !important;
        border: none !important;
        color: #fff !important;
        box-shadow: 0 6px 18px rgba(229,72,46,.28);
    }
    [data-testid="stBaseButton-primary"]:hover {
        background: var(--accent-ink) !important;
    }

    /* Image générée */
    [data-testid="stImage"] img {
        border-radius: 14px;
        box-shadow: 0 14px 40px rgba(27,26,23,.18);
    }

    /* État vide */
    .bs-empty {
        text-align: center; color: var(--muted);
        padding: 2.6rem 1.2rem; line-height: 1.5;
    }
    .bs-empty .ico { font-size: 1.8rem; display:block; margin-bottom:.5rem; opacity:.7; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# État de session
# ─────────────────────────────────────────────────────────────────────────────
st.session_state.setdefault("brand_text", "")
st.session_state.setdefault("image_bytes", None)
st.session_state.setdefault("last_produit", "")
st.session_state.setdefault("last_style", "")

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar — le brief produit
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div class='bs-kicker'>Brand Studio</div>"
        "<div style='font-family:Fraunces,serif;font-size:1.5rem;font-weight:600;"
        "margin-bottom:1rem'>Le brief</div>",
        unsafe_allow_html=True,
    )
    produit = st.text_area(
        "Produit / idée",
        placeholder="ex : casque audio sans fil à réduction de bruit",
        height=92,
    )
    secteur = st.text_input("Secteur", placeholder="ex : tech / audio")
    ton = st.selectbox("Ton de marque",
                       ["libre", "premium", "fun", "minimaliste", "écolo"])
    public = st.text_input("Public cible", placeholder="ex : jeunes pros urbains")
    style = st.selectbox(
        "Style du visuel",
        ["photoréaliste, éclairage studio", "minimaliste, fond uni",
         "illustration colorée", "3D moderne"],
    )
    st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
    go = st.button("✦  Générer l'identité", type="primary",
                   use_container_width=True, disabled=not produit.strip())
    st.caption("Étape 1 : identité de marque · Étape 2 : visuel publicitaire")

# ─────────────────────────────────────────────────────────────────────────────
# Hero
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='bs-kicker'>Générateur de marque par IA</div>"
    "<h1 class='bs-title'>Du brief à la marque,<br>visuel compris.</h1>"
    "<p class='bs-sub'>Décris ton produit : l'IA imagine une identité de marque "
    "complète, puis en compose le visuel publicitaire.</p>"
    "<div class='bs-rule'></div>",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# Génération du texte (déclenchée par le bouton du brief)
# ─────────────────────────────────────────────────────────────────────────────
if go:
    st.session_state.brand_text = ""
    st.session_state.image_bytes = None
    st.session_state.last_produit = produit
    st.session_state.last_style = style

col_text, col_img = st.columns([1.05, 1], gap="large")

# ── Colonne gauche : identité de marque ──────────────────────────────────────
with col_text:
    st.markdown(
        "<div class='bs-section'><span class='num'>01</span>"
        "<span class='lbl'>Identité de marque</span></div>",
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        if go:
            messages = prompts.build_brand_prompt(
                {"produit": produit, "secteur": secteur,
                 "ton": ton, "public_cible": public}
            )
            try:
                brand_text = st.write_stream(llm_client.generate_brand(messages))
                st.session_state.brand_text = brand_text
            except Exception as e:
                st.session_state.brand_text = ""
                st.error(f"Erreur lors de la génération du texte : {e}")
        elif st.session_state.brand_text:
            st.markdown(st.session_state.brand_text)
        else:
            st.markdown(
                "<div class='bs-empty'><span class='ico'>✦</span>"
                "Remplis le brief à gauche, puis lance la génération.</div>",
                unsafe_allow_html=True,
            )

# ── Colonne droite : visuel publicitaire ─────────────────────────────────────
with col_img:
    st.markdown(
        "<div class='bs-section'><span class='num'>02</span>"
        "<span class='lbl'>Visuel publicitaire</span></div>",
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        if st.session_state.brand_text:
            label = ("🎨  Régénérer le visuel" if st.session_state.image_bytes
                     else "🎨  Générer le visuel")
            if st.button(label, use_container_width=True):
                img_prompt = prompts.build_image_prompt(
                    st.session_state.brand_text,
                    style=st.session_state.last_style or style,
                    produit=st.session_state.last_produit or produit,
                )
                try:
                    with st.spinner("Composition du visuel… (~30 s)"):
                        st.session_state.image_bytes = image_client.generate_image(img_prompt)
                except Exception as e:
                    st.session_state.image_bytes = None
                    st.error(f"Erreur lors de la génération de l'image : {e}")

            if st.session_state.image_bytes:
                st.image(st.session_state.image_bytes, use_container_width=True)
                st.download_button(
                    "⬇️  Télécharger le visuel", st.session_state.image_bytes,
                    file_name="brand_visual.png", mime="image/png",
                    use_container_width=True,
                )
            else:
                st.markdown(
                    "<div class='bs-empty'><span class='ico'>🎨</span>"
                    "Clique sur « Générer le visuel » pour composer l'image "
                    "à partir de l'identité de marque.</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                "<div class='bs-empty'><span class='ico'>🖼️</span>"
                "Le visuel apparaîtra ici une fois l'identité de marque générée.</div>",
                unsafe_allow_html=True,
            )
