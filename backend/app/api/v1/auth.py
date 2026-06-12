from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db=Depends(get_db)):
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available.",
        )

    existing_user = await db.users.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    hashed_password = get_password_hash(user_in.password)
    user_doc = {
        "name": user_in.name,
        "email": user_in.email,
        "hashed_password": hashed_password,
        "role": "user",
        "createdAt": datetime.now(UTC),
    }

    result = await db.users.insert_one(user_doc)
    return {"id": str(result.inserted_id), "message": "User registered successfully."}


@router.post("/login", response_model=TokenResponse)
async def login(login_in: LoginRequest, db=Depends(get_db)):
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available.",
        )

    user = await db.users.find_one({"email": login_in.email})
    if not user or not verify_password(login_in.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    access_token = create_access_token(subject=str(user["_id"]))

    user_res = UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        role=user.get("role", "user"),
        createdAt=user["createdAt"],
    )

    return TokenResponse(access_token=access_token, user=user_res)
