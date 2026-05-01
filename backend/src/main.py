# import asyncio
# from typing import List, Literal, TypedDict
# from langgraph.graph import StateGraph, START, END
# from backend.src.hybrid_search import get_hybrid_reranked_docs
# from backend.src.build_prompt import generator_prompt, evaluator_prompt, refiner_prompt
# from backend.src.generator import generateAnswer
# from backend.src.evaluator import evaluate_answer
# import json


# TOP_K = 3

# # Document structure to hold retrieved information along with its source and scores for retrieval and reranking.
# class RetrievedDoc(TypedDict):
#     content: str
#     source: str
#     retrieval_score: float
#     rerank_score: float

# # State Schema for the agent, capturing all relevant information across the different stages of the process.
# class AgentState(TypedDict):
#     # --- Input ---
#     query: str
#     iteration: int
#     max_iterations: int

#     # --- Retrieval ---
#     retrieved_docs: List[RetrievedDoc]

#     # --- Generation ---
#     current_answer: str

#     # --- Evaluation ---
#     faithfulness_score: float
#     relevance_score: float
#     feedback: str
#     failure_type: Literal[
#         "hallucination",
#         "low_relevance",
#         "good"
#     ]
    
#     # Low relevance score refine query 
#     refined_query: str
    
#     # # Planner state 
#     plan: Literal[
#     "direct_answer",
#     "retrieve" 
#     ]
    
#     #  --- Observability ---
#     thoughts: List[str]
    
# async def planner(state: AgentState) -> AgentState:
#     query = state["query"].lower()
    
#     # Simple heuristics
#     retrieval_keywords = [
#         "document", "pdf", "file", "uploaded",
#         "according to", "in the document",
#         "based on", "from the text"
#     ]
    
#     if any(keyword in query for keyword in retrieval_keywords):
#         state["plan"] = "retrieve"
#     else:
#         state["plan"] = "direct_answer"
    
#     state.setdefault("thoughts", []).append(
#         f"Planner decided: {state['plan']}"
#     )
    
#     return state
    

# async def retriever_node(state: AgentState):
#     query = state["query"]
#     # We AWAIT the result here
#     processed_docs = await get_hybrid_reranked_docs(query)
    
#     return {"retrieved_docs": processed_docs}

# async def generator(state: AgentState) -> AgentState:    
#     # This function would typically use the retrieved documents to generate an answer to the query.
#     query = state["query"]
    
#     if state["plan"] == "direct_answer":
#         system_prompt = "Answer the question directly:"
#         user_prompt = f"Question: {query}"
#         answer = await generateAnswer(system_prompt, user_prompt)
        
#         state["current_answer"] = answer
#         return state
    
#     docs = state["retrieved_docs"]
    
#     # If retrieval fails:
#     if not docs:
#         state["current_answer"] = "I don't know"
#         return state
    
#     context = "\n\n".join([f"{doc['content']} (source: {doc['source']})" for doc in docs[:TOP_K]]) 
    
#     system_prompt = "You are a helpful AI assistant that answers strictly from provided context."
#     user_prompt = generator_prompt(query, context)
#     answer = await generateAnswer(system_prompt, user_prompt)
    
#     state['current_answer'] = answer
    
#     state.setdefault("thoughts", []).append(
#         f"Generated answer using top {len(docs[:TOP_K])} docs"
#     )
    
#     return state

# async def critic(state: AgentState) -> AgentState:
#     """
#     Evaluates the generated answer for faithfulness to context 
#     and relevance to the user query.
#     """
#     state["iteration"] = state["iteration"] + 1
    
#     # Extract necessary data from state
#     query = state["query"]
    
#     # Information from Retriever
#     docs = state["retrieved_docs"]
#     context = "\n\n".join([f"{doc['content']} (source: {doc['source']})" for doc in docs[:TOP_K]]) 
    
#     # Information from Generator
#     answer = state["current_answer"] 
    
#     # Build evaluation prompt
#     system_prompt = evaluator_prompt()
#     user_prompt = f"QUERY: {query}\n\nCONTEXT: {context}\n\nANSWER: {answer}"
    
#     # Call the LLM to evaluate the answer
#     evaluation_response = await evaluate_answer(system_prompt, user_prompt)
    
#     # Parse the scores and feedback from the LLM's response
#     score = json.loads(evaluation_response)
    
#     state["faithfulness_score"] = score.get("faithfulness_score", 0.0)
#     state["relevance_score"] = score.get("relevance_score", 0.0)
#     state["feedback"] = score.get("feedback", "")
    
#     print("Iteration", state['iteration'])
#     print(f"Evaluation → Faithfulness: {state['faithfulness_score']}, Relevance: {state['relevance_score']}, Feedback: {state['feedback']}")
    
    
#     # Determine failure type based on scores 
#     if state['faithfulness_score'] < 0.7:
#         state['failure_type'] = "hallucination"
#     elif state['relevance_score'] < 0.7:
#         state['failure_type'] = "low_relevance"
#     else:
#         state['failure_type'] = "good"
        
#     state["thoughts"].append(
#     f"Critic → faithfulness: {state['faithfulness_score']}, relevance: {state['relevance_score']}"
#     )
        
#     return state

# async def refiner(state: AgentState) -> AgentState:
#     original_query = state["query"]
#     feedback = state.get("feedback", "")

#     user_prompt = f"""
# Original Query:
# {original_query}

# Feedback from system:
# {feedback}

# Improve the query for better document retrieval.
# """
#     system_prompt = refiner_prompt()
#     improved_query = await generateAnswer(system_prompt, user_prompt)

#     state["refined_query"] = improved_query
#     state["query"] = improved_query  # overwrite for next loop

#     state.setdefault("thoughts", []).append(
#         f"Refined query: {improved_query}"
#     )

#     return state


# def should_continue(state: AgentState):
#     if state["iteration"] >= state["max_iterations"]:
#         return "end"
    
#     if state["failure_type"] == "good":
#         return "end"
    
#     if state["failure_type"] == "low_relevance":
#         return "refiner"

#     if state["failure_type"] == "hallucination":
#         return "retriever"
    
#     return "retry"

# def route_from_planner(state: AgentState):
#     if state["plan"] == "direct_answer":
#         return "generator"
#     return "retriever"


# agent_builder = StateGraph(AgentState)

# agent_builder.add_node("planner", planner)
# agent_builder.add_node("retriever", retriever_node)
# agent_builder.add_node("generator", generator)
# agent_builder.add_node("critic", critic)
# agent_builder.add_node("refiner", refiner)

# agent_builder.add_edge(START, "planner")
# agent_builder.add_conditional_edges(
#     "planner",
#     route_from_planner,
#     {
#         "generator": "generator",
#         "retriever": "retriever"
#     }
# )
# agent_builder.add_edge("retriever", "generator")
# agent_builder.add_edge("generator", "critic")
# agent_builder.add_conditional_edges("critic", should_continue, { "end": END, "retriever": "retriever", "refiner": "refiner"})
# agent_builder.add_edge("refiner", "retriever")

# graph = agent_builder.compile()

# async def run_agent():
#     # Use AINVOKE instead of INVOKE
#     state = await graph.ainvoke({
#         "query": "What is FAISS", 
#         "iteration": 0, 
#         "max_iterations": 3,
#         "thoughts": []
#     })
#     print(state)

# # 3. Run the async loop
# if __name__ == "__main__":
#     asyncio.run(run_agent())
    
    
    
import asyncio
from engine.data_manager import run_full_ingestion
from engine.graph import graph

async def main():
    # 1. POPULATE THE BRAIN
    print("--- Phase 1: Ingesting Data ---")
    file_to_process = "raw_data.txt"
    await run_full_ingestion(file_to_process)
    
    # 2. RUN THE AGENT
    print("\n--- Phase 2: Running Agentic Research ---")
    inputs = {
        "query": "Summarize the key findings in the uploaded document.",
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