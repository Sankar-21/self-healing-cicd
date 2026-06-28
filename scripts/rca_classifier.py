import os
import re
import joblib
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from training_data import TRAINING_DATA

MODEL_PATH = os.path.join(os.path.dirname(__file__), "rca_model.pkl")

# ── Feature extraction ───────────────────────────────────

def extract_features(log_text):
    """Add keyword-based features on top of raw log text."""
    keywords = {
        "has_assert":      int(bool(re.search(r"assert|AssertionError", log_text, re.I))),
        "has_import":      int(bool(re.search(r"ModuleNotFoundError|ImportError|No module", log_text, re.I))),
        "has_syntax":      int(bool(re.search(r"SyntaxError|IndentationError|NameError", log_text, re.I))),
        "has_network":     int(bool(re.search(r"timeout|Connection refused|unavailable|ECONNREFUSED", log_text, re.I))),
        "has_auth":        int(bool(re.search(r"403|401|Forbidden|Unauthorized|permission denied", log_text, re.I))),
        "has_failed":      int(bool(re.search(r"FAILED|failed|failure", log_text, re.I))),
    }
    return log_text, keywords

# ── Train ────────────────────────────────────────────────

def train():
    print("🤖 Training RCA classifier...")

    texts  = [row[0] for row in TRAINING_DATA]
    labels = [row[1] for row in TRAINING_DATA]

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=500)),
        ("clf",   DecisionTreeClassifier(max_depth=10, random_state=42))
    ])

    model.fit(X_train, y_train)

    print("\n📊 Evaluation on test set:")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, zero_division=0))

    joblib.dump(model, MODEL_PATH)
    print(f"✅ Model saved to {MODEL_PATH}")
    return model

# ── Predict ──────────────────────────────────────────────

def predict(log_text):
    if not os.path.exists(MODEL_PATH):
        print("⚠️  Model not found. Training now...")
        train()

    model    = joblib.load(MODEL_PATH)
    category = model.predict([log_text])[0]
    proba    = model.predict_proba([log_text])[0]
    confidence = round(max(proba) * 100, 1)

    return category, confidence

if __name__ == "__main__":
    train()

    # Quick smoke test
    print("\n🧪 Sample predictions:")
    samples = [
        "FAILED tests/test_main.py AssertionError assert 404 == 200",
        "ModuleNotFoundError: No module named 'fastapi'",
        "SyntaxError: invalid syntax line 5",
        "Connection refused localhost timeout",
        "401 Unauthorized invalid token",
    ]
    for s in samples:
        cat, conf = predict(s)
        print(f"  [{conf}%] {cat:20s} ← {s[:55]}")