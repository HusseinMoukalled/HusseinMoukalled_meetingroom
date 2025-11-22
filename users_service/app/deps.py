from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from shared.database import get_db
from sqlalchemy.orm import Session
from users_service.app import models, auth

oauth2 = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    data = auth.decode_token(token)
    username = data.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

def require_admin(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user
