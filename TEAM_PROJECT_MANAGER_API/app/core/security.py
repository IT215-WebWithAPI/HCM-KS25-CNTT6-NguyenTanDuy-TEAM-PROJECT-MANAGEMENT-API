import bcrypt
import jwt

from datetime import datetime, timedelta, timezone
from app.core.config import settings

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def hash_password(password: str) -> str:
    password_byte = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_byte, salt)

    return hashed_password.decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    password_byte = password.encode("utf-8")
    hashed_password_byte = hashed_password.encode("utf-8")

    return bcrypt.checkpw(password_byte, hashed_password_byte)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt