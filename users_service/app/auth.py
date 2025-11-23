import bcrypt
from jose import jwt
from datetime import datetime, timedelta

# Use bcrypt directly instead of passlib to avoid initialization issues
BCRYPT_ROUNDS = 12


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    """
    # Encode password to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against a hash.
    """
    try:
        # Encode both to bytes
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed.encode('utf-8')
        # Verify password
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
