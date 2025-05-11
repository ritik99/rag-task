# Project RAG Application

This project implements a Retrieval Augmented Generation (RAG) system, featuring a FastAPI backend for data processing and a Next.js frontend.

## Overview

*   **Backend (FastAPI):** Handles document uploading, processing, embedding, storage in a Chroma vector database, and provides API endpoints for querying the RAG system. It uses `uv` for package management and `uvicorn` as the ASGI server.
*   **Frontend (Next.js):** Provides a user interface to upload documents, submit questions to the backend, and display the generated answers along with their sources. It uses `bun` for package management and development.

## Prerequisites

*   Python 3.11+ (for backend)
*   `uv` (Python package installer and virtual environment manager)
*   Node.js (latest LTS recommended for frontend)
*   `bun` (JavaScript runtime and toolkit)

## Running the Application Locally

You need to run the backend and frontend services separately in two different terminal sessions.

### 1. Setup .env

Create the following .env:
```
NEXT_PUBLIC_FASTAPI_BACKEND_URL=http://localhost:8000
DEFAULT_LLM_MODEL=gpt-4o
RAGAS_LLM_MODEL=gpt-4o
OPENAI_API_KEY=YOUR_OPENAI_KEY
```

### 2. Running the Backend (FastAPI)

The backend server will run on `http://localhost:8000`.

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create and activate a Python virtual environment using `uv`:**
    ```bash
    uv venv
    source .venv/bin/activate  # On macOS/Linux
    # .venv\Scripts\activate   # On Windows
    ```

3.  **Install Python dependencies using `uv`:**
    (This will install dependencies listed in `pyproject.toml`)
    ```bash
    uv pip install .
    ```

4.  **Run the FastAPI application:**
    The command you provided for manual execution is:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --loop asyncio
    ```
    Alternatively, if you want auto-reloading during development:
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 --loop asyncio
    ```

5.  **Accessing the Backend:**
    *   API Base URL: `http://localhost:8000`
    *   Interactive API Documentation (Swagger UI): `http://localhost:8000/api/v1/docs`

### 3. Running the Frontend (Next.js)

The frontend development server will run on `http://localhost:3000`.

1.  **Navigate to the frontend directory (in a new terminal):**
    ```bash
    cd frontend
    ```

2.  **Install JavaScript dependencies using `bun`:**
    ```bash
    bun install
    ```

3.  **Run the Next.js development server using `bun`:**
    The command you provided for manual execution is:
    ```bash
    bun dev
    ```
    (This typically uses the `dev` script from `frontend/package.json`, which is `next dev --turbopack`)

4.  **Accessing the Frontend:**
    *   Open your browser and go to `http://localhost:3000`

### 4. Using the app

The current prompt instructs the LLM to answer questions only based on the information from the fetched chunks. Initially the Chroma database will have no data. Add documents 
using the `api/v1/documents/upload` endpoints explained inside `backend/README.md`. For example, `curl -X POST -F "files=@[ROOT_LOCATION]/rag-task/data/FastHTML_llms.txt" http://localhost:8000/api/v1/documents/upload`

## Project Structure Highlights

*   **`backend/`**: Contains the FastAPI application.
    *   `main.py`: FastAPI app entry point.
    *   `app/`: Core application logic, API endpoints, and services.
    *   `pyproject.toml`: Python project dependencies.
    *   `chroma_data/`: Default local storage for ChromaDB (should be gitignored).
*   **`frontend/`**: Contains the Next.js application.
    *   `app/page.tsx`: Main page component.
    *   `package.json`: Node.js project dependencies and scripts.
*   **`data/`**: Sample data files for the RAG system.
*   **`README.md`**: This file.
*   **`.gitignore`**: Specifies intentionally untracked files that Git should ignore.
