"""Transcription router for Whisper API fallback."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from app.schemas.transcription import TranscriptionResponse, TranscriptionError
from app.dependencies.auth import get_current_user_id

# Router will be completed in Phase 7 (T036-T037)
router = APIRouter(prefix="/api", tags=["transcription"])

# Max file size: 25 MB
MAX_FILE_SIZE = 25 * 1024 * 1024

# Allowed audio formats
ALLOWED_FORMATS = {'webm', 'wav', 'mp3', 'm4a', 'ogg'}


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = Form("en"),
    user_id: str = Depends(get_current_user_id)
):
    """
    Transcribe audio file using OpenAI Whisper API (T036-T037).

    This endpoint is a fallback for browsers that don't support Web Speech API.
    Requires authentication.

    Args:
        audio: Audio file (webm, wav, mp3, m4a, ogg)
        language: Language hint (BCP-47 code, default: "en")
        user_id: Authenticated user ID (from JWT)

    Returns:
        TranscriptionResponse with transcribed text

    Raises:
        400: Invalid input (missing file, wrong format, too large)
        500: Transcription failed
    """
    from app.services.whisper import whisper_service
    import io

    # T037: Validate audio file
    if not audio:
        raise HTTPException(
            status_code=400,
            detail="No audio file provided"
        )

    # Check file format
    filename = audio.filename or "audio"
    ext = filename.lower().split('.')[-1]
    if ext not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format. Allowed: {', '.join(ALLOWED_FORMATS)}"
        )

    # Read file and check size
    audio_bytes = await audio.read()
    if len(audio_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Audio file too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB"
        )

    if len(audio_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="Audio file is empty"
        )

    # T036: Transcribe using Whisper
    try:
        # Create file-like object for Whisper API
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        # Transcribe
        text, confidence = whisper_service.transcribe(
            audio_file,
            language=language,
            filename=filename
        )

        return TranscriptionResponse(
            text=text,
            confidence=confidence,
            language=language,
            duration_ms=None  # Not easily calculable from audio bytes
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )
