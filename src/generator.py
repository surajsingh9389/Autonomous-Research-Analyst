import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

# Your Read Token 
HF_TOKEN = os.getenv("TOKEN")

# Initialize the client with your API token
client = InferenceClient(api_key=HF_TOKEN)

async def generateAnswer(system_prompt: str, user_prompt: str) -> str:
    # Example for text generation
    messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
    ]
    completion = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3", 
        messages=messages, 
        max_tokens=100,
        temperature=0.0
    )
    return completion.choices[0].message.content.strip()