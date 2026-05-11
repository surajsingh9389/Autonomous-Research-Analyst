from pathlib import Path
from typing import List
import asyncio

from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType  
from langchain_core.documents import Document
from docling.chunking import HybridChunker

class IngestionService:
    def __init__(self):
        pass
    
    async def ingest_and_chunk(self, file_path: str) -> List[Document]:
        """Uses Docling to export tables as Markdown to preserve row relationships."""
        
        # Initialize DoclingLoader with Markdown export enabled
        loader = DoclingLoader(
        file_path=file_path,
        export_type=ExportType.DOC_CHUNKS, # Tells Docling to handle the chunking
        chunker=HybridChunker(
        tokenizer="sentence-transformers/all-MiniLM-L6-v2", # Matches embedding model
        max_tokens=512,  
        merge_peers=True # Keeps related list items/table rows together
        )
    )
        
        raw_docs = await loader.aload() 
        
        final_cleaned_chunks = []
        source_name = Path(file_path).name
        
        for idx, doc in enumerate(raw_docs):
            # For small tables, we don't want to split them at all.
            # We want the WHOLE table in one chunk so the LLM sees the header + row.
            
            clean_metadata = {
                "source": source_name,
                "chunk_id": idx,
                "heading": doc.metadata.get("dl_meta", {}).get("headings", ["None"])[-1]
            }
            
            # Use the page_content directly from Docling's Markdown export
            doc.metadata = clean_metadata
            final_cleaned_chunks.append(doc)
        
        print("Final Chunks after Docling Processing:")
        print(final_cleaned_chunks)
        print('-'*70)
        return final_cleaned_chunks

# For local testing
if __name__ == "__main__":
    service = IngestionService()
    # Ensure you have a dummy file or update path to test
    asyncio.run(service.ingest_and_chunk("raw_data.txt"))