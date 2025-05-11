from fastapi import APIRouter

from app.api.v1 import documents, rag

# Create a main v1 router
api_v1_router = APIRouter()

# Include sub-routers with prefixes
api_v1_router.include_router(documents.router, prefix="/documents", tags=["Document Management"])
api_v1_router.include_router(rag.router, prefix="/rag", tags=["RAG System"])

