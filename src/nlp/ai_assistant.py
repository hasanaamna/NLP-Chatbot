
import os
import uuid
from collections import defaultdict
from threading import RLock

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

SYSTEM_PROMPT = """
You are a helpful, friendly, intelligent AI assistant.

Guidelines:
- Answer the user's question directly and clearly.
- Explain difficult concepts step by step when useful.
- Help with programming, debugging, writing, learning, and general questions.
- Use the conversation history to understand follow-up questions.
- If you are uncertain, be honest rather than inventing facts.
- Use readable formatting and code blocks when appropriate.
"""


class AIAssistant:
    """Groq-powered assistant with in-memory conversation context."""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.model = os.getenv(
            "GROQ_MODEL", "llama-3.3-70b-versatile"
        ).strip()

        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.conversations = defaultdict(list)
        self.lock = RLock()

    def get_response(self, message: str, conversation_id: str | None = None):
        if not self.client:
            raise RuntimeError(
                "Groq API key is missing. Configure GROQ_API_KEY in .env."
            )

        message = message.strip()
        if not message:
            raise ValueError("Message cannot be empty.")

        # Create a new conversation if the client did not provide an ID.
        conversation_id = conversation_id or str(uuid.uuid4())

        with self.lock:
            history = list(self.conversations[conversation_id])

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": message},
        ]

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1500,
        )

        answer = completion.choices[0].message.content
        if not answer or not answer.strip():
            raise RuntimeError("The AI provider returned an empty response.")

        # Keep the most recent 10 exchanges in memory.
        updated_history = [
            *history,
            {"role": "user", "content": message},
            {"role": "assistant", "content": answer.strip()},
        ][-20:]

        with self.lock:
            self.conversations[conversation_id] = updated_history

        return {
            "conversation_id": conversation_id,
            "response": answer.strip(),
            "model": self.model,
        }
