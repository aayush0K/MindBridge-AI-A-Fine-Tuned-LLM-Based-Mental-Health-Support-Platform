"""
MentalHealthEmbedder — Core AI component
Implements the IEEE ICDSBS 2025 paper methodology:
- all-MiniLM-L6-v2 sentence embeddings (384-dim)
- Cosine similarity with 0.4 relevance threshold
- Few-shot retrieval (top-K=3)
- Embedding-based crisis detection (0.7 threshold)
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MentalHealthEmbedder:
    MODEL_NAME = "all-MiniLM-L6-v2"
    RELEVANCE_THRESHOLD = 0.25  # Lowered from 0.4 — short phrases score lower against longer corpus text
    TOP_K = 3                   # Number of few-shot examples to retrieve
    CRISIS_THRESHOLD = 0.7      # High similarity to crisis vectors

    def __init__(self):
        self.model: SentenceTransformer | None = None
        self.corpus_data: list[dict] = []
        self.corpus_embeddings: np.ndarray | None = None
        self.crisis_embeddings: np.ndarray | None = None
        self._loaded = False

    def initialize(self):
        """Load the sentence transformer model. Called once at startup."""
        logger.info(f"[Embedder] Loading model: {self.MODEL_NAME}")
        self.model = SentenceTransformer(self.MODEL_NAME)
        logger.info("[Embedder] Model loaded successfully.")

    def load_corpus(self, corpus_path: str):
        """Load corpus JSON and pre-compute all embeddings at startup."""
        path = Path(corpus_path)
        if not path.exists():
            logger.warning(f"[Embedder] Corpus not found at {corpus_path}. Operating without corpus.")
            return

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        self.corpus_data = data
        contexts = [item["context"] for item in data]

        # Pre-computed embeddings on disk to eliminate startup CPU & RAM spike
        emb_file = path.parent / "corpus_embeddings.npy"
        crisis_file = path.parent / "crisis_embeddings.npy"

        if emb_file.exists():
            logger.info("[Embedder] Loading pre-computed embeddings from disk (instant, 0 RAM spike)...")
            self.corpus_embeddings = np.load(str(emb_file))
            if crisis_file.exists():
                self.crisis_embeddings = np.load(str(crisis_file))
        else:
            logger.info(f"[Embedder] Computing embeddings for {len(contexts)} corpus entries...")
            self.corpus_embeddings = self.model.encode(
                contexts,
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=32,
            )
            crisis_items = [d for d in data if d.get("category") == "crisis"]
            if crisis_items:
                self.crisis_embeddings = self.model.encode(
                    [c["context"] for c in crisis_items],
                    normalize_embeddings=True,
                )

        self._loaded = True
        logger.info(f"[Embedder] Loaded {len(data)} corpus entries ({len(crisis_items)} crisis).")

    def embed(self, text: str) -> np.ndarray:
        """Embed a single text string into a 384-dim normalized vector."""
        if self.model is None:
            self.initialize()
        return self.model.encode([text], normalize_embeddings=True)[0]

    def check_relevance(self, query_vec: np.ndarray) -> tuple[bool, float]:
        """
        Returns (is_relevant, max_similarity_score).
        Uses 0.4 threshold from IEEE paper.
        """
        if self.corpus_embeddings is None or len(self.corpus_embeddings) == 0:
            # Fallback: no corpus loaded, allow all messages
            return True, 0.5

        sims = cosine_similarity([query_vec], self.corpus_embeddings)[0]
        max_sim = float(np.max(sims))
        return max_sim >= self.RELEVANCE_THRESHOLD, max_sim

    def check_crisis_embedding(self, query_vec: np.ndarray) -> bool:
        """Embedding-based crisis check (complements keyword check)."""
        if self.crisis_embeddings is None or len(self.crisis_embeddings) == 0:
            return False
        sims = cosine_similarity([query_vec], self.crisis_embeddings)[0]
        return float(np.max(sims)) >= self.CRISIS_THRESHOLD

    def get_few_shot_examples(self, query_vec: np.ndarray) -> list[dict]:
        """Retrieve top-K most semantically similar corpus entries."""
        if self.corpus_embeddings is None or len(self.corpus_embeddings) == 0:
            return []

        sims = cosine_similarity([query_vec], self.corpus_embeddings)[0]
        top_indices = np.argsort(sims)[::-1][:self.TOP_K]
        return [self.corpus_data[i] for i in top_indices]

    def get_few_shot_examples_by_category(
        self, query_vec: np.ndarray, category: str | None, top_k: int | None = None
    ) -> list[dict]:
        """
        Category-aware retrieval, used when the trained classifier (Phase 2/3)
        is confident about a predicted category. Retrieves top-K examples
        FROM THAT CATEGORY ONLY, ranked by cosine similarity within it.

        Falls back to the original full-corpus behavior (get_few_shot_examples)
        if: category is None, unknown, "crisis" (crisis examples are never used
        as few-shot generation examples), or has fewer than top_k entries.
        """
        top_k = top_k or self.TOP_K
        if self.corpus_embeddings is None or len(self.corpus_embeddings) == 0:
            return []

        if category and category != "crisis":
            cat_indices = [
                i for i, d in enumerate(self.corpus_data) if d.get("category") == category
            ]
            if len(cat_indices) >= top_k:
                cat_embeddings = self.corpus_embeddings[cat_indices]
                sims = cosine_similarity([query_vec], cat_embeddings)[0]
                top_local = np.argsort(sims)[::-1][:top_k]
                return [self.corpus_data[cat_indices[i]] for i in top_local]

        # Fallback: original full-corpus cosine similarity
        return self.get_few_shot_examples(query_vec)


# Singleton — initialized once at FastAPI startup
embedder = MentalHealthEmbedder()
