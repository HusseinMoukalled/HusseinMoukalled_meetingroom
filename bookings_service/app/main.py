from fastapi import FastAPI
from app.routers import bookings

app=FastAPI()

app.include_router(bookings.router,prefix="/bookings",tags=["Bookings"])