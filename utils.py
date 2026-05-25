# utils.py (LangChain Version)
import base64
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()
# We initialize the model using LangChain's wrapper
# This makes it easy to swap 'gpt-4o' for 'claude' or 'llama' later
model = ChatOpenAI(model="gpt-4o-mini", max_tokens=1024)


def _encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def get_ingredients_from_image(image_bytes: bytes) -> str:
    base64_image = _encode_image(image_bytes)
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": (
                    "List every ingredient you can identify in this image. "
                    "Return a plain comma-separated list, nothing else. "
                    "Example: tomatoes, garlic, olive oil, pasta"
                ),
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
        ]
    )
    try:
        response = model.invoke([message])
        return response.content.strip()
    except Exception as e:
        return f"Error: {e}"


def get_recipes_from_ingredients(ingredients: str) -> str:
    message = HumanMessage(
        content=(
            f"I have these ingredients: {ingredients}\n\n"
            "Suggest 3 recipes I can make. For each recipe provide:\n"
            "- A recipe name as a heading\n"
            "- A one-sentence description\n"
            "- The full ingredient list with quantities\n"
            "- Numbered step-by-step cooking instructions\n"
        )
    )
    try:
        response = model.invoke([message])
        return response.content
    except Exception as e:
        return f"Error: {e}"