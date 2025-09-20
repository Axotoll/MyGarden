# Точка входа FastAPI

from fastapi import FastAPI
from app.routes import plants, reminders, users

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(plants.router, prefix="/plants", tags=["plants"])
app.include_router(reminders.router, prefix="/reminders", tags=["reminders"])