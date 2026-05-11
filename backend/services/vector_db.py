from typing import List
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from langchain_core.documents import Document
from backend.core.state import RetrievedDoc
import asyncio

class VectorDBService:
    def __init__(
        self, 
        db_path: str = "./qdrant_db", 
        collection_name: str = "research_docs",
        # Using a highly efficient, lightweight model
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2" 
    ):
        self.db_path = db_path
        self.collection_name = collection_name
        
        # It handles the embedding generation locally with high optimization
        self.embeddings = FastEmbedEmbeddings(model_name=model_name)
        self.vectorstore = None

    def initialize_store(self, documents: List[Document] = None):
        """
        Creates a new collection if documents are passed, 
        otherwise loads the existing local database.
        """
        if documents:
            # This line generates embeddings AND stores them in Qdrant
            self.vectorstore = QdrantVectorStore.from_documents(
                documents=documents,
                embedding=self.embeddings,
                path=self.db_path,
                collection_name=self.collection_name,
                retrieval_mode=RetrievalMode.DENSE,
            )
        else:
            self.vectorstore = QdrantVectorStore.from_existing_collection(
                embedding=self.embeddings,
                path=self.db_path,
                collection_name=self.collection_name,
                retrieval_mode=RetrievalMode.DENSE,
            )

    async def search_docs(self, query: str, top_k: int = 3):
        """Simple semantic search without reranking."""
        if not self.vectorstore:
            self.initialize_store()
            
        docs_with_scores = await self.vectorstore.asimilarity_search_with_score(query, k=top_k) 
            
        final_output: List[RetrievedDoc] = []
        for doc, score in docs_with_scores:         
            final_output.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "retrieval_score": float(score),
                "rerank_score": 0.0
            })
        
        print(final_output)
        return final_output


# # For local testing
# if __name__ == "__main__":
#     service = VectorDBService()
#     # Ensure you have a dummy file or update path to test

#     raw_docs = [
#     Document(
#         page_content="# Quarterly Financial Overview\nThis report outlines the fiscal performance for Q3 2024, focusing on regional growth and operational expenses.",
#         metadata={
#             "source": "financial_report.pdf",
#             "chunk_id": 0,
#             "heading": "Quarterly Financial Overview"
#         }
#     ),
#     Document(
#         page_content="| Department | Budget | Actual | Variance |\n|---|---|---|---|\n| Marketing | $50,000 | $48,500 | -$1,500 |\n| Engineering | $120,000 | $125,000 | +$5,000 |\n| Sales | $75,000 | $70,000 | -$5,000 |",
#         metadata={
#             "source": "financial_report.pdf",
#             "chunk_id": 1,
#             "heading": "Expenditure Table"
#         }
#     ),
#     Document(
#         page_content="## Key Takeaways\nOverall, the company remains under budget by 2% despite the slight overage in the Engineering department due to cloud infrastructure scaling.",
#         metadata={
#             "source": "financial_report.pdf",
#             "chunk_id": 2,
#             "heading": "Key Takeaways"
#         }
#     )
# ]
#     service.initialize_store(documents=raw_docs)
#     asyncio.run(service.search_docs("What department overspent?"))