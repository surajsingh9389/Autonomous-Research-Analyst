import asyncio
from typing import List, Optional
from core.state import RetrievedDoc

from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder
from langchain_core.documents import Document


class VectorDBService:
    def __init__(
        self, 
        db_path: str = "./qdrant_db", 
        collection_name: str = "research_docs",
        dense_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        sparse_model: str = "Qdrant/bm25",
        rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Initialize Models
        self.embeddings_model = HuggingFaceEmbeddings(model_name=dense_model)
        self.sparse_embeddings = FastEmbedSparse(model_name=sparse_model)
        self.reranker = CrossEncoder(rerank_model)
        
        self.vectorstore: Optional[QdrantVectorStore] = None

    def initialize_store(self, documents: List[Document] = None):
        """Initializes the Qdrant store. Creates new if documents provided, else loads existing."""
        if documents:
            self.vectorstore = QdrantVectorStore.from_documents(
                documents=documents,
                embedding=self.embeddings_model,
                sparse_embedding=self.sparse_embeddings,
                path=self.db_path,
                collection_name=self.collection_name,
                retrieval_mode=RetrievalMode.HYBRID,
            )
        else:
            # Load existing local storage
            self.vectorstore = QdrantVectorStore.from_existing_collection(
                embedding=self.embeddings_model,
                sparse_embedding=self.sparse_embeddings,
                path=self.db_path,
                collection_name=self.collection_name,
                retrieval_mode=RetrievalMode.HYBRID,
            )

    async def get_hybrid_reranked_docs(self, query: str, top_k: int = 3) -> List[RetrievedDoc]:
        if not self.vectorstore:
            self.initialize_store()

        # 1. Hybrid Retrieval
        initial_docs_with_score = await self.vectorstore.asimilarity_search_with_score(query, k=top_k)
        
        if not initial_docs_with_score:
            return []

        # 2. Re-ranking (Non-blocking)
        loop = asyncio.get_event_loop()
        passages = [doc.page_content for doc, _ in initial_docs_with_score]
        pairs = [[query, p] for p in passages]
        
        rerank_scores = await loop.run_in_executor(None, lambda: self.reranker.predict(pairs))

        # 3. Format and Sort
        final_output: List[RetrievedDoc] = []
        for i, (doc, score) in enumerate(initial_docs_with_score):        
            final_output.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "retrieval_score": float(score),
                "rerank_score": float(rerank_scores[i])
            })

        final_output.sort(key=lambda x: x["rerank_score"], reverse=True)
        print('-'*50)
        print("Reranked Results:")
        print(final_output)
        return final_output[:top_k]