"""Transcription API schemas."""
from typing import Optional
from pydantic import BaseModel


class TranscriptionResponse(BaseModel):
    """Response from transcription endpoint."""
    text: str
    confidence: Optional[float] = None
    language: str = "en"
    duration_ms: Optional[int] = None


class TranscriptionError(BaseModel):
    """Error response from transcription endpoint."""
    error: str
    code: str
