/**
 * Voice transcription service
 * Handles Web Speech API detection and transcription fallback
 */

/**
 * Check if Web Speech API is supported in the current browser
 */
export function isWebSpeechSupported(): boolean {
  if (typeof window === 'undefined') return false;
  
  const SpeechRecognition =
    (window as any).SpeechRecognition ||
    (window as any).webkitSpeechRecognition;
  
  return typeof SpeechRecognition !== 'undefined';
}

/**
 * Get the SpeechRecognition constructor
 * Handles vendor prefixes (webkit for Safari)
 */
export function getSpeechRecognition(): typeof SpeechRecognition | null {
  if (typeof window === 'undefined') return null;
  
  return (
    (window as any).SpeechRecognition ||
    (window as any).webkitSpeechRecognition ||
    null
  );
}

/**
 * Transcribe audio blob using OpenAI Whisper API (fallback)
 * This is used when Web Speech API is unavailable (T032)
 *
 * @param audioBlob - Audio data to transcribe
 * @param token - JWT authentication token
 * @param language - Optional language hint (BCP-47)
 * @returns Transcribed text
 */
export async function transcribeWithWhisper(
  audioBlob: Blob,
  token: string,
  language: string = 'en'
): Promise<string> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');
  formData.append('language', language);

  const response = await fetch(`${apiUrl}/api/transcribe`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Transcription failed' }));
    throw new Error(error.error || 'Transcription failed');
  }

  const result = await response.json();
  return result.text;
}

/**
 * Start recording audio using MediaRecorder API (T033)
 * Used for Whisper API fallback
 *
 * @returns MediaRecorder instance and audio chunks array
 */
export async function startAudioRecording(): Promise<{
  recorder: MediaRecorder;
  chunks: Blob[];
}> {
  // Request microphone access
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

  // Check supported mime types
  const mimeType = MediaRecorder.isTypeSupported('audio/webm')
    ? 'audio/webm'
    : MediaRecorder.isTypeSupported('audio/mp4')
    ? 'audio/mp4'
    : 'audio/wav';

  const recorder = new MediaRecorder(stream, { mimeType });
  const chunks: Blob[] = [];

  recorder.ondataavailable = (event) => {
    if (event.data.size > 0) {
      chunks.push(event.data);
    }
  };

  return { recorder, chunks };
}
