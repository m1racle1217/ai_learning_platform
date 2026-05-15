from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.bootstrap import ensure_database_seeded
from app.database import engine
from app.models import Base
from app.routers import dashboard, exercises, learning, quizzes, resources, runtime, settings

ensure_database_seeded()
Base.metadata.create_all(engine)

app = FastAPI(title="AI 学习平台")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(dashboard.router)
app.include_router(learning.router)
app.include_router(exercises.router)
app.include_router(quizzes.router)
app.include_router(resources.router)
app.include_router(runtime.router)
app.include_router(settings.router)
