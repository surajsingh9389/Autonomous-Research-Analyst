import os
from typing import Optional
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from pydantic import BaseModel

# Move the schema here so it's reusable by the service
class EvalResponse(BaseModel):
    faithfulness_score: float
    relevance_score: float
    feedback: str

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("TOKEN")
        self.client = InferenceClient(api_key=self.api_key)
        # 2026 Pro-tip: Use different models for different tasks
        self.gen_model = "deepseek-ai/DeepSeek-V3"
        self.eval_model = "meta-llama/Llama-3.3-70B-Instruct"

    async def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """General purpose generation using DeepSeek."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        completion = self.client.chat.completions.create(
            model=self.gen_model,
            messages=messages,
            max_tokens=500,
            temperature=0.0
        )
        return completion.choices[0].message.content.strip()

    async def evaluate_structured(self, system_prompt: str, user_prompt: str) -> str:
        """
        Structured evaluation using Llama-3.3-70B.
        Ensures the output matches the EvalResponse schema perfectly.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        completion = self.client.chat.completions.create(
            model=self.eval_model,
            messages=messages,
            response_format={
                "type": "json_object",
                "schema": EvalResponse.model_json_schema(),
            },
            temperature=0.0
        )
        return completion.choices[0].message.content.strip()