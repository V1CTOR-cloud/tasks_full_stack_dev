from fastapi import APIRouter

from .project import router as project_router
from .task import router as tasks_router
from .team import router as teams_router

router = APIRouter()

router.include_router(project_router)
router.include_router(tasks_router)
router.include_router(teams_router)