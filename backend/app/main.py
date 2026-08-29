"""
MindBridge AI — FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api.v1.router import api_router, root_api_router
from app.ws.chat_ws import router as ws_router
from app.services.embedder import embedder
from app.services.classifier_service import classifier_service
from app.services.ai_service import _initialize_inference
from app.services.memory_service import memory_service
from app.services.mood_service import mood_detector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    logger.info("🚀 MindBridge AI starting up...")

    # ── Create tables (SQLite / fresh DB) ────────────────────────────────────
    from app.database import engine, Base
    from app.models import User, ChatSession, Message, MoodLog, WellnessReport, JournalEntry  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("📦 Database tables ensured.")

    # ── Sentence Transformer + corpus ────────────────────────────────────────
    try:
        embedder.initialize()
        embedder.load_corpus(settings.CORPUS_PATH)
    except Exception as e:
        logger.error(f"Failed to initialize embedder: {e}")

    # ── Trained classifier (non-fatal — falls back to cosine similarity) ─────
    try:
        classifier_service.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize classifier: {e}")

    # ── Local Inference Client ────────────────────────────────────────────────
    try:
        _initialize_inference()
    except Exception as e:
        logger.error(f"Failed to initialize inference client: {e}")

    # ── Mood Detector (DistilBERT emotion classifier) ────────────────────────
    try:
        mood_detector.load()
    except Exception as e:
        logger.error(f"Failed to initialize mood detector: {e}")

    # ── Redis memory (non-fatal — chat still works without memory) ───────────
    try:
        await memory_service.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize MemoryService: {e}")

    logger.info("✅ MindBridge AI ready!")
    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("👋 MindBridge AI shutting down...")
    await memory_service.close()


app = FastAPI(
    title="MindBridge AI",
    description="AI-Powered Mental Health Support Platform — Built with Meta Llama 3",
    version="2.2.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(api_router)
app.include_router(root_api_router)
app.include_router(ws_router)


@app.get("/")
async def root():
    return {
        "name": "MindBridge AI",
        "version": "2.2.0",
        "status": "running",
        "architecture": "Llama-3-8B-Instruct + QLoRA",
        "attribution": "Built with Meta Llama 3",
        "corpus_loaded": embedder._loaded,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """
    Health check endpoint.
    Returns status of all major subsystems so users/reviewers can verify
    each component is operational.
    """
    memory_ok = await memory_service.ping()

    return {
        "status": "healthy",
        "model": "Meta Llama-3-8B-Instruct (QLoRA)",
        "attribution": "Built with Meta Llama 3",
        # ── NLP / ML ─────────────────────────────────────────────────────────
        "embedder_loaded": embedder._loaded,
        "corpus_size": len(embedder.corpus_data),
        "classifier_loaded": classifier_service._loaded,
        "classifier_categories": (
            classifier_service.categories if classifier_service._loaded else []
        ),
        # ── Memory ───────────────────────────────────────────────────────────
        "redis_connected": memory_ok,
        "memory_ttl_hours": settings.MEMORY_TTL_SECONDS // 3600,
    }
