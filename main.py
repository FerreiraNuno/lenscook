# main.py
import streamlit as st
from utils import (
    get_ingredients_from_image,
    get_recipe_titles,
    get_recipe_detail,
    build_vectorstore,
)

st.set_page_config(page_title="AI Recipe Generator", page_icon="🍳")

st.title("🍳 AI Recipe Generator")
st.write("Take a picture of your ingredients to get 3 instant recipes!")

# Rezept Upload (optional)

st.subheader("Rezepte hochladen (optional)")
pdf_file = st.file_uploader("Lad hier deine prefferierten Rezepte hoch", type = ["pdf"], key = "pdf_upload")

if pdf_file is not None:
    if "vectorstore" not in st.session_state or st.session_state.get("pdf_name") != pdf_file.name:
        with st.spinner("Extracting recipes..."):
            st.session_state["vectorstore"] = build_vectorstore(pdf_file.getvalue())
            st.session_state["pdf_name"] = pdf_file.name
    st.success(f"Kochbuch indexiert: **{pdf_file.name}**")
else:
    st.session_state.pop("vectorstore", None)
    st.session_state.pop("pdf_name", None)
            
    

# Provide both Camera and Upload options for easier testing on desktop/mobile
input_method = st.radio("Choose image input method:", ["Camera", "File Upload"])

img_file = None
if input_method == "Camera":
    img_file = st.camera_input("Snap a picture of your ingredients!")
else:
    img_file = st.file_uploader("Upload an image of your ingredients", type=["jpg", "jpeg", "png"])

if img_file is not None:
    st.image(img_file, caption="Your ingredients", use_container_width=True)

    # Step 1: detect ingredients
    if st.button("Detect Ingredients", type="primary"):
        with st.spinner("Identifying ingredients..."):
            image_bytes = img_file.getvalue()
            detected = get_ingredients_from_image(image_bytes)
            st.session_state["detected_ingredients"] = detected
            st.session_state["recipe_titles"] = None
            st.session_state["recipe_details"] = {}

# Step 2: let user review and edit the ingredient list
if st.session_state.get("detected_ingredients"):
    st.subheader("Detected ingredients")
    st.write("Edit the list below if anything is missing or wrong, then generate recipes.")
    edited = st.text_area(
        "Ingredients (comma-separated)",
        value=st.session_state["detected_ingredients"],
        key="ingredients_input",
    )

    if st.button("Generate Recipes", type="primary"):
        with st.spinner("Finding recipe ideas..."):
            vectorstore = st.session_state.get("vectorstore")
            st.session_state["recipe_titles"] = get_recipe_titles(edited, vectorstore)
            st.session_state["recipe_details"] = {}
            st.session_state["confirmed_ingredients"] = edited

# Step 3: show recipe titles with expandable full details
titles = st.session_state.get("recipe_titles")
if titles:
    has_book = "vectorstore" in st.session_state
    st.success("Hier sind 3 Rezepte aus deinem Kochbuch!" if has_book
        else "Hier sind 3 Rezepte die du machen kannst!")
    confirmed_ingredients = st.session_state.get("confirmed_ingredients", "")
    vectorstore = st.session_state.get("vectorstore")
    for title in titles:
        with st.expander(f"**{title}**  —  click to see full recipe"):
            detail_key = f"detail_{title}"
            if detail_key not in st.session_state["recipe_details"]:
                if st.button(f"Load full recipe for '{title}'", key=f"btn_{title}"):
                    with st.spinner("Fetching full recipe..."):
                        detail = get_recipe_detail(title, confirmed_ingredients, vectorstore)
                        st.session_state["recipe_details"][detail_key] = detail
                        st.rerun()
            else:
                st.markdown(st.session_state["recipe_details"][detail_key])
