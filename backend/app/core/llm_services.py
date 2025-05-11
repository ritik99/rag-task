import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_community.llms.fake import FakeListLLM
from langchain_community.embeddings.fake import FakeEmbeddings as LangchainFakeEmbeddings # Renamed to avoid conflict

# Default fake responses for LLM
_fake_llm_responses = ["This is a fallback fake LLM response."] * 10
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
try:
    # Core Langchain LLM Client (for general use, e.g., in RAG)
    general_llm_model_name = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")
    
    general_llm = ChatOpenAI(model=general_llm_model_name, temperature=0.3, api_key=OPENAI_API_KEY)
    print(f"Initialized general_llm with ChatOpenAI model: {general_llm_model_name}.")

    # Ragas specific LLM and Embeddings
    ragas_llm_model_name = os.getenv("RAGAS_LLM_MODEL", "gpt-4o")
    _ragas_chat_openai_instance = ChatOpenAI(model=ragas_llm_model_name, api_key=OPENAI_API_KEY)
    evaluator_llm = LangchainLLMWrapper(langchain_llm=_ragas_chat_openai_instance)
    print(f"Initialized Ragas evaluator_llm with ChatOpenAI model: {ragas_llm_model_name}")

    _ragas_openai_embeddings_instance = OpenAIEmbeddings()
    evaluator_embeddings = LangchainEmbeddingsWrapper(embeddings=_ragas_openai_embeddings_instance)
    print("Initialized Ragas evaluator_embeddings with OpenAIEmbeddings.")

except Exception as e:
    print(f"Warning: Error initializing OpenAI LLM/Embedding services: {e}")
    print("Falling back to FakeListLLM and FakeEmbeddings.")
    print("Please ensure OPENAI_API_KEY is set in the root .env file and accessible for real LLM functionality.")

    # Fallback for general LLM
    general_llm = FakeListLLM(responses=_fake_llm_responses)
    print("Fallback: Initialized general_llm with FakeListLLM.")

    # Fallback for Ragas LLM
    _ragas_fake_llm_instance = FakeListLLM(responses=_fake_llm_responses)
    evaluator_llm = LangchainLLMWrapper(langchain_llm=_ragas_fake_llm_instance)
    print("Fallback: Initialized Ragas evaluator_llm with FakeListLLM.")

    # Fallback for Ragas Embeddings
    # Ragas LangchainEmbeddingsWrapper needs a Langchain Embeddings object.
    _ragas_fake_embeddings_instance = LangchainFakeEmbeddings(size=768) # Specify a common embedding size
    evaluator_embeddings = LangchainEmbeddingsWrapper(embeddings=_ragas_fake_embeddings_instance)
    print("Fallback: Initialized Ragas evaluator_embeddings with FakeEmbeddings.")

rag_llm_client = general_llm
