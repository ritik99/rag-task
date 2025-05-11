from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Path, Depends
from typing import List, Optional, Dict, Any
import uuid
import os
import tempfile

from app.schemas import (
    DocumentCreateResponse,
    DocumentListResponse,
    DocumentDetailResponse,
    DocumentDeleteResponse,
    DocumentBase
)

from app.core.vector_store import get_vector_store 

# Langchain components
from langchain_community.vectorstores import Chroma # For type hint
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

router = APIRouter()

@router.post("/upload", response_model=List[DocumentCreateResponse], status_code=201)
async def upload_documents(
    files: List[UploadFile] = File(..., description="One or more files to upload."),
    vector_store: Chroma = Depends(get_vector_store)
):
    """
    Uploads one or more documents. Documents are processed, chunked, embedded,
    and stored in the persistent ChromaDB vector store.
    """
    responses = []
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    for file in files:
        if not file.filename:
            continue # Should not happen with FastAPI UploadFile

        source_document_id = str(uuid.uuid4())
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
                tmp_file.write(await file.read())
                tmp_file_path = tmp_file.name
            
            if file.content_type == "application/pdf" or tmp_file_path.lower().endswith(".pdf"):
                loader = PyPDFLoader(tmp_file_path)
            elif file.content_type == "text/plain" or tmp_file_path.lower().endswith(".txt"):
                loader = TextLoader(tmp_file_path)
            # Add more loaders as needed (e.g., for .md, .docx)
            else:
                os.unlink(tmp_file_path) # Clean up temp file
                responses.append(DocumentCreateResponse(id=source_document_id, filename=file.filename, status=f"error: unsupported file type {file.content_type}"))
                continue

            documents = loader.load()
            
            # Add metadata to all loaded document pages/parts before splitting
            for doc in documents:
                doc.metadata["source_document_id"] = source_document_id
                doc.metadata["filename"] = file.filename
                # You can add more metadata like upload_date, user_id etc.

            chunks = text_splitter.split_documents(documents)
            
            if chunks:
                vector_store.add_documents(chunks) # Langchain Chroma handles embedding and adding
                status = "processed"
            else:
                status = "empty_or_unparsable"
            
            responses.append(DocumentCreateResponse(id=source_document_id, filename=file.filename, status=status))

        except Exception as e:
            responses.append(DocumentCreateResponse(id=source_document_id, filename=file.filename, status=f"error: {str(e)}"))
        finally:
            if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path) # Ensure temp file is deleted

    if not responses: # Should not happen if files were provided, but as a safeguard
        raise HTTPException(status_code=400, detail="No files were processed.")
    return responses


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    vector_store: Chroma = Depends(get_vector_store)
):
    """
    Lists unique source documents based on metadata.
    Note: This is a simplified implementation. ChromaDB primarily stores chunks.
    This endpoint attempts to list distinct documents by querying metadata.
    """
    try:
        results = vector_store.get(include=["metadatas"], limit=2000)
        
        seen_doc_ids = set()
        unique_docs_metadata = []
        
        if results and results.get("metadatas"):
            for metadata in results["metadatas"]:
                if metadata and "source_document_id" in metadata:
                    doc_id = metadata["source_document_id"]
                    if doc_id not in seen_doc_ids:
                        seen_doc_ids.add(doc_id)
                        # For each unique document, get its chunk count
                        chunks_for_doc = vector_store.get(
                            where={"source_document_id": doc_id},
                            include=[] # We only need IDs to count
                        )
                        num_chunks = len(chunks_for_doc["ids"]) if chunks_for_doc and chunks_for_doc.get("ids") else 0

                        unique_docs_metadata.append(
                            DocumentBase(
                                id=doc_id,
                                filename=metadata.get("filename"),
                                status="indexed", 
                                indexed_chunks=num_chunks
                            )
                        )
        
        total_unique_docs = len(unique_docs_metadata)
        paginated_docs = unique_docs_metadata[offset : offset + limit]

        return DocumentListResponse(
            documents=paginated_docs,
            total=total_unique_docs,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document_details(
    document_id: str = Path(..., description="The source_document_id of the document to retrieve."),
    vector_store: Chroma = Depends(get_vector_store)
):
    """
    Retrieves details for a specific source document, including its chunks.
    'document_id' here refers to the 'source_document_id' assigned during upload.
    """
    try:
        # Query ChromaDB for chunks matching the source_document_id
        results = vector_store.get(
            where={"source_document_id": document_id},
            include=["metadatas", "documents"] # "documents" here are the text content of chunks
        )
        
        if not results or not results.get("ids"):
            raise HTTPException(status_code=404, detail=f"Document with source_document_id '{document_id}' not found or has no chunks.")

        # Assuming all chunks of a document share the same filename in metadata
        filename = results["metadatas"][0].get("filename") if results["metadatas"] else "N/A"
        
        # Count of chunks for this document_id
        num_chunks = len(results["ids"])

        # For simplicity, we're not returning all chunk content here, just metadata.
        return DocumentDetailResponse(
            id=document_id,
            filename=filename,
            status="indexed", # Simplified
            indexed_chunks=num_chunks,
            # metadata could include other aggregated info if stored
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document details: {str(e)}")


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    document_id: str = Path(..., description="The source_document_id of the document to delete."),
    vector_store: Chroma = Depends(get_vector_store)
):
    """
    Deletes all chunks associated with a specific source_document_id from ChromaDB.
    """
    try:
        # A common way is to get IDs first, then delete by IDs.
        results_to_delete = vector_store.get(
            where={"source_document_id": document_id},
            include=[] # We only need IDs
        )

        if results_to_delete and results_to_delete.get("ids"):
            ids_to_delete = results_to_delete["ids"]
            if ids_to_delete:
                vector_store.delete(ids=ids_to_delete)
                return DocumentDeleteResponse(message=f"Document {document_id} and its {len(ids_to_delete)} chunks deleted successfully.")
            else:
                return DocumentDeleteResponse(message=f"No chunks found for document {document_id} to delete.")
        else:
            raise HTTPException(status_code=404, detail=f"Document with source_document_id '{document_id}' not found for deletion.")
            
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")
