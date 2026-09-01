from fastapi import FastAPI
from app.routers import user, auth, color
from app.routers.project import router as project_router
from app.routers.team import router as team_router
from app.routers.task import router as tasks_router

app = FastAPI(
    title="tasks_full_stack_dev",
    version="1.0.0"
)

app.include_router(user.router)
app.include_router(color.router)
app.include_router(auth.router)
app.include_router(tasks_router)
app.include_router(team_router)
app.include_router(project_router)