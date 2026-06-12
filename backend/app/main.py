from contextlib import asynccontextmanager
import logging
import os

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from ws.telemetry_socket import router as ws_router

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import db_manager
from backend.utils.i18n_manager import get_locale_fastapi, get_translator
from backend.services.ai_service import AIService

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_manager.connect()
    yield
    await db_manager.disconnect()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)


@app.get("/health", tags=["health"])
async def health_check(request: Request, _=Depends(get_translator)):
    return {"status": _("healthy"), "project": settings.PROJECT_NAME}

# Initialize AI Service
ai_service = AIService()

@app.post("/api/translate_sign", tags=["ai"])
async def translate_sign(
    request: Request,
    _ = Depends(get_translator),
    target_lang: str = Depends(get_locale_fastapi)
):
    """
    Processes sign language input, translates it, and generates voice output.
    """
    # In a real application, you would receive video frame data here
    # For now, let's simulate receiving some data.
    try:
        body = await request.json()
        video_frame_data = body.get('video_data') # Placeholder for actual video data
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_("Invalid JSON body"))

    if not video_frame_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_("Video data is required."))

    # Determine inference mode (local or cloud) based on user preference or config
    inference_mode = request.query_params.get('inference_mode', None) # 'local' or 'cloud'

    translated_text, audio_file_path = ai_service.process_sign_language(
        video_frame_data, target_lang, inference_mode
    )

    if audio_file_path and os.path.exists(audio_file_path):
        # For demonstration, we'll send the file. In production, you might stream it or return a URL.
        # Ensure the file is cleaned up after sending if it's temporary
        return FileResponse(audio_file_path, media_type="audio/mpeg", filename="translated_audio.mp3")
    
    return JSONResponse(
        {"translated_text": translated_text, "message": _("Audio generation failed or not available.")},
        status_code=status.HTTP_200_OK
    )

@app.get("/api/supported_languages", tags=["i18n"])
async def supported_languages():
    return {"languages": settings.SUPPORTED_LANGUAGES}

@app.post("/api/ask_ai", tags=["ai"])
async def ask_ai(request: Request, _=Depends(get_translator)):
    """
    Example route for advanced LLM interaction (if Ollama is integrated).
    """
    body = await request.json()
    user_prompt = body.get('prompt')
    if not user_prompt:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_("Prompt is required."))
    
    response = ai_service.query_ollama(user_prompt)
    return {"response": response}
