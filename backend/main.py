import os
from dotenv import load_dotenv

# Load environment variables from .env file in the parent directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
else:
    print(f"Warning: .env file not found at {dotenv_path}. Environment variables might not be loaded.")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1_router

# Create FastAPI app instance
app = FastAPI(
    title="RAG System API",
    description="API for the Retrieval-Augmented Generation (RAG) System.",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json", # Standard location for OpenAPI spec
    docs_url="/api/v1/docs", # Standard location for Swagger UI
    redoc_url="/api/v1/redoc" # Standard location for ReDoc
)

# CORS (Cross-Origin Resource Sharing) Middleware
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Allows all headers
)

# Include the v1 API router
app.include_router(api_v1_router, prefix="/api/v1")

# Root endpoint
@app.get("/", tags=["General"])
async def read_root():
    """
    Root endpoint for the API.
    Provides a welcome message and link to the documentation.
    """
    return {
        "message": "Welcome to the RAG Testing API!",
        "documentation_v1": "/api/v1/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
