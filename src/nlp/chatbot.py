
import json
import random
from pathlib import Path

import joblib


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "data" / "intents.json"
MODEL_FILE = PROJECT_ROOT / "models" / "intent_classifier.joblib"

CONFIDENCE_THRESHOLD = 0.40


class NLPChatbot:
    def __init__(self):
        if not MODEL_FILE.exists():
            raise FileNotFoundError(
                "Model not found. Run: python -m src.nlp.train"
            )

        self.model = joblib.load(MODEL_FILE)

        with DATA_FILE.open("r", encoding="utf-8") as file:
            dataset = json.load(file)

        self.intents = {
            item["tag"]: item
            for item in dataset["intents"]
        }

        self.pattern_to_intent = {}

        for intent in dataset["intents"]:
            if intent["tag"] == "fallback":
                continue

            for pattern in intent["patterns"]:
                normalized = self.normalize(pattern)
                self.pattern_to_intent[normalized] = intent["tag"]

        self.fallback_responses = self.intents["fallback"]["responses"]

    @staticmethod
    def normalize(text):
        """Normalize text for exact phrase matching."""
        return " ".join(text.casefold().split()).strip()

    def get_response(self, message):
        if not isinstance(message, str) or not message.strip():
            return {
                "intent": "fallback",
                "confidence": 0.0,
                "method": "input_validation",
                "response": "Please enter a message so I can help you.",
            }

        normalized = self.normalize(message)

        # 1. Match known phrases directly.
        if normalized in self.pattern_to_intent:
            intent = self.pattern_to_intent[normalized]
            response = random.choice(self.intents[intent]["responses"])

            return {
                "intent": intent,
                "confidence": 1.0,
                "method": "exact_match",
                "response": response,
            }

        # 2. Use the trained model for other messages.
        probabilities = self.model.predict_proba([message])[0]
        classes = self.model.classes_

        best_index = probabilities.argmax()
        intent = str(classes[best_index])
        confidence = float(probabilities[best_index])

        if confidence < CONFIDENCE_THRESHOLD:
            return {
                "intent": "fallback",
                "confidence": round(confidence, 4),
                "method": "low_confidence",
                "response": random.choice(self.fallback_responses),
            }

        return {
            "intent": intent,
            "confidence": round(confidence, 4),
            "method": "model_prediction",
            "response": random.choice(self.intents[intent]["responses"]),
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
            f"Confidence: {result['confidence']:.2f} | "
            f"Method: {result['method']}]\n"
        )


if __name__ == "__main__":
    main()
