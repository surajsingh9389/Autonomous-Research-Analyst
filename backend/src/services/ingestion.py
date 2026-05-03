from pathlib import Path
from typing import List
import asyncio

from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType  
# from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from docling.chunking import HybridChunker

class IngestionService:
    def __init__(self):
        # , chunk_size: int = 600, chunk_overlap: int = 100
        # self.text_splitter = RecursiveCharacterTextSplitter(
        #     chunk_size=chunk_size,
        #     chunk_overlap=chunk_overlap,
        #     separators=["\n\n", "\n", ".", " ", ""]
        # )
        
        pass 

    # async def ingest_and_chunk(self, file_path: str) -> List[Document]:
    #     """Loads a document, cleans metadata, and enriches content for RAG."""
        
    #     loader = DoclingLoader(file_path=file_path)
    #     raw_docs = await loader.aload() 
        
    #     final_cleaned_chunks = []
    #     chunk_count = 0 
    #     source_name = Path(file_path).name
        
    #     for doc in raw_docs:
    #         # Extract breadcrumbs from Docling metadata
    #         headings = doc.metadata.get("dl_meta", {}).get("headings", [])
    #         breadcrumb = " > ".join(headings)
            
    #         # Split the document
    #         sub_chunks = self.text_splitter.split_documents([doc])
            
    #         for chunk in sub_chunks:
    #             # --- PURGE AND REBUILD METADATA ---
    #             clean_metadata = {
    #                 "source": source_name,
    #                 "chunk_id": chunk_count,
    #             }
                
    #             # Add headers as top-level keys for easy filtering
    #             for idx, title in enumerate(headings):
    #                 clean_metadata[f"header_{idx+1}"] = title
                
    #             # Apply the clean metadata to the chunk
    #             chunk.metadata = clean_metadata
                
    #             # --- ENRICH CONTENT ---
    #             if breadcrumb:
    #                 chunk.page_content = f"Context: {breadcrumb}\n\n{chunk.page_content}"
                    
    #             final_cleaned_chunks.append(chunk)
    #             chunk_count += 1
        
    #     print("Final Chunks")
    #     print(final_cleaned_chunks)
        
    #     return final_cleaned_chunks
    
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
        return final_cleaned_chunks

# For local testing
if __name__ == "__main__":
    service = IngestionService()
    # Ensure you have a dummy file or update path to test
    # asyncio.run(service.ingest_and_chunk("raw_data.txt"))