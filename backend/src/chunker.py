from langchain_docling import DoclingLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
import os
import asyncio


async def ingest_and_chunk_document(file_path: str) -> List[Document]:
    
    # Load the document using DoclingLoader
    loader = DoclingLoader(file_path=file_path)
    raw_docs = await loader.aload() 
    
    print("Raw Docs")
    print(raw_docs)
    print("__"*60)
    print("\n")
    
    final_cleaned_chunks = []
    
    # Unique Chunk ID Counter
    global_chunk_count = 0  
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    for doc in raw_docs:
        # Extract the essentials from the 'dirty' metadata
        headings = doc.metadata.get("dl_meta", {}).get("headings", [])
        breadcrumb = " > ".join(headings)
        source_name = os.path.basename(file_path)
        
        # Split the document
        sub_chunks = text_splitter.split_documents([doc])
        
        for chunk in sub_chunks:
            # --- PURGE AND REBUILD METADATA ---
            # We replace the bloated doc.metadata with a fresh, slim dictionary
            clean_metadata = {
                "source": source_name,
                "chunk_id": global_chunk_count
            }
            
            # Add headers as top-level keys for easy filtering
            for idx, title in enumerate(headings):
                clean_metadata[f"Header_{idx+1}"] = title
            
            # Apply the clean metadata to the chunk
            chunk.metadata = clean_metadata
            
            # --- ENRICH CONTENT ---
            # Prepend context to text for better vector search
            if breadcrumb:
                chunk.page_content = f"Context: {breadcrumb}\n\n{chunk.page_content}"
                
            final_cleaned_chunks.append(chunk)
            global_chunk_count += 1
            
    print("Final Cleaned Chunks")
    print(final_cleaned_chunks)

    return final_cleaned_chunks


# 3. Run the async loop
if __name__ == "__main__":
    asyncio.run(ingest_and_chunk_document("raw_data.txt"))