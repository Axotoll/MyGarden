from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import PyMongoError

from app.models.user import UserCreate, UserInDb, UserPublic, UserLogin, Token, TokenData
from app.functions.security import hash_password, verify_password
from app.db.mongo import users_collection

from app.auth.oauth2 import create_access_token, get_current_user

router = APIRouter()


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    try:
        # Check if user with the same email already exists
        existing_user = users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered.")

        # Hash the password (using a simple placeholder here; use bcrypt/argon2 in production)
        hashed_password = hash_password(user.password)

        user_in_db = UserInDb(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )

        # Insert the new user into the database
        result = users_collection.insert_one(user_in_db.dict())
        if not result.acknowledged:
            raise HTTPException(status_code=500, detail="Failed to create user.")

        return UserPublic(
            username=user_in_db.username,
            email=user_in_db.email,
            language=user_in_db.language,
            is_active=user_in_db.is_active,
            is_admin=user_in_db.is_admin,
            created_at=user_in_db.created_at
        )

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



#login for app
@router.post("/login_json", response_model=Token)
async def login_user(user: UserLogin):
    try:
        # Find the user by email
        user_in_db = users_collection.find_one({"email": user.email})
        if not user_in_db:
            raise HTTPException(status_code=400, detail="Invalid email or password.")

        user_in_db = UserInDb(**user_in_db)

        # Verify the password
        if not verify_password(user.password, user_in_db.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid email or password.")

        # Create JWT token
        access_token = create_access_token(data={"sub": user_in_db.email}, expires_delta=timedelta(hours=1))

        return Token(access_token=access_token)

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
#login for swagger uing OAuth2
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        # Find the user by email (username field in OAuth2PasswordRequestForm)
        user_in_db = users_collection.find_one({"email": form_data.username})
        if not user_in_db:
            raise HTTPException(status_code=400, detail="Invalid email or password.")

        user_in_db = UserInDb(**user_in_db)

        # Verify the password
        if not verify_password(form_data.password, user_in_db.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid email or password.")

        # Create JWT token
        access_token = create_access_token(data={"sub": user_in_db.email}, expires_delta=timedelta(hours=1))

        return Token(access_token=access_token)

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    

@router.get("/me", response_model=UserPublic)
async def read_current_user(current_user: UserInDb = Depends(get_current_user)):
    return UserPublic(
        username=current_user.username,
        email=current_user.email,
        language=current_user.language,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at
    )