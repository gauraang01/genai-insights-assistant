# semantic/build_semantic_index.py
import os
import json
from chromadb import Client, HttpClient
from chromadb.config import Settings
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Embeddings imports
try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_huggingface import HuggingFaceEmbeddings

except ImportError:
    raise ImportError("Please run: poetry add langchain-openai langchain-community sentence-transformers")

def get_embeddings():
    """Return OpenAI or local HuggingFace embeddings."""
    if os.getenv("OPENAI_API_KEY"):
        print("🔑 Using OpenAI embeddings...")
        return OpenAIEmbeddings()
    else:
        print("Using local MiniLM embeddings (offline mode)...")
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_chroma_client():
    """Use Chroma HTTP client (1.x API)."""
    from chromadb import HttpClient
    host = os.getenv("CHROMA_HOST", "localhost")
    port = int(os.getenv("CHROMA_HTTP_PORT", 8000))
    print(f"Connecting to Chroma {host}:{port} ...")
    client = HttpClient(
        host=host,
        port=port,
        tenant="default_tenant",
        database="default_database"
    )
    client.list_collections()  # quick sanity check
    print("Connected to Chroma server.")
    return client





def build_index(merged_json="semantic/merged_semantic.json"):
    """Build vector index from semantic layer."""
    with open(merged_json) as f:
        merged = json.load(f)

    texts, metadatas, ids = [], [], []
    idx = 0
    for section, items in merged.items():
        if isinstance(items, dict):
            for name, details in items.items():
                idx += 1
                text = f"{section.upper()} {name}: {json.dumps(details)}"
                texts.append(text)
                metadatas.append({"type": section, "name": name})
                ids.append(f"{section}_{name}_{idx}")

    chroma_client = get_chroma_client()
    try:
        chroma_client.delete_collection("semantic_index")
        print("Old collection deleted.")
    except Exception:
        print("No existing collection found.")

    collection = chroma_client.get_or_create_collection("semantic_index")

    embedder = get_embeddings()
    embeddings = embedder.embed_documents(texts)

    # Clear & rebuild index
    try:
        collection.delete(where={})
    except Exception:
        pass

    collection.add(documents=texts, metadatas=metadatas, embeddings=embeddings, ids=ids)
    print(f"Indexed {len(texts)} semantic entries in 'semantic_index'.")

if __name__ == "__main__":
    build_index()
