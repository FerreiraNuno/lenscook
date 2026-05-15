# utils.py
import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_recipes_from_image(image_bytes: bytes) -> str:
    """
    Takes raw image bytes, encodes them to Base64, 
    and sends them to GPT-4o to generate recipes.
    """
    # Convert the raw bytes to a base64 encoded string
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "give me 3 recipes for the provided ingredient"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000 # Enough room for 3 recipes
        )
        return response.choices[0].message.content
    
    except Exception as e:
        return f"An error occurred while contacting OpenAI: {e}"