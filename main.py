# main.py
import streamlit as st
from utils import (
    get_ingredients_from_image,
    get_recipe_titles,
    get_recipe_detail,
    build_vectorstore,
)

st.set_page_config(page_title="KI Rezept Generator", page_icon="🍳")

st.title("🍳 KI Rezept Generator")
st.write("Fotografiere deine Zutaten und erhalte 3 Rezeptvorschläge!")

# Rezept Upload (optional)

st.subheader("Rezepte hochladen (optional)")
pdf_file = st.file_uploader("Lade hier dein bevorzugtes Kochbuch hoch", type=["pdf"], key="pdf_upload")

if pdf_file is not None:
    if "vectorstore" not in st.session_state or st.session_state.get("pdf_name") != pdf_file.name:
        with st.spinner("Rezepte werden indexiert..."):
            st.session_state["vectorstore"] = build_vectorstore(pdf_file.getvalue())
            st.session_state["pdf_name"] = pdf_file.name
    st.success(f"Kochbuch indexiert: **{pdf_file.name}**")
else:
    st.session_state.pop("vectorstore", None)
    st.session_state.pop("pdf_name", None)
            
    

# Provide both Camera and Upload options for easier testing on desktop/mobile
input_method = st.radio("Bildquelle wählen:", ["Kamera", "Datei hochladen"])

img_file = None
if input_method == "Kamera":
    img_file = st.camera_input("Fotografiere deine Zutaten!")
else:
    img_file = st.file_uploader("Lade ein Bild deiner Zutaten hoch", type=["jpg", "jpeg", "png"])

if img_file is not None:
    st.image(img_file, caption="Deine Zutaten", use_container_width=True)

    # Step 1: detect ingredients
    if st.button("Zutaten erkennen", type="primary"):
        with st.spinner("Erkenne Zutaten..."):
            image_bytes = img_file.getvalue()
            detected = get_ingredients_from_image(image_bytes)
            st.session_state["detected_ingredients"] = detected
            st.session_state["recipe_titles"] = None
            st.session_state["recipe_details"] = {}

# Step 2: let user review and edit the ingredient list
if st.session_state.get("detected_ingredients"):
    st.subheader("Erkannte Zutaten")
    st.write("Überprüfe die Liste und passe sie an, dann generiere Rezepte.")
    edited = st.text_area(
        "Zutaten (kommagetrennt)",
        value=st.session_state["detected_ingredients"],
        key="ingredients_input",
    )

    if st.button("Rezepte generieren", type="primary"):
        vectorstore = st.session_state.get("vectorstore")
        with st.spinner("Suche Rezeptideen..."):
            titles = get_recipe_titles(edited, vectorstore)
            st.session_state["recipe_titles"] = titles
            st.session_state["confirmed_ingredients"] = edited
        details = {}
        for i, title in enumerate(titles):
            with st.spinner(f"Lade Rezept {i + 1} von {len(titles)}..."):
                details[f"detail_{title}"] = get_recipe_detail(title, edited, vectorstore)
        st.session_state["recipe_details"] = details

# Step 3: show recipe titles with expandable full details
titles = st.session_state.get("recipe_titles")
if titles:
    has_book = "vectorstore" in st.session_state
    st.success("Hier sind 3 Rezepte aus deinem Kochbuch!" if has_book
        else "Hier sind 3 Rezepte die du machen kannst!")
    for title in titles:
        with st.expander(f"**{title}**  —  für das vollständige Rezept aufklappen"):
            detail = st.session_state.get("recipe_details", {}).get(f"detail_{title}")
            if detail:
                st.markdown(detail)
