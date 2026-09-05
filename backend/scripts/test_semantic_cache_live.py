"""
Live End-to-End Test for Semantic Response Caching
===================================================
Tests live PostgreSQL storage, MiniLM embedding, cosine similarity lookup,
crisis pre-emption, and metric tracking.
"""

import asyncio
import uuid
import sys
from pathlib import Path

# Fix Windows console encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import delete
from app.database import AsyncSessionLocal
from app.models.semantic_cache import SemanticCache
from app.services.embedder import embedder
from app.services.ai_service import process_message
from app.services.metrics_service import cache_metrics
from app.config import settings


async def main():
    print("=" * 70)
    print("MindBridge AI - Live Semantic Response Cache Verification")
    print("=" * 70)

    # 1. Initialize embedder
    print("\n[1/6] Initializing MiniLM embedding model...")
    embedder.initialize()
    embedder.load_corpus(settings.CORPUS_PATH)
    print("      MiniLM loaded successfully.")

    session_id = str(uuid.uuid4())

    async with AsyncSessionLocal() as db:
        # Clean test entries
        await db.execute(delete(SemanticCache))
        await db.commit()
        print("\n[2/6] Cleaned test cache entries from PostgreSQL.")

        # Test Case 1: First query (Cache Miss)
        q1 = "What are some practical tips to manage exam stress?"
        print(f"\n[3/6] Sending Query 1 (Cache Miss Expected): '{q1}'")
        res1 = await process_message(
            user_message=q1,
            session_id=session_id,
            session_history=[],
            db=db,
        )
        print(f"      Response received (len={len(res1['response'])} chars)")
        print(f"      cache_hit        : {res1.get('cache_hit')}")
        print(f"      is_crisis        : {res1.get('is_crisis')}")
        assert res1.get("cache_hit") is False, "Query 1 should be a Cache MISS"

        # Test Case 2: Exact same query (Cache Hit)
        print(f"\n[4/6] Sending Query 2 (Identical -> Cache Hit Expected): '{q1}'")
        res2 = await process_message(
            user_message=q1,
            session_id=session_id,
            session_history=[],
            db=db,
        )
        print(f"      Response received: '{res2['response'][:60]}...'")
        print(f"      cache_hit        : {res2.get('cache_hit')}")
        print(f"      cached_similarity: {res2.get('cached_similarity')}")
        assert res2.get("cache_hit") is True, "Query 2 MUST be a Cache HIT"
        assert res2.get("cached_similarity") >= 0.98, "Similarity should be ~1.0 for exact query"

        # Test Case 3: Paraphrased query (Cache Hit via Cosine Similarity)
        q3 = "What can I do to manage exam stress?"
        print(f"\n[5/6] Sending Query 3 (Paraphrased -> Semantic Cache Hit Expected): '{q3}'")
        res3 = await process_message(
            user_message=q3,
            session_id=session_id,
            session_history=[],
            db=db,
        )
        print(f"      Response received: '{res3['response'][:60]}...'")
        print(f"      cache_hit        : {res3.get('cache_hit')}")
        print(f"      cached_similarity: {res3.get('cached_similarity')}")
        assert res3.get("cache_hit") is True, "Query 3 MUST be a Cache HIT via semantic similarity"
        assert res3.get("cached_similarity") >= 0.90, "Similarity must be >= 0.90"

        # Test Case 4: Crisis query (Must Pre-empt Cache)
        q4 = "I want to kill myself, I cannot take this anymore"
        print(f"\n[6/6] Sending Query 4 (Crisis Safety Pre-emption Test): '{q4}'")
        res4 = await process_message(
            user_message=q4,
            session_id=session_id,
            session_history=[],
            db=db,
        )
        print(f"      is_crisis        : {res4.get('is_crisis')}")
        print(f"      cache_hit        : {res4.get('cache_hit')}")
        print(f"      Safety Message   : '{res4['response'][:65]}...'")
        assert res4.get("is_crisis") is True, "Query 4 MUST trigger crisis safety"
        assert res4.get("cache_hit") is False, "Crisis query must NEVER be cached or hit cache"

    # Display Metrics Summary
    metrics = cache_metrics.get_metrics()
    print("\n" + "=" * 70)
    print("LIVE CACHE PERFORMANCE METRICS")
    print("=" * 70)
    print(f" Total Queries Handled      : {metrics['total_queries']}")
    print(f" Cache Hits                 : {metrics['cache_hits']}")
    print(f" Cache Misses               : {metrics['cache_misses']}")
    print(f" GPU Calls Avoided          : {metrics['gpu_calls_avoided']}")
    print(f" Hit Rate                   : {metrics['hit_rate_percentage']}%")
    print(f" Average Cache Lookup Latency: {metrics['avg_cache_lookup_ms']} ms")
    print(f" Average Embedding Latency  : {metrics['avg_embedding_ms']} ms")
    print(f" Average Hit Similarity     : {metrics['avg_hit_similarity_score']}")
    print("=" * 70)
    print("[SUCCESS] All live verification checks passed successfully!\n")


if __name__ == "__main__":
    asyncio.run(main())
