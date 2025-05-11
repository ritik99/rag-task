import chromadb
from chromadb.config import Settings
import os
from typing import Optional

from fastapi import HTTPException # Added
from langchain_chroma import Chroma # Updated import
from langchain_huggingface import HuggingFaceEmbeddings # Updated import

CHROMA_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "chroma_data")
DEFAULT_COLLECTION_NAME = "rag_documents"

# Ensure the directory exists
os.makedirs(CHROMA_DATA_PATH, exist_ok=True)

print(f"ChromaDB persistent path: {CHROMA_DATA_PATH}")

# Global ChromaDB client instance
try:
    chroma_client = chromadb.PersistentClient(
        path=CHROMA_DATA_PATH,
        settings=Settings(anonymized_telemetry=False)
    )
    print("ChromaDB client initialized successfully.")
except Exception as e:
    print(f"Error initializing ChromaDB client: {e}")
    chroma_client = None

# Initialize embedding model
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
try:
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    print(f"HuggingFaceEmbeddings model '{EMBEDDING_MODEL_NAME}' loaded successfully.")
except Exception as e:
    print(f"Error loading HuggingFaceEmbeddings model: {e}")
    embeddings = None

def get_chroma_client() -> Optional[chromadb.Client]:
    """
    Returns the initialized ChromaDB client.
    """
    if chroma_client is None:
        print("CRITICAL: ChromaDB client is not initialized.") # Log more visibly
        raise ConnectionError("ChromaDB client is not initialized. Check server startup logs.")
    return chroma_client

def get_or_create_collection(collection_name: str = DEFAULT_COLLECTION_NAME):
    """
    Retrieves an existing collection or creates it if it doesn't exist.
    """
    client = get_chroma_client()
    collection = client.get_or_create_collection(name=collection_name)
    return collection

def get_vector_store() -> Chroma:
    """
    Provides a Langchain Chroma vector store instance.
    This is suitable for FastAPI dependency injection.
    """
    if embeddings is None:
        raise HTTPException(status_code=500, detail="Embedding model not available. Check server startup logs.")
    if chroma_client is None:
        raise HTTPException(status_code=500, detail="ChromaDB client not available. Check server startup logs.")
        
    vector_store = Chroma(
        client=get_chroma_client(), # Use the getter to ensure client is available
        collection_name=DEFAULT_COLLECTION_NAME,
        embedding_function=embeddings
    )
    return vector_store
