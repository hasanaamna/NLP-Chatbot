
import json
import random
from pathlib import Path

import joblib


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "data" / "intents.json"
MODEL_FILE = PROJECT_ROOT / "models" / "intent_classifier.joblib"

# Initial threshold; we will tune it using validation examples.
CONFIDENCE_THRESHOLD = 0.40


class NLPChatbot:
    def __init__(self):
        if not MODEL_FILE.exists():
            raise FileNotFoundError(
                "Trained model not found. Run: python -m src.nlp.train"
            )

        if not DATA_FILE.exists():
            raise FileNotFoundError(
                f"Intent dataset not found: {DATA_FILE}"
            )

        self.model = joblib.load(MODEL_FILE)

        with DATA_FILE.open("r", encoding="utf-8") as file:
            dataset = json.load(file)

        self.intents = {
            intent["tag"]: intent
            for intent in dataset["intents"]
        }

        self.fallback_responses = self.intents.get(
            "fallback",
            {
                "responses": [
                    "I'm not sure I understand. Could you rephrase that?"
                ]
            },
        )["responses"]

    def get_response(self, message):
        """Predict the intent and return an appropriate response."""
        if not isinstance(message, str) or not message.strip():
            return {
                "intent": "fallback",
                "confidence": 0.0,
                "response": "Please enter a message so I can help you.",
            }

        probabilities = self.model.predict_proba([message])[0]
        classes = self.model.classes_

        best_index = probabilities.argmax()
        predicted_intent = str(classes[best_index])
        confidence = float(probabilities[best_index])

        # Use a fallback when the model is not sufficiently confident.
        if confidence < CONFIDENCE_THRESHOLD:
            return {
                "intent": "fallback",
                "confidence": round(confidence, 4),
                "response": random.choice(self.fallback_responses),
            }

        intent_data = self.intents.get(predicted_intent)

        if not intent_data or not intent_data.get("responses"):
            return {
                "intent": "fallback",
                "confidence": round(confidence, 4),
                "response": random.choice(self.fallback_responses),
            }

        return {
            "intent": predicted_intent,
            "confidence": round(confidence, 4),
            "response": random.choice(intent_data["responses"]),
        }


def main():
    chatbot = NLPChatbot()

    print("\n===================================")
    print("       NLP CHATBOT")
    print("===================================")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nChatbot: Goodbye!")
            break

        if message.casefold() in {"exit", "quit"}:
            print("Chatbot: Goodbye!")
            break

        result = chatbot.get_response(message)

        print(f"Chatbot: {result['response']}")
        print(
            f"[Intent: {result['intent']} | "
            f"Confidence: {result['confidence']:.2f}]\n"
        )


if __name__ == "__main__":
    main()
