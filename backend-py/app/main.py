from fastapi import FastAPI
from app.routers import user, auth, task, color, team, project
app = FastAPI(
    title="tasks_full_stack_dev",
    version="1.0.0"
)

app.include_router(user.router)
app.include_router(task.router)
app.include_router(color.router)
app.include_router(team.router)
app.include_router(auth.router)
app.include_router(project.router)