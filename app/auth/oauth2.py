from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
import jwt
from app.db.mongo import users_collection
from app.models.user import UserInDb, TokenData
import os
from app.config import JWT_SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Эта штука говорит Swagger, что мы используем Bearer токен
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    print("JWT_SECRET_KEY:", JWT_SECRET_KEY)
    print("ALGORITHM:", ALGORITHM)
    print("ACCESS_TOKEN_EXPIRE_MINUTES:", ACCESS_TOKEN_EXPIRE_MINUTES)

    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDb:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, "your_secret_key", algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.PyJWTError:
        raise credentials_exception
    user_dict = users_collection.find_one({"email": token_data.email})
    if user_dict is None:
        raise credentials_exception
    return UserInDb(**user_dict)