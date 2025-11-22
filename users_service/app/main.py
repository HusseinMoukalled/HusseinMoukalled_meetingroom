from fastapi import FastAPI
from users_service.app.routers import users

app = FastAPI()
app.include_router(users.router, prefix="/users", tags=["Users"])
