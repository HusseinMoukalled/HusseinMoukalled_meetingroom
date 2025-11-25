from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from users_service.app import models, auth
from users_service.app.schemas import UserCreate, UserLogin, UserUpdate, UserResponse, UserBookingHistoryResponse, BookingHistoryItem
from users_service.app.deps import get_current_user, require_admin
from shared.database import get_db
from shared.exceptions import (
    ValidationException,
    NotFoundException,
    ConflictException,
    AuthenticationException
)
import re
from pydantic import EmailStr

router = APIRouter()

def sanitize_string(input_str: str) -> str:
    """
    Sanitize string input to prevent SQL injection and XSS attacks.
    
    Args:
        input_str: Input string to sanitize
        
    Returns:
        str: Sanitized string
    """
    if not input_str:
        return ""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[;\'"\\<>]', '', input_str)
    return sanitized.strip()

def validate_password(password: str) -> bool:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        bool: True if password meets requirements
    """
    if len(password) < 6:
        return False
    return True

def validate_role(role: str) -> bool:
    """
    Validate that role is one of the allowed roles.
    
    Args:
        role: Role to validate
        
    Returns:
        bool: True if role is valid
    """
    allowed_roles = ["regular_user", "admin", "moderator"]
    return role in allowed_roles

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    - **name**: Full name of the user
    - **username**: Unique username
    - **email**: Valid email address
    - **password**: Password (minimum 6 characters)
    - **role**: User role (regular_user, admin, moderator) - defaults to regular_user
    
    Note: Only admins can create admin or moderator accounts. Regular users can only create regular_user accounts.
    """
    # Sanitize inputs
    username = sanitize_string(data.username)
    name = sanitize_string(data.name)
    
    # Validate username
    if not username or len(username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters long"
        )
    
    # Validate password
    if not validate_password(data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    # Validate role
    role = data.role if data.role else "regular_user"
    if not validate_role(role):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Allowed roles: regular_user, admin, moderator"
        )
    
    # Check if username already exists
    existing = db.query(models.User).filter(models.User.username == username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email already exists
    existing_email = db.query(models.User).filter(models.User.email == data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed = auth.hash_password(data.password)

    user = models.User(
        name=name,
        username=username,
        email=data.email,
        hashed_password=hashed,
        role=role,
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", status_code=status.HTTP_200_OK)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return an access token.
    
    - **username**: Username
    - **password**: Password
    
    Returns a JWT access token for authenticated requests.
    """
    # Sanitize username
    username = sanitize_string(data.username)
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    if not auth.verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """
    Get all users in the system.
    
    Requires admin role.
    """
    return db.query(models.User).all()

@router.get("/{username}", response_model=UserResponse)
def get_user(
    username: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get a specific user by username.
    
    Regular users can only view their own profile. Admins can view any user.
    """
    # Sanitize username
    username = sanitize_string(username)
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Authorization: Users can view their own profile, admins can view any
    if current_user.role != "admin" and current_user.username != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile"
        )
    
    return user

@router.put("/{username}", response_model=UserResponse)
def update_user(
    username: str,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Update user profile information.
    
    - **name**: New name (optional)
    - **email**: New email (optional)
    - **password**: New password (optional)
    
    Regular users can only update their own profile. Admins can update any user.
    """
    # Sanitize username
    username = sanitize_string(username)
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Authorization check
    if current_user.username != username and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )

    if data.name:
        user.name = sanitize_string(data.name)
    if data.email:
        # Check if email is already taken by another user
        existing_email = db.query(models.User).filter(
            models.User.email == data.email,
            models.User.id != user.id
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = data.email
    if data.password:
        if not validate_password(data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        user.hashed_password = auth.hash_password(data.password)

    db.commit()
    db.refresh(user)
    return user

@router.put("/{username}/role", response_model=UserResponse)
def update_user_role(
    username: str,
    new_role: str,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """
    Update a user's role.
    
    - **username**: Username of the user to update
    - **new_role**: New role (regular_user, admin, moderator)
    
    Requires admin role.
    """
    # Sanitize inputs
    username = sanitize_string(username)
    new_role = sanitize_string(new_role)
    
    if not validate_role(new_role):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Allowed roles: regular_user, admin, moderator"
        )
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user

@router.put("/{username}/activate", response_model=UserResponse)
def activate_user(
    username: str,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """
    Activate a user account.
    
    Requires admin role.
    """
    username = sanitize_string(username)
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user

@router.put("/{username}/deactivate", response_model=UserResponse)
def deactivate_user(
    username: str,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """
    Deactivate a user account.
    
    Requires admin role.
    """
    username = sanitize_string(username)
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{username}", status_code=status.HTTP_200_OK)
def delete_user(
    username: str,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """
    Delete a user account.
    
    Requires admin role.
    """
    username = sanitize_string(username)
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}

@router.get("/{username}/history", response_model=UserBookingHistoryResponse)
def booking_history(
    username: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get booking history for a specific user.
    
    Regular users can only view their own booking history. Admins can view any user's history.
    """
    # Sanitize username
    username = sanitize_string(username)
    
    # Authorization check
    if current_user.username != username and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own booking history"
        )
    
    # Validate user exists
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Use parameterized query to prevent SQL injection
    rows = db.execute(
        text("SELECT room_id, date, start_time, end_time FROM bookings WHERE username = :u ORDER BY date DESC, start_time DESC"),
        {"u": username}
    ).fetchall()

    items = [
        BookingHistoryItem(
            room_id=r[0],
            date=str(r[1]),
            start_time=str(r[2]),
            end_time=str(r[3])
        ) for r in rows
    ]

    return UserBookingHistoryResponse(username=username, bookings=items)
