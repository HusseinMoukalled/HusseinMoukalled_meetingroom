from sqlalchemy.orm import Session
from shared.database import get_db

def get_db_session()->Session:
    db=next(get_db())
    try:
        yield db
    finally:
        db.close()
