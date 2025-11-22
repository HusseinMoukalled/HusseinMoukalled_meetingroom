from fastapi import FastAPI
from shared.database import Base, engine
from reviews_service.app.routers.reviews import router

import users_service.app.models
import rooms_service.app.models
import reviews_service.app.models

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router, prefix="/reviews")
