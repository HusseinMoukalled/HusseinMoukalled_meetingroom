from fastapi import FastAPI
from app.routers import reviews

app=FastAPI()

app.include_router(reviews.router,prefix="/reviews",tags=["Reviews"])
