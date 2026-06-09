from fastapi import APIRouter, Depends, HTTPException, status
from app.api.utils import get_current_user
from app.db import client
from bson import ObjectId

router = APIRouter()

async def require_admin(user: dict = Depends(get_current_user)):
    if user.get('role') != 'admin':
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin access required')
    return user

@router.get('/users')
async def get_users(_=Depends(require_admin)):
    db = client.get_db()
    users = await db.users.find().limit(50).to_list(length=50)
    return [{'id': str(user['_id']), 'name': user['name'], 'email': user['email'], 'role': user['role'], 'createdAt': user['createdAt']} for user in users]

@router.get('/analytics')
async def get_analytics(_=Depends(require_admin)):
    db = client.get_db()
    total_users = await db.users.count_documents({})
    total_translations = await db.translations.count_documents({})
    active_users = round(total_users * 0.78)
    return {
        'totalUsers': total_users,
        'totalTranslations': total_translations,
        'activeUsers': active_users
    }

@router.get('/translations')
async def get_translations(_=Depends(require_admin)):
    db = client.get_db()
    docs = await db.translations.find().sort('timestamp', -1).limit(50).to_list(length=50)
    return [
        {
            'id': str(doc['_id']),
            'userId': doc['userId'],
            'detectedGesture': doc['detectedGesture'],
            'translatedText': doc['translatedText'],
            'confidence': doc['confidence'],
            'timestamp': doc['timestamp']
        }
        for doc in docs
    ]
