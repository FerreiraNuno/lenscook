# utils.py (LangChain Version)
import base64
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()
# We initialize the model using LangChain's wrapper
# This makes it easy to swap 'gpt-4o' for 'claude' or 'llama' later
llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=1024)
embeddings = OpenAIEmbeddings()

# --- Pinecone Setup ---
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
INDEX_NAME = "recipe-index"

#Indexing
def build_vectorstore(pdf_bytes: bytes) -> str:
    reader = pypdf.PdfReader(io.Bytes(pdf_bytes))
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""
        
    #Chunking
    splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 20)
    docs = splitter.create_documents([full_text])
    print(f"Chunks erzeuht: {len(docs)}")
    
    #Pinecone Index neu erstellen
    dimensions = len(embeddings.embed_query("test"))
    if pc.has_index(INDEX_NAME):
        pc.delete_index(INDEX_NAME)
    pc.create_index(
        name = INDEX_NAME
        dimension = dimensions,
        metric = "cosine",
        spec = ServerlessSpec(cloud = "aws", region = "us-east-1"),
    )
    
    #Chunks in Pinecone laden
    
    vectorstore = PineconeVectorStore(index_name = INDEX_NAME, embedding = embeddings)
    vectorstore.add_documents(docs)
    return vectorstore

#retriever
def get_retriever(vectorstore: PineconeVectorStore):
    return vectorstore.as_retriever(search_kwargs={"k":5})

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)
    
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