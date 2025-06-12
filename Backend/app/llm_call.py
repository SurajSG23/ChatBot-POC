import os
import openai
from dotenv import load_dotenv
import httpx
httpx_client = httpx.Client(verify=False)
load_dotenv()

client = openai.OpenAI(
            base_url = os.getenv("BASE_URL"),
            api_key = os.getenv("API_KEY"),
            http_client=httpx_client
        )

def get_chat_completion(prompt,model_str):
    completion = client.chat.completions.create(
        model = model_str,
        messages=[
            {"role": "system", "content": "You are a helpful and professional customer support agent. Your job is to assist users with their queries using the context provided If the user prompt doesn't have any link with the context then disregard the context and instead provide a general yet accurate response based solely on your own knowledge. Always be clear, concise, and friendly. If the context is insufficient, respond based on general knowledge, but prioritize the context when available."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=1024
        )
    return completion.choices[0].message.content




# {"role": "system", "content":"You are a knowledgeable and professional virtual assistant developed for Deloitte India. Your role is to provide accurate, concise, and context-aware responses that reflect Deloitte's commitment to excellence, integrity, and client service."},
# {"role": "user", "content": prompt}