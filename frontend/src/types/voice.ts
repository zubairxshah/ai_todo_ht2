// Voice input types and interfaces

export type VoiceStatus = 'idle' | 'listening' | 'processing' | 'error';

export type VoiceErrorCode =
  | 'permission_denied'      // User denied microphone access
  | 'not_supported'          // Browser doesn't support speech recognition
  | 'network_error'          // Whisper API call failed
  | 'no_speech'              // No speech detected in audio
  | 'audio_capture_error'    // Failed to capture audio
  | 'transcription_failed'   // Speech recognition returned no result
  | 'aborted';               // User cancelled recording

export interface VoiceError {
  code: VoiceErrorCode;
  message: string;
  recoverable: boolean;  // Can user retry?
}

export interface VoiceState {
  status: VoiceStatus;
  isSupported: boolean;           // Web Speech API available
  permissionState: 'granted' | 'denied' | 'prompt' | 'unknown';
  transcription: string | null;   // Current/last transcription
  confidence: number | null;      // 0-1 confidence score
  error: VoiceError | null;       // Last error if any
}

export interface VoiceInputConfig {
  language: string;              // BCP-47 language code, default 'en-US'
  continuous: boolean;           // Keep listening after result, default false
  interimResults: boolean;       // Show partial results, default true
  maxDuration: number;           // Max recording time in ms, default 60000
  silenceTimeout: number;        // Stop after silence in ms, default 3000
}

export interface VoiceInputHookReturn {
  // State
  state: VoiceState;

  // Actions
  startListening: () => Promise<void>;
  stopListening: () => void;
  cancelListening: () => void;

  // Computed
  isListening: boolean;
  isProcessing: boolean;
  canUseVoice: boolean;
}
