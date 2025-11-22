from fastapi import FastAPI
from rooms_service.app.routers import rooms

app=FastAPI()

app.include_router(rooms.router,prefix="/rooms",tags=["Rooms"])
