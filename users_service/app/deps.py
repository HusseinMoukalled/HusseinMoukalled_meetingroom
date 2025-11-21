from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from shared.database import get_db
from app import auth,models

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    try:
        payload=auth.decode_token(token)
        username=payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401,detail="Invalid token")

    user=db.query(models.User).filter(models.User.username==username).first()
    if not user:
        raise HTTPException(status_code=401,detail="User not found")
    return user

def require_admin(current_user=Depends(get_current_user)):
    if current_user.role!="admin":
        raise HTTPException(status_code=403,detail="Admin access required")
    return current_user
