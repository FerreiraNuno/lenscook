# main.py
import streamlit as st
from utils import get_recipes_from_image

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

# If an image is captured or uploaded
if img_file is not None:
    # Display the image back to the user
    st.image(img_file, caption="Your ingredients", use_container_width=True)
    
    # Generate button
    if st.button("Generate Recipes", type="primary"):
        with st.spinner("Chef GPT-4o is analyzing your ingredients..."):
            
            # Extract raw bytes from the Streamlit UploadedFile object
            image_bytes = img_file.getvalue()
            
            # Call our utility function
            recipe_text = get_recipes_from_image(image_bytes)
            
            # Display the results
            st.success("Recipes generated!")
            st.markdown(recipe_text)