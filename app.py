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
