from fastapi import APIRouter, Depends, HTTPException, status
from app.api.utils import get_current_user
from app.db import client
from app.db.schemas import TranslationInput
from app.services.translate_service import translate_image
from datetime import datetime, timezone
from bson import ObjectId

router = APIRouter()

@router.post('/translate')
async def translate(payload: TranslationInput, user: dict = Depends(get_current_user)):
    result = await translate_image(payload.imageData, payload.language)
    record = {
        'userId': user['sub'],
        'detectedGesture': result['detectedGesture'],
        'translatedText': result['translatedText'],
        'confidence': result['confidence'],
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    db = client.get_db()
    await db.translations.insert_one(record)
    return {**result, 'record': record}

@router.get('/history')
async def history(user: dict = Depends(get_current_user)):
    db = client.get_db()
    cursor = db.translations.find({'userId': user['sub']}).sort('timestamp', -1).limit(20)
    results = [
        {
            'id': str(doc['_id']),
            'userId': doc['userId'],
            'detectedGesture': doc['detectedGesture'],
            'translatedText': doc['translatedText'],
            'confidence': doc['confidence'],
            'timestamp': doc['timestamp']
        }
        for doc in await cursor.to_list(length=20)
    ]
    return results

@router.delete('/history/{translation_id}')
async def delete_history(translation_id: str, user: dict = Depends(get_current_user)):
    db = client.get_db()
    try:
        obj_id = ObjectId(translation_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid translation ID')
    result = await db.translations.delete_one({'_id': obj_id, 'userId': user['sub']})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Translation not found')
    return {'message': 'Deleted successfully'}
