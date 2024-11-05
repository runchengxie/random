from openai import OpenAI
import os

PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY')

print(PERPLEXITY_API_KEY)

messages = [
    {
        "role": "system",
        "content": (
            "You are an artificial intelligence assistant and you need to "
            "engage in a helpful, detailed, polite conversation with a user."
        ),
    },
    {
        "role": "user",
        "content": (
            "How many stars are in the universe?"
        ),
    },
]


client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")

# chat completion without streaming
response = client.chat.completions.create(
    model="llama-3.1-sonar-small-128k-online",
    messages=messages,
)
print(response)