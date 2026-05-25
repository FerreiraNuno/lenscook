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


def get_recipe_titles(ingredients: str) -> list[str]:
    """Return a list of 3 recipe name suggestions for the given ingredients."""
    message = HumanMessage(
        content=(
            f"I have these ingredients: {ingredients}\n\n"
            "Suggest 3 recipe names I could make. "
            "Reply with only the 3 names, one per line, no numbering or extra text."
        )
    )
    try:
        response = model.invoke([message])
        titles = [t.strip() for t in response.content.strip().splitlines() if t.strip()]
        return titles[:3]
    except Exception as e:
        return [f"Error: {e}"]


def get_recipe_detail(recipe_name: str, ingredients: str) -> str:
    """Return full step-by-step instructions for a single recipe."""
    message = HumanMessage(
        content=(
            f"I want to make '{recipe_name}' using some of these ingredients: {ingredients}\n\n"
            "Provide the full recipe with:\n"
            "- A one-sentence description\n"
            "- Ingredient list with quantities\n"
            "- Numbered step-by-step cooking instructions"
        )
    )
    try:
        response = model.invoke([message])
        return response.content
    except Exception as e:
        return f"Error: {e}"