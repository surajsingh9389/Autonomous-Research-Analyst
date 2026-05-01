import asyncio
from typing import List, TypedDict
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder
from langchain_core.documents import Document

class SearchOutput(TypedDict):
    content: str
    source: str
    retrieval_score: float
    rerank_score: float
    
# Prepare data using the proper Document class
raw_data = [
    {"content": "LangGraph is a library for building stateful, multi-actor applications...", "source": "langchain_docs"},
    {"content": "FAISS is a library for efficient similarity search...", "source": "vector_store_weekly"},
    {"content": "The BM25 algorithm is a ranking function used by search engines...", "source": "search_theory_hub"},
    {"content": "Hybrid search combines BM25 with FAISS retrieval.", "source": "ai_engineering_blog"},
]


# Initialize Sparse (Keyword) Embeddings
sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

# Convert to LangChain Document objects
docs = [Document(page_content=d["content"], metadata={"source": d["source"]}) for d in raw_data]

# Setup Components
embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# Cross-Encoder for high-accuracy re-ranking
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Initialize VectorStore in HYBRID mode
vectorstore = QdrantVectorStore.from_documents(
    documents=docs,
    embedding=embeddings_model,
    sparse_embedding=sparse_embeddings,
    path="./qdrant_db",
    collection_name="research_docs",
    retrieval_mode=RetrievalMode.HYBRID, # Enables Dense + Sparse Fusion
)

# --- Async Helper ---
async def get_hybrid_reranked_docs(query: str, top_k: int = 3) -> List[SearchOutput]:   
    # ainvoke allows other graph tasks to run in parallel
    initial_docs_with_score = await vectorstore.asimilarity_search_with_score(query, k=top_k)
    
    if not initial_docs_with_score:
        return []
    
    # Re-ranking
    
    # Cross-encoders are CPU-intensive; we run in a thread to keep the loop non-blocking
    loop = asyncio.get_event_loop()
    
    passages = [doc.page_content for doc, _ in initial_docs_with_score]
    pairs = [[query, p] for p in passages]
    
    rerank_scores = await loop.run_in_executor(None, lambda: reranker.predict(pairs))
    
    final_output: List[SearchOutput] = []
    for i, (doc, score) in enumerate(initial_docs_with_score):        
        doc_entry: SearchOutput = {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "retrieval_score": float(score),
            "rerank_score": float(rerank_scores[i])
        }
        final_output.append(doc_entry)
    
    # Sort by rerank score
    final_output.sort(key=lambda x: x["rerank_score"], reverse=True)
    
    # Return top k docs after sorting by re-rank score
    return final_output[:top_k]

