"""
Database initialization script.
Creates all database tables.
"""
from shared.database import Base, engine
import users_service.app.models
import rooms_service.app.models
import bookings_service.app.models
import reviews_service.app.models

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

