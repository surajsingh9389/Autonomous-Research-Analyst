from engine.data_manager import run_full_ingestion
from engine.graph import graph
import asyncio

async def main():
    # 1. POPULATE THE BRAIN
    print("--- Phase 1: Ingesting Data ---")
    file_to_process = "raw_data.txt"
    await run_full_ingestion(file_to_process)
    
    # 2. RUN THE AGENT
    print("\n--- Phase 2: Running Agentic Research ---")
    inputs = {
        "query": "Summarize the project in the uploaded document.",
        "iteration": 0,
        "max_iterations": 3,
        "thoughts": []
    }
    
    # Use astream for that 2026 "live" feel
    async for event in graph.astream(inputs):
        for node_name, state_update in event.items():
            print(f"[{node_name}] is processing...")
            if "current_answer" in state_update:
                print(f"Result: {state_update['current_answer']}")

if __name__ == "__main__":
    asyncio.run(main())