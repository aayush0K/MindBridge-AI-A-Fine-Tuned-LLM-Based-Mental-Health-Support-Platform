from fastapi import APIRouter
from .auth import router as auth_router
from .chat import router as chat_router
from .mood import router as mood_router
from .users import router as users_router
from .report import router as report_router
from .journal import router as journal_router

# Versioned API router (/api/v1)
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(mood_router)
api_router.include_router(users_router)
api_router.include_router(report_router)
api_router.include_router(journal_router)

# Direct alias router (/api) for backward compatibility
root_api_router = APIRouter(prefix="/api")
root_api_router.include_router(auth_router)
root_api_router.include_router(chat_router)
root_api_router.include_router(mood_router)
root_api_router.include_router(users_router)
root_api_router.include_router(report_router)
root_api_router.include_router(journal_router)
