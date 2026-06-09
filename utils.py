# utils.py
import base64
import io

import pypdf
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage

load_dotenv()
model = ChatOpenAI(model="gpt-4o-mini", max_tokens=1024)
embeddings = OpenAIEmbeddings()


def build_vectorstore(pdf_bytes: bytes) -> FAISS:
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    full_text = "".join(page.extract_text() or "" for page in reader.pages)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.create_documents([full_text])

    return FAISS.from_documents(docs, embeddings)


def get_retriever(vectorstore: FAISS):
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


def get_recipe_titles(ingredients: str, vectorstore = None) -> list[str]:
    """Return a list of 3 recipe name suggestions for the given ingredients."""
    if vectorstore:
        retriever = get_retriever(vectorstore)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Du bist ein Kochassistent. Schlage 3 Rezeptnamen vor, "
             "die zu den Zutaten passen. Bevorzuge Rezepte aus dem folgenden Kontext.\n\n"
             "Kontext:\n{context}"),
            ("human",
             "Ich habe folgende Zutaten: {input}\n\n"
             "Antworte NUR mit 3 Rezeptnamen, einen pro Zeile, ohne Nummerierung.")
        ]) 
        chain = (
            {
                "context": retriever | format_docs,
                "input" : RunnablePassthrough(),
            }
            | prompt
            | model
            | StrOutputParser()
        )
        response = chain.invoke(ingredients)
    else:
        prompt = ChatPromptTemplate.from_messages([
            ("human",
             "Ich habe folgende Zutaten: {input}\n\n"
             "Schlage 3 Rezeptnamen vor. "
             "Antworte NUR mit 3 Namen, einen pro Zeile, ohne Nummerierung.")
        ])
        chain = prompt | model | StrOutputParser()
        response = chain.invoke({"input": ingredients})
        
    titles = [t.strip() for t in response.strip().splitlines() if t.strip()]
    return titles[:3]


def get_recipe_detail(recipe_name: str, ingredients: str, vectorstore: FAISS) -> str:
    """Return full step-by-step instructions for a single recipe."""
    if vectorstore:
        retriever = get_retriever(vectorstore)

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Du bist ein Kochassistent. Nutze den folgenden Kontext aus einem Kochbuch "
             "um das Rezept zu erstellen. Falls das Rezept im Kontext vorkommt, "
             "verwende genau diese Version.\n\n"
             "Kontext:\n{context}"),
            ("human",
             "Ich möchte '{recipe_name}' kochen mit diesen Zutaten: {ingredients}\n\n"
             "Gib das vollständige Rezept mit:\n"
             "- Kurzbeschreibung (1 Satz)\n"
             "- Zutatenliste mit Mengen\n"
             "- Nummerierte Schritt-für-Schritt Anleitung")
        ])
        
        chain = (
            {
                "context": RunnableLambda(lambda x: x["recipe_name"]) | retriever | format_docs,
                "recipe_name": lambda x : x["recipe_name"],
                "ingredients": lambda x : x["ingredients"],
            }
            | prompt
            | model
            | StrOutputParser()
        )
        
        return chain.invoke({"recipe_name": recipe_name, "ingredients": ingredients})
    else:
        prompt = ChatPromptTemplate.from_messages([
            ("human",
             "Ich möchte '{recipe_name}' kochen mit diesen Zutaten: {ingredients}\n\n"
             "Gib das vollständige Rezept mit:\n"
             "- Kurzbeschreibung (1 Satz)\n"
             "- Zutatenliste mit Mengen\n"
             "- Nummerierte Schritt-für-Schritt Anleitung")
        ])
        chain = prompt | model | StrOutputParser()
        return chain.invoke({"recipe_name": recipe_name, "ingredients": ingredients})
    
    