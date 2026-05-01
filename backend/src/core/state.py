from typing import List, Literal, TypedDict

class RetrievedDoc(TypedDict):
    content: str
    source: str
    retrieval_score: float
    rerank_score: float

class AgentState(TypedDict):
    query: str
    iteration: int
    max_iterations: int
    retrieved_docs: List[RetrievedDoc]
    current_answer: str
    faithfulness_score: float
    relevance_score: float
    feedback: str
    failure_type: Literal["hallucination", "low_relevance", "good"]
    refined_query: str
    plan: Literal["direct_answer", "retrieve"]
    thoughts: List[str]