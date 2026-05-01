from ..services.ingestion import IngestionService
from ..services.vector_db import VectorDBService

# Create single instances to be shared across the app
ingestor = IngestionService()
vector_db = VectorDBService()

async def run_full_ingestion(file_path: str):
    """
    This function is the 'First Method' you mentioned.
    It connects the two services together.
    """
    # 1. Chunker
    chunks = await ingestor.ingest_and_chunk(file_path)
    
    # 2. Vector DB
    await vector_db.initialize_store(chunks)
    
    return f"Processed {len(chunks)} chunks from {file_path}"