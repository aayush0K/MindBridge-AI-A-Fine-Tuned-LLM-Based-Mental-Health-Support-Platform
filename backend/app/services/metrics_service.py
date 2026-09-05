"""
Metrics Service — Tracks semantic response caching performance, latencies,
hit rates, and avoided GPU compute.
"""

from __future__ import annotations

import logging
import threading
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class CacheMetricsTracker:
    """Thread-safe in-memory metrics tracker for Semantic Response Caching."""

    def __init__(self, max_recent: int = 100):
        self._lock = threading.Lock()
        self.max_recent = max_recent
        self.total_queries: int = 0
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self.gpu_calls_avoided: int = 0

        # Rolling latency collections (in milliseconds)
        self.lookup_latencies: List[float] = []
        self.embedding_latencies: List[float] = []
        self.llama_latencies: List[float] = []
        self.similarity_scores: List[float] = []

    def record_hit(self, similarity_score: float, lookup_latency_ms: float) -> None:
        with self._lock:
            self.total_queries += 1
            self.cache_hits += 1
            self.gpu_calls_avoided += 1
            self.lookup_latencies.append(round(lookup_latency_ms, 2))
            self.similarity_scores.append(round(similarity_score, 4))
            if len(self.lookup_latencies) > self.max_recent:
                self.lookup_latencies.pop(0)
            if len(self.similarity_scores) > self.max_recent:
                self.similarity_scores.pop(0)

        logger.info(
            f"[SemanticCache] HIT | Score: {similarity_score:.4f} | "
            f"Lookup: {lookup_latency_ms:.2f}ms | GPU Call Avoided! (Total Avoided: {self.gpu_calls_avoided})"
        )

    def record_miss(self, lookup_latency_ms: float) -> None:
        with self._lock:
            self.total_queries += 1
            self.cache_misses += 1
            self.lookup_latencies.append(round(lookup_latency_ms, 2))
            if len(self.lookup_latencies) > self.max_recent:
                self.lookup_latencies.pop(0)

        logger.info(
            f"[SemanticCache] MISS | Lookup: {lookup_latency_ms:.2f}ms | Routing to Llama 3 remote GPU."
        )

    def record_embedding_latency(self, latency_ms: float) -> None:
        with self._lock:
            self.embedding_latencies.append(round(latency_ms, 2))
            if len(self.embedding_latencies) > self.max_recent:
                self.embedding_latencies.pop(0)

    def record_llama_latency(self, latency_ms: float) -> None:
        with self._lock:
            self.llama_latencies.append(round(latency_ms, 2))
            if len(self.llama_latencies) > self.max_recent:
                self.llama_latencies.pop(0)

    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            total = self.total_queries
            hit_rate = round((self.cache_hits / total) * 100, 2) if total > 0 else 0.0

            avg_lookup = (
                round(sum(self.lookup_latencies) / len(self.lookup_latencies), 2)
                if self.lookup_latencies
                else 0.0
            )
            avg_embedding = (
                round(sum(self.embedding_latencies) / len(self.embedding_latencies), 2)
                if self.embedding_latencies
                else 0.0
            )
            avg_llama = (
                round(sum(self.llama_latencies) / len(self.llama_latencies), 2)
                if self.llama_latencies
                else 0.0
            )
            avg_similarity = (
                round(sum(self.similarity_scores) / len(self.similarity_scores), 4)
                if self.similarity_scores
                else 0.0
            )

            return {
                "total_queries": total,
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "gpu_calls_avoided": self.gpu_calls_avoided,
                "hit_rate_percentage": hit_rate,
                "avg_cache_lookup_ms": avg_lookup,
                "avg_embedding_ms": avg_embedding,
                "avg_llama_inference_ms": avg_llama,
                "avg_hit_similarity_score": avg_similarity,
                "recent_samples_tracked": len(self.lookup_latencies),
            }

    def reset(self) -> None:
        with self._lock:
            self.total_queries = 0
            self.cache_hits = 0
            self.cache_misses = 0
            self.gpu_calls_avoided = 0
            self.lookup_latencies.clear()
            self.embedding_latencies.clear()
            self.llama_latencies.clear()
            self.similarity_scores.clear()


# Global shared singleton
cache_metrics = CacheMetricsTracker()
