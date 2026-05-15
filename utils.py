# utils.py (LangChain Version)
import base64
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()
# We initialize the model using LangChain's wrapper
# This makes it easy to swap 'gpt-4o' for 'claude' or 'llama' later
model = ChatOpenAI(model="gpt-4o-mini", max_tokens=1024)

def get_recipes_from_image(image_bytes: bytes) -> str:
    # Encode image as before
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    message = HumanMessage(
        content=[
            {"type": "text", "text": "give me 3 recipes for the provided ingredients"},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
        ]
    )
    
    try:
        response = model.invoke([message])
        return response.content
    except Exception as e:
        return f"Error: {e}"