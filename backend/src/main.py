# from engine.data_manager import run_full_ingestion
from engine import graph

import os
from pydantic import BaseModel
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from engine.data_manager import run_full_ingestion
app = FastAPI(title="Personal Knowledge Agent")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    
 
@app.get('/')
async def health_check():
    return {"status": "ok", "message": "Personal Knowledge Agent is running!"}    

@app.post("/ingest", tags=["Ingestion"])
async def ingest_data(file: UploadFile = File(...)):
    """
    Step 1: Save file locally, Chunk with Docling, and Upsert to Qdrant.
    """
    temp_path = f"temp_{file.filename}"
    try:
        # Save temp file
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        message = run_full_ingestion(temp_path)
        
        return {"status": "success", "message": message}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/ask", response_model=QueryResponse, tags=["Agent"])
async def ask_researcher(request: QueryRequest):
    """
    Step 2: Invoke the LangGraph researcher agent.
    """
    try:
        # Initial state for your LangGraph
        
        inputs = {
        "query": request.query,
        "iteration": 0,
        "max_iterations": 3,
        "thoughts": []
        }
        
        # Run the graph
        final_state = await graph.ainvoke(inputs)
        
        # Extract the last message from the agent
        answer = final_state["current_answer"]
        
        return QueryResponse(
            answer=answer,
            sources=[] # You can extract source metadata from the state if needed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)

# async def main():
#     # 1. POPULATE THE BRAIN
#     print("--- Phase 1: Ingesting Data ---")
#     file_to_process = "raw_data.txt"
#     await run_full_ingestion(file_to_process)
    
#     # 2. RUN THE AGENT
#     print("\n--- Phase 2: Running Agentic Research ---")
#     inputs = {
        
#         "query": "summarize my document",
#         "iteration": 0,
#         "max_iterations": 3,
#         "thoughts": []
#     }
    
#     # Use astream for that 2026 "live" feel
#     async for event in graph.astream(inputs):
#         for node_name, state_update in event.items():
#             print(f"[{node_name}] is processing...")
#             if "current_answer" in state_update:
#                 print(f"Result: {state_update['current_answer']}")

# if __name__ == "__main__":
#     asyncio.run(main())