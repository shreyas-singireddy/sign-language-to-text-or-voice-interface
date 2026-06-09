from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.db import client
from app.db.schemas import UserCreate
from app.core.security import create_access_token, get_password_hash, verify_password

class LoginRequest(BaseModel):
    email: str
    password: str

router = APIRouter()

@router.post('/register')
async def register(user: UserCreate):
    db = client.get_db()
    existing = await db.users.find_one({'email': user.email})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')

    hashed_password = get_password_hash(user.password)
    payload = {
        'name': user.name,
        'email': user.email,
        'hashed_password': hashed_password,
        'role': 'user',
        'createdAt': datetime.now(timezone.utc).isoformat()
    }
    result = await db.users.insert_one(payload)
    return {'id': str(result.inserted_id), 'message': 'User created successfully'}

@router.post('/login')
async def login(payload: LoginRequest):
    db = client.get_db()
    user = await db.users.find_one({'email': payload.email})
    if not user or not verify_password(payload.password, user['hashed_password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

    token = create_access_token({'sub': str(user['_id']), 'role': user['role']})
    return {
        'user': {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'createdAt': user['createdAt']
        },
        'token': token
    }

@router.post('/logout')
async def logout():
    return {'message': 'Logged out successfully'}

@router.post('/reset-password')
async def reset_password(data: dict):
    # Placeholder reset flow. In production use email tokens and secure validation.
    return {'message': 'Password reset request received'}
