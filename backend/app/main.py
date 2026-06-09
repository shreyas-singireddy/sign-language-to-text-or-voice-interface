from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.translate import router as translate_router
from app.api.live import router as live_router
from app.api.admin import router as admin_router
from app.db.client import connect_to_mongo, close_mongo_connection

app = FastAPI(title='SignBridge AI', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.add_event_handler('startup', connect_to_mongo)
app.add_event_handler('shutdown', close_mongo_connection)

app.include_router(auth_router, prefix='/api/auth', tags=['auth'])
app.include_router(translate_router, prefix='/api', tags=['translate'])
app.include_router(live_router, prefix='/api', tags=['live'])
app.include_router(admin_router, prefix='/api/admin', tags=['admin'])

@app.get('/')
def root():
    return {'message': 'SignBridge AI backend is online.'}
