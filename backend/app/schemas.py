from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- Document Management Schemas ---

class DocumentBase(BaseModel):
    id: str
    filename: Optional[str] = None
    status: Optional[str] = None
    indexed_chunks: Optional[int] = None
    added_on: Optional[str] = None # Consider using datetime
    metadata: Optional[Dict[str, Any]] = None

class DocumentCreateResponse(BaseModel):
    id: str
    filename: str
    status: str = "processing_started"

class DocumentListResponse(BaseModel):
    documents: List[DocumentBase]
    total: int
    limit: int
    offset: int

class DocumentDetailResponse(DocumentBase):
    pass

class DocumentDeleteResponse(BaseModel):
    message: str

# --- RAG System Schemas ---

class RagQueryRequest(BaseModel):
    query: str = Field(..., description="The user's query.")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of relevant documents to retrieve.")
    reference_answer: Optional[str] = Field(None, description="Optional ground truth answer for evaluation.")

class SourceDocument(BaseModel):
    id: str  # ID of the source document chunk
    document_name: Optional[str] = None
    snippet: str
    score: Optional[float] = None

class MetricScore(BaseModel):
    response_relevancy: Optional[float] = Field(None, description="Score for response relevancy to the query")
    bleu_score: Optional[float] = Field(None, description="BLEU score for similarity to reference answer")
    rouge_score: Optional[float] = Field(None, description="ROUGE score for similarity to reference answer")

class RagQueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    query_time_ms: Optional[float] = None
    evaluation_scores: Optional[MetricScore] = Field(None, description="Evaluation scores if reference_answer was provided.")
