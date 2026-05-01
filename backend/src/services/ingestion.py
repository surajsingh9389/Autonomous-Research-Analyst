from pathlib import Path
from typing import List
import asyncio

from langchain_docling import DoclingLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class IngestionService:
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    async def ingest_and_chunk(self, file_path: str) -> List[Document]:
        """Loads a document, cleans metadata, and enriches content for RAG."""
        
        loader = DoclingLoader(file_path=file_path)
        raw_docs = await loader.aload() 
        
        final_cleaned_chunks = []
        chunk_count = 0 
        source_name = Path(file_path).name
        
        for doc in raw_docs:
            # Extract breadcrumbs from Docling metadata
            headings = doc.metadata.get("dl_meta", {}).get("headings", [])
            breadcrumb = " > ".join(headings)
            
            # Split the document
            sub_chunks = self.text_splitter.split_documents([doc])
            
            for chunk in sub_chunks:
                # --- PURGE AND REBUILD METADATA ---
                clean_metadata = {
                    "source": source_name,
                    "chunk_id": chunk_count,
                }
                
                # Add headers as top-level keys for easy filtering
                for idx, title in enumerate(headings):
                    clean_metadata[f"header_{idx+1}"] = title
                
                # Apply the clean metadata to the chunk
                chunk.metadata = clean_metadata
                
                # --- ENRICH CONTENT ---
                if breadcrumb:
                    chunk.page_content = f"Context: {breadcrumb}\n\n{chunk.page_content}"
                    
                final_cleaned_chunks.append(chunk)
                chunk_count += 1
        
        return final_cleaned_chunks

# For local testing
if __name__ == "__main__":
    service = IngestionService()
    # Ensure you have a dummy file or update path to test
    # asyncio.run(service.ingest_and_chunk("raw_data.txt"))