"""
train_classifier.py
====================
Trains the MentalHealthClassifier on top of frozen all-MiniLM-L6-v2 embeddings
and saves the weights + label map for inference.

Usage
-----
    cd backend
    python scripts/train_classifier.py

Output
------
    app/models/classifier_weights.pt   ← PyTorch state dict
    app/models/label_map.json          ← category index ↔ name mapping

Notes
-----
- The embedding model (MiniLM) is NOT fine-tuned. All embeddings are computed
  once, cached, and reused across all epochs (fast training).
- Adjust EPOCHS, HIDDEN_DIM, DROPOUT_P here if experimenting. Keep
  CATEGORIES in sync with classifier.py to avoid inference mismatches.
- After training, restart the FastAPI server to load the new weights.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer

# ── Allow imports from app/ when run from the backend/ directory ──────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.classifier import MentalHealthClassifier, CATEGORIES

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
BACKEND_DIR   = Path(__file__).resolve().parent.parent
CORPUS_PATH   = BACKEND_DIR / "corpus" / "mental_health_corpus.json"
WEIGHTS_PATH  = BACKEND_DIR / "app" / "models" / "classifier_weights.pt"
LABEL_MAP_PATH = BACKEND_DIR / "app" / "models" / "label_map.json"

# ── Hyperparameters ───────────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EPOCHS          = 50
LEARNING_RATE   = 1e-3
BATCH_SIZE      = 32


def load_corpus() -> tuple[list[str], list[int]]:
    """Load corpus and return (texts, label_indices)."""
    with open(CORPUS_PATH, encoding="utf-8") as f:
        data = json.load(f)

    cat_to_idx = {cat: i for i, cat in enumerate(CATEGORIES)}
    texts, labels = [], []

    skipped = 0
    for item in data:
        cat = item.get("category")
        if cat not in cat_to_idx:
            skipped += 1
            continue
        texts.append(item["context"])
        labels.append(cat_to_idx[cat])

    logger.info(f"Loaded {len(texts)} training examples ({skipped} skipped — unknown category).")
    return texts, labels


def train() -> None:
    logger.info("Loading embedding model …")
    embedder = SentenceTransformer(EMBEDDING_MODEL)

    texts, labels = load_corpus()

    logger.info("Computing embeddings (once, cached) …")
    embeddings = embedder.encode(texts, normalize_embeddings=True, show_progress_bar=True)

    X = torch.tensor(embeddings, dtype=torch.float32)
    y = torch.tensor(labels, dtype=torch.long)

    model = MentalHealthClassifier()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.CrossEntropyLoss()

    logger.info(f"Training for {EPOCHS} epochs …")
    model.train()
    for epoch in range(1, EPOCHS + 1):
        # Mini-batch loop
        indices = torch.randperm(len(X))
        epoch_loss = 0.0
        for start in range(0, len(X), BATCH_SIZE):
            batch_idx = indices[start : start + BATCH_SIZE]
            xb, yb = X[batch_idx], y[batch_idx]
            optimizer.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        if epoch % 10 == 0 or epoch == 1:
            logger.info(f"  Epoch {epoch:3d}/{EPOCHS}  loss={epoch_loss:.4f}")

    # ── Save ──────────────────────────────────────────────────────────────────
    WEIGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), WEIGHTS_PATH)
    logger.info(f"Saved weights → {WEIGHTS_PATH}")

    label_map = {"categories": CATEGORIES}
    with open(LABEL_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2)
    logger.info(f"Saved label map → {LABEL_MAP_PATH}")

    # ── Quick accuracy check ──────────────────────────────────────────────────
    model.eval()
    with torch.no_grad():
        preds = torch.argmax(model(X), dim=1)
        acc = (preds == y).float().mean().item()
    logger.info(f"Training accuracy: {acc:.1%}")
    logger.info("Done. Restart the backend server to load the new weights.")


if __name__ == "__main__":
    train()
