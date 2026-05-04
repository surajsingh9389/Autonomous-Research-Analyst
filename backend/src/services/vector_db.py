import asyncio
import requests
from typing import List, Optional
from core.state import RetrievedDoc

from langchain_qdrant import QdrantVectorStore, RetrievalMode
from langchain_community.embeddings import HuggingFaceInferenceEmbeddings
from langchain_core.documents import Document

class VectorDBService:
    def __init__(
        self, 
        hf_token: str,
        db_path: str = "./qdrant_db", 
        collection_name: str = "research_docs",
        # We specify the model names to ensure the API uses the right dimensions
        dense_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        self.db_path = db_path
        self.collection_name = collection_name
        self.hf_token = hf_token
        self.rerank_model = rerank_model
        
        # 1. API-based Embeddings (Instant startup, 0MB RAM)
        self.embeddings_model = HuggingFaceInferenceEmbeddings(
            api_key=hf_token,
            model_name=dense_model
        )
        
        # Qdrant local storage still works the same, but uses the API for math
        self.vectorstore: Optional[QdrantVectorStore] = None

    def initialize_store(self, documents: List[Document] = None):
        """Initializes Qdrant. No heavy model loading happens here."""
        if documents:
            self.vectorstore = QdrantVectorStore.from_documents(
                documents=documents,
                embedding=self.embeddings_model,
                path=self.db_path,
                collection_name=self.collection_name,
                retrieval_mode=RetrievalMode.DENSE, # Using Dense for API simplicity
            )
        else:
            self.vectorstore = QdrantVectorStore.from_existing_collection(
                embedding=self.embeddings_model,
                path=self.db_path,
                collection_name=self.collection_name,
            )

    async def _get_api_rerank_scores(self, query: str, passages: List[str]) -> List[float]:
        """Calls Hugging Face Inference API for reranking."""
        api_url = f"https://api-inference.huggingface.co/models/{self.rerank_model}"
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        payload = {
            "inputs": {
                "source_sentence": query,
                "sentences": passages
            }
        }

        # Run the request in a thread to keep FastAPI async
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None, 
                lambda: requests.post(api_url, headers=headers, json=payload, timeout=10)
            )
            response.raise_for_status()
            # HF returns a list of dicts: [{'label': 'LABEL_0', 'score': 0.99}, ...]
            # or a simple list of scores depending on the model
            scores = response.json()
            return [s['score'] for s in scores] if isinstance(scores[0], dict) else scores
        except Exception as e:
            print(f"Reranking API Error: {e}")
            return [0.0] * len(passages)

    async def get_hybrid_reranked_docs(self, query: str, top_k: int = 3) -> List[RetrievedDoc]:
        if not self.vectorstore:
            self.initialize_store()

        # 1. Retrieve documents via API-powered Vector Search
        initial_docs_with_score = await self.vectorstore.asimilarity_search_with_score(query, k=top_k)
        
        if not initial_docs_with_score:
            return []

        # 2. Extract content for Reranking
        passages = [doc.page_content for doc, _ in initial_docs_with_score]
        
        # 3. Get scores from API instead of local CrossEncoder
        rerank_scores = await self._get_api_rerank_scores(query, passages)

        # 4. Format and Sort
        final_output: List[RetrievedDoc] = []
        for i, (doc, score) in enumerate(initial_docs_with_score):         
            final_output.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "retrieval_score": float(score),
                "rerank_score": float(rerank_scores[i]) if i < len(rerank_scores) else 0.0
            })

        final_output.sort(key=lambda x: x["rerank_score"], reverse=True)
        return final_output[:top_k]