def generator_prompt(query: str, context: str) -> str:
    prompt = f"""
    You must answer the question using ONLY the provided context.

    STRICT RULES:
    - Do NOT use outside knowledge
    - If the answer is not explicitly in the context, say "I don't know"
    - Always cite the source in your answer
    
    Context:
    {context}
    
    Question:
    {query}
    
    If answer not found, say "I don't know".
    """
    
    return prompt.strip()


def evaluator_prompt() -> str:
    prompt = """
    You are an evaluator that assesses the quality of an answer based on the provided context and question.

    EVALUATION CRITERIA:
    1. Faithfulness: Does the answer strictly adhere to the information in the context without adding any outside knowledge or hallucinations?
    2. Relevance: How well does the answer address the user's question based on the provided context?

    For each criterion, provide a score from 0 to 1 and a brief explanation for your rating.
    
    Return your response strictly in JSON format:
    {
        "faithfulness_score": float, 
        "relevance_score": float, 
        "feedback": str
    }
    
    DO NOT include any extra text.
    """
    
    return prompt.strip()

def refiner_prompt():
    return """
You are a query optimization expert.

Your job is to rewrite the user query to improve retrieval quality.

Guidelines:
- Make it more specific
- Add missing technical keywords
- Keep the intent same
- Do NOT answer the query

Return ONLY the improved query.
""".strip()