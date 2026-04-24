from typing import List, TypedDict
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.retrievers import EnsembleRetriever
from sentence_transformers import CrossEncoder
from langchain_core.documents import Document

class SearchOutput(TypedDict):
    content: str
    source: str
    retrieval_score: float
    rerank_score: float
    
# 1. Prepare data using the proper Document class
raw_data = [
    {"content": "LangGraph is a library for building stateful, multi-actor applications...", "source": "langchain_docs"},
    {"content": "FAISS is a library for efficient similarity search...", "source": "vector_store_weekly"},
    {"content": "The BM25 algorithm is a ranking function used by search engines...", "source": "search_theory_hub"},
    {"content": "Hybrid search combines BM25 with FAISS retrieval.", "source": "ai_engineering_blog"},
]

# Convert to LangChain Document objects
docs = [Document(page_content=d["content"], metadata={"source": d["source"]}) for d in raw_data]

# Setup Components
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# Cross-Encoder for high-accuracy re-ranking
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# STEP 1: Hybrid Retrieval (Using ainvoke for 2026 standards)
bm25 = BM25Retriever.from_documents(docs)
faiss_vs = FAISS.from_documents(docs, embeddings)

ensemble = EnsembleRetriever(
    retrievers=[bm25, faiss_vs.as_retriever()],
    weights=[0.4, 0.6]
)

# --- Async Helper ---
async def get_hybrid_reranked_docs(query: str) -> List[Document]:    
    # ainvoke allows other graph tasks to run in parallel
    initial_docs = await ensemble.ainvoke(query)
    
    # STEP 2: Re-ranking
    # Note: Most local CrossEncoders are CPU-bound and don't have anative 'async' call,
    # but we keep the wrapper async so the Graph stays non-blocking.
    pairs = [[query, doc.page_content] for doc in initial_docs]
    rerank_scores = reranker.predict(pairs)
    
    final_output: List[Document] = []
    for i, doc in enumerate(initial_docs):        
        doc_entry: SearchOutput = {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "retrieval_score": 0.0, # Ensemble doesn't provide raw scores by default
            "rerank_score": float(rerank_scores[i])
        }
        final_output.append(doc_entry)
        
    final_output.sort(key=lambda x: x["rerank_score"], reverse=True)
    return final_output

