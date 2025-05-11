from fastapi import APIRouter, HTTPException, Body, Depends
import time # For query_time_ms
from typing import List, Optional
import os
from app.schemas import (
    RagQueryRequest,
    RagQueryResponse,
    SourceDocument,
    MetricScore # Added for inline evaluation
)
from app.core.vector_store import get_vector_store
from app.core.llm_services import rag_llm_client, evaluator_llm, evaluator_embeddings # Import evaluators
from langchain_community.vectorstores import Chroma
from langchain_core.messages import HumanMessage, SystemMessage # For Langchain style prompts

# Ragas components for inline evaluation
from ragas import SingleTurnSample
from ragas.metrics import (
    ResponseRelevancy,
    BleuScore,
    RougeScore,
)

router = APIRouter()

@router.post("/query", response_model=RagQueryResponse)
async def query_rag_system(
    request: RagQueryRequest = Body(...),
    vector_store: Chroma = Depends(get_vector_store)
):
    """
    Submits a query to the RAG system.
    Retrieves relevant documents, generates a response using an LLM.
    If a reference_answer is provided in the request, it also performs Ragas evaluation.
    """
    start_time = time.time()
    evaluation_scores: Optional[MetricScore] = None

    try:
        # 1. Query ChromaDB to get top_k relevant document chunks
        retrieved_docs_with_scores: List[tuple[any, float]] = vector_store.similarity_search_with_score(
            query=request.query,
            k=request.top_k
        )

        sources: List[SourceDocument] = []
        if retrieved_docs_with_scores:
            for doc, score in retrieved_docs_with_scores:
                sources.append(
                    SourceDocument(
                        id=doc.metadata.get("source_document_id", str(doc.metadata.get("id", "unknown_id"))),
                        document_name=doc.metadata.get("filename", "Unknown Document"),
                        snippet=doc.page_content,
                        score=score
                    )
                )
        
        context_for_llm = "\n\n".join([source.snippet for source in sources])
        actual_answer = ""

        if not sources:
            actual_answer = f"I could not find any relevant documents for your query: '{request.query}'. Please try rephrasing or uploading more relevant documents."
        else:
            try:
                if rag_llm_client is None:
                    print("Critical: rag_llm_client is None. LLM functionality is unavailable.")
                    actual_answer = "The Language Model is currently unavailable. Please try again later."
                else:
                    print(f'[query_rag_system] The context is {context_for_llm}')
                    prompt_text = f"You must utilize the sources given to answer the user's query. " \
                                  f"If the source is irrelevant to the question asked, let the user know that sources do not contain the information so you cannot answer. "\
                                  f"Based on the following documents, please answer the query: '{request.query}'\n\n" \
                                  f"Documents:\n{context_for_llm}\n\n" \
                                  f"Answer:"
                    messages = [
                        SystemMessage(content="You are a helpful assistant that answers questions based on provided documents."),
                        HumanMessage(content=prompt_text)
                    ]
                    llm_response = await rag_llm_client.ainvoke(messages)
                    actual_answer = llm_response.content.strip() if hasattr(llm_response, 'content') else str(llm_response).strip()
            except Exception as e_llm:
                print(f"LLM processing error: {e_llm}")
                actual_answer = f"An unexpected error occurred while generating the answer. (Query: {request.query})"

        # 3. Perform Ragas evaluation if reference_answer is provided
        if request.reference_answer:
            print(f'Reference answer provided: {request.reference_answer}. Calculating evaluations.')
            if evaluator_llm is None:
                print("Warning: evaluator_llm is None. LLM-based Ragas metrics will be skipped.")
            if evaluator_embeddings is None:
                print("Warning: evaluator_embeddings is None. Embedding-based Ragas metrics will be skipped.")

            retrieved_contexts = [src.snippet for src in sources]
            sample_data = {
                "user_input": request.query,
                "response": actual_answer,
                "retrieved_contexts": retrieved_contexts,
                "reference": request.reference_answer,
            }
            sample_data_filtered = {k: v for k, v in sample_data.items() if v is not None}
            
            if not all(k in sample_data_filtered for k in ["user_input", "response", "reference"]): # retrieved_contexts can be empty
                print(f"Skipping Ragas evaluation for query '{request.query}' due to missing core data (query, response, or reference).")
            else:
                ragas_sample = SingleTurnSample(**sample_data_filtered)
                current_scores_dict = {}

                # Define metrics to calculate
                metrics_to_run = {
                    "response_relevancy": (ResponseRelevancy, {"llm": evaluator_llm, "embeddings": evaluator_embeddings}, ["response"]), # Check if query is implicitly used
                    "bleu_score": (BleuScore, {}, ["response", "reference"]),
                    "rouge_score": (RougeScore, {}, ["response", "reference"]),
                }
                
                for key, (metric_cls, metric_params, required_fields) in metrics_to_run.items():
                    # Check if all required fields for the metric are present in the sample
                    if not all(field in sample_data_filtered for field in required_fields):
                        print(f"Skipping metric '{key}' for query '{request.query}' due to missing required data: {required_fields}")
                        current_scores_dict[key] = None
                        continue
                    
                    # Skip LLM-based metrics if evaluator_llm is None
                    if "llm" in metric_params and evaluator_llm is None:
                        print(f"Skipping LLM-based metric '{key}' because evaluator_llm is None.")
                        current_scores_dict[key] = None
                        continue
                    # Skip Embedding-based metrics if evaluator_embeddings is None
                    if "embeddings" in metric_params and evaluator_embeddings is None:
                        print(f"Skipping Embedding-based metric '{key}' because evaluator_embeddings is None.")
                        current_scores_dict[key] = None
                        continue
                        
                    try:
                        metric_instance = metric_cls(**{k: v for k, v in metric_params.items() if v is not None})
                        score = await metric_instance.single_turn_ascore(ragas_sample)
                        current_scores_dict[key] = score
                    except Exception as e_metric:
                        print(f"Error calculating Ragas metric '{key}' for query '{request.query}': {e_metric}")
                        current_scores_dict[key] = None
                
                evaluation_scores = MetricScore(**current_scores_dict)
                print(f"[query_rag_system] Evaluation scores are {evaluation_scores}")

    except Exception as e:
        print(f"RAG query processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Error during RAG query processing: {str(e)}")

    end_time = time.time()
    query_time_ms = (end_time - start_time) * 1000

    return RagQueryResponse(
        answer=actual_answer,
        sources=sources,
        query_time_ms=query_time_ms,
        evaluation_scores=evaluation_scores # Add scores to response
    )
