from fastapi import FastAPI
from bookings_service.app.routers import bookings

app = FastAPI()

app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
