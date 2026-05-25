# main.py
import streamlit as st
from utils import get_ingredients_from_image, get_recipe_titles, get_recipe_detail

st.set_page_config(page_title="AI Recipe Generator", page_icon="🍳")

st.title("🍳 AI Recipe Generator")
st.write("Take a picture of your ingredients to get 3 instant recipes!")

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
            st.session_state["recipe_titles"] = get_recipe_titles(edited)
            st.session_state["recipe_details"] = {}
            st.session_state["confirmed_ingredients"] = edited

# Step 3: show recipe titles with expandable full details
titles = st.session_state.get("recipe_titles")
if titles:
    st.success("Here are 3 recipes you can make!")
    confirmed_ingredients = st.session_state.get("confirmed_ingredients", "")

    for title in titles:
        with st.expander(f"**{title}**  —  click to see full recipe"):
            detail_key = f"detail_{title}"
            if detail_key not in st.session_state["recipe_details"]:
                if st.button(f"Load full recipe for '{title}'", key=f"btn_{title}"):
                    with st.spinner("Fetching full recipe..."):
                        detail = get_recipe_detail(title, confirmed_ingredients)
                        st.session_state["recipe_details"][detail_key] = detail
                        st.rerun()
            else:
                st.markdown(st.session_state["recipe_details"][detail_key])
