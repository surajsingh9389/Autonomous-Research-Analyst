import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from pydantic import BaseModel

class EvalResponse(BaseModel):
    faithfulness_score: float
    relevance_score: float
    feedback: str

load_dotenv()

# Your Read Token 
HF_TOKEN = os.getenv("TOKEN")

# Initialize the client with your API token
client = InferenceClient(api_key=HF_TOKEN)

async def evaluate_answer(system_prompt: str, user_prompt: str) -> str:
    messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
    ]
    completion = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct", 
        messages=messages, 
        response_format={
            "type": "json_object",
            "schema": EvalResponse.model_json_schema(),
        },
        temperature=0.0
    )
    return completion.choices[0].message.content.strip()