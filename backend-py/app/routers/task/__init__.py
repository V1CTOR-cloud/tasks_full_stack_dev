from fastapi import APIRouter

from .task import router as tasks_router
from .comment import router as comment_router

router = APIRouter()

router.include_router(tasks_router)
router.include_router(comment_router)