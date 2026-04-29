from langchain_docling import DoclingLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List

def ingest_and_chunk_pdf(file_path: str) -> List[Document]:
    """
    Loads a PDF using Docling, converts to Markdown, and chunks 
    while preserving header context.
    """
    
    # Load PDF and convert to Markdown
    # Docling is superior for preserving tables and headers
    loader = DoclingLoader(file_path=file_path)
    raw_docs = loader.load() # Usually returns 1 large Doc per file
    
    # Split by Markdown Headers
    # This ensures a chunk doesn't mix "Introduction" with "Conclusion"
    headers_to_split_on = [
        ("#", "Header_1"),
        ("##", "Header_2"),
        ("###", "Header_3"),
    ]
    
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False # Keep the '#' symbols for the LLM to see structure
    )
    
    # split_text returns a list of Document objects with header info in metadata
    semantic_chunks = header_splitter.split_text(raw_docs[0].page_content)
    
    print(semantic_chunks)
    
    # Sub-split large sections
    # If a section is 5000 words, we break it down further
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    final_chunks = text_splitter.split_documents(semantic_chunks)
    
    # Add the filename to metadata for your source tracking
    for chunk in final_chunks:
        chunk.metadata["file_name"] = file_path.split("/")[-1]
        
    print(f"Ingested {file_path}: Created {len(final_chunks)} chunks.")
    
    return final_chunks

# --- Usage Example ---
# chunks = ingest_and_chunk_pdf("research_paper.pdf")
# vectorstore.add_documents(chunks)