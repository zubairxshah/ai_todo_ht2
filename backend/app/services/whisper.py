"""OpenAI Whisper API integration for audio transcription."""
import os
from typing import BinaryIO, Optional
from openai import OpenAI
from app.config import settings


class WhisperService:
    """Service for transcribing audio using OpenAI Whisper API."""

    def __init__(self):
        """Initialize Whisper service with OpenAI client."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "whisper-1"

    def transcribe(
        self,
        audio_file: BinaryIO,
        language: str = "en",
        filename: str = "audio.webm"
    ) -> tuple[str, Optional[float]]:
        """
        Transcribe audio file using Whisper API.

        Args:
            audio_file: Audio file object (file-like)
            language: Language hint (BCP-47 code)
            filename: Filename with extension (for format detection)

        Returns:
            Tuple of (transcribed_text, confidence_score)
            Note: Whisper API doesn't return confidence, so second value is None

        Raises:
            Exception: If transcription fails
        """
        try:
            # Create a file tuple for the API
            # Format: (filename, file_object, content_type)
            file_tuple = (filename, audio_file, self._get_content_type(filename))

            # Call Whisper API
            transcription = self.client.audio.transcriptions.create(
                model=self.model,
                file=file_tuple,
                language=language,
                response_format="json"
            )

            text = transcription.text.strip()
            
            if not text:
                raise ValueError("Transcription returned empty text")

            return text, None  # Whisper doesn't provide confidence scores

        except Exception as e:
            raise Exception(f"Whisper transcription failed: {str(e)}")

    def _get_content_type(self, filename: str) -> str:
        """Get content type from filename extension."""
        ext = filename.lower().split('.')[-1]
        content_types = {
            'webm': 'audio/webm',
            'wav': 'audio/wav',
            'mp3': 'audio/mpeg',
            'm4a': 'audio/mp4',
            'ogg': 'audio/ogg',
        }
        return content_types.get(ext, 'application/octet-stream')


# Singleton instance
whisper_service = WhisperService()
