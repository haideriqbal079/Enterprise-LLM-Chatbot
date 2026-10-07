from groq import Groq

from src.config import GROQ_API_KEY


class GroqService:
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not configured.")

        self.client = Groq(api_key=GROQ_API_KEY)

    def generate_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an internal company knowledge assistant. "
                        "Answer using the provided company knowledge. "
                        "If the information is not available in the provided "
                        "knowledge, clearly say that you do not have enough "
                        "information."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            max_tokens=500,
        )

        return response.choices[0].message.content