
import json
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "data" / "intents.json"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_FILE = MODEL_DIR / "intent_classifier.joblib"


def load_dataset():
    """Load training patterns and their intent labels."""
    with DATA_FILE.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    texts = []
    labels = []
    seen = set()

    for intent in dataset["intents"]:
        tag = intent["tag"]

        # Fallback is handled using model confidence, not trained as an intent.
        if tag == "fallback":
            continue

        for pattern in intent["patterns"]:
            pattern = pattern.strip()

            if not pattern:
                continue

            key = (pattern.casefold(), tag)

            if key not in seen:
                texts.append(pattern)
                labels.append(tag)
                seen.add(key)

    if len(set(labels)) < 2:
        raise ValueError("At least two distinct intents are required.")

    counts = {tag: labels.count(tag) for tag in set(labels)}

    if min(counts.values()) < 5:
        raise ValueError(
            "Each intent needs at least five unique examples."
        )

    return texts, labels


def train_model():
    """Train, evaluate, and save the intent classifier."""
    texts, labels = load_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.25,
        random_state=42,
        stratify=labels,
    )

    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                strip_accents="unicode",
                ngram_range=(1, 2),
                sublinear_tf=True,
            ),
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42,
            ),
        ),
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print("\n========== NLP CHATBOT MODEL RESULTS ==========")
    print(f"Total examples: {len(texts)}")
    print(f"Training examples: {len(X_train)}")
    print(f"Testing examples: {len(X_test)}")
    print(f"Number of intents: {len(set(labels))}")
    print(f"Test accuracy: {accuracy_score(y_test, predictions):.4f}")

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_FILE)

    print(f"\nModel saved successfully: {MODEL_FILE}")


if __name__ == "__main__":
    train_model()
