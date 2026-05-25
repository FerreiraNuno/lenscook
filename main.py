# main.py
import streamlit as st
from utils import get_ingredients_from_image, get_recipes_from_ingredients

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
            st.session_state["recipes"] = None

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
        with st.spinner("Chef GPT-4o is cooking up recipes..."):
            st.session_state["recipes"] = get_recipes_from_ingredients(edited)

# Step 3: show recipes
if st.session_state.get("recipes"):
    st.success("Recipes generated!")
    st.markdown(st.session_state["recipes"])
