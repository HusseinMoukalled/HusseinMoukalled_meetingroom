from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from users_service.app import models, auth
from users_service.app.schemas import UserCreate, UserLogin, UserUpdate, UserResponse, UserBookingHistoryResponse, BookingHistoryItem
from users_service.app.deps import get_current_user, require_admin
from shared.database import get_db

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed = auth.hash_password(data.password)

    user = models.User(
        name=data.name,
        username=data.username,
        email=data.email,
        hashed_password=hashed,
        role=data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not auth.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return db.query(models.User).all()

@router.get("/{username}", response_model=UserResponse)
def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{username}", response_model=UserResponse)
def update_user(username: str, data: UserUpdate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current.username != username and current.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")

    if data.name:
        user.name = data.name
    if data.email:
        user.email = data.email
    if data.password:
        user.hashed_password = auth.hash_password(data.password)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{username}")
def delete_user(username: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}

@router.get("/{username}/history", response_model=UserBookingHistoryResponse)
def booking_history(username: str, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if current.username != username and current.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")

    rows = db.execute(
        text("SELECT room_id, date, start_time, end_time FROM bookings WHERE username = :u"),
        {"u": username}
    ).fetchall()

    items = [BookingHistoryItem(room_id=r[0], date=str(r[1]), start_time=str(r[2]), end_time=str(r[3])) for r in rows]

    return UserBookingHistoryResponse(username=username, bookings=items)
