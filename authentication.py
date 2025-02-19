from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from models import UserInDB
from passlib.context import CryptContext
import jwt
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError


SECRET_KEY = "k1YwgtE8spsG5Ngg4RXEw/XgzOP7CYfvmTD8QqTRhpjYcUdwbNcWnuEdJAapY9Op"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# password: root
users_db = {
    "root": {
        "username": "root",
        "hashed_password": "$2y$10$CcdopyypIEtAk0Y5lrLzzuTOjOaQLH6UMXg48QMyXPfJ.DYtazJNK",
    }
}

# Instance of CryptContext with bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Verify password function
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Hash password function
def get_password_hash(password):
    return pwd_context.hash(password)


# Search user in database
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


# Authenticate user
def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# Create access token for 15 minutes
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Verify authentication token on every request
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(users_db, username)
    if user is None:
        raise credentials_exception
    return user
