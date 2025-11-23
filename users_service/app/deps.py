from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from shared.database import get_db
from sqlalchemy.orm import Session
from users_service.app import models, auth
from typing import Optional

oauth2 = OAuth2PasswordBearer(tokenUrl="/users/login", auto_error=False)

def get_current_user(token: Optional[str] = Depends(oauth2), db: Session = Depends(get_db)):
    """
    Get the current authenticated user from the JWT token.
    
    Args:
        token: JWT token from the Authorization header
        db: Database session
        
    Returns:
        User: The authenticated user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        data = auth.decode_token(token)
        username = data.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    return user

def require_admin(user=Depends(get_current_user)):
    """
    Require the current user to have admin role.
    
    Args:
        user: Current authenticated user
        
    Returns:
        User: The admin user
        
    Raises:
        HTTPException: If user is not an admin
    """
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

def require_moderator(user=Depends(get_current_user)):
    """
    Require the current user to have moderator or admin role.
    
    Args:
        user: Current authenticated user
        
    Returns:
        User: The moderator or admin user
        
    Raises:
        HTTPException: If user is not a moderator or admin
    """
    if user.role not in ["moderator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator or admin access required"
        )
    return user

def require_regular_user_or_above(user=Depends(get_current_user)):
    """
    Require the current user to be at least a regular user (regular_user, moderator, or admin).
    
    Args:
        user: Current authenticated user
        
    Returns:
        User: The authenticated user
    """
    if user.role not in ["regular_user", "moderator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return user
