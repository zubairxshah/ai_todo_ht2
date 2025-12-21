import { useState, useCallback, useRef, useEffect } from 'react';
import type {
  VoiceState,
  VoiceInputConfig,
  VoiceInputHookReturn,
  VoiceError,
} from '@/types/voice';
import { getSpeechRecognition, isWebSpeechSupported } from '@/lib/voice-transcription';

const defaultConfig: VoiceInputConfig = {
  language: 'en-US',
  continuous: false,
  interimResults: true,
  maxDuration: 60000, // 60 seconds
  silenceTimeout: 3000, // 3 seconds
};

export function useVoiceInput(
  config: Partial<VoiceInputConfig> = {},
  onTranscription?: (text: string) => void
): VoiceInputHookReturn {
  console.log('🎤 [VOICE] useVoiceInput hook called with onTranscription:', !!onTranscription, typeof onTranscription);
  const finalConfig = { ...defaultConfig, ...config };

  const [state, setState] = useState<VoiceState>({
    status: 'idle',
    isSupported: false,
    permissionState: 'unknown',
    transcription: null,
    confidence: null,
    error: null,
  });

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const onTranscriptionRef = useRef(onTranscription);

  // Keep the ref updated with the latest callback
  useEffect(() => {
    console.log('🎤 [VOICE] Updating onTranscriptionRef with:', !!onTranscription, typeof onTranscription);
    onTranscriptionRef.current = onTranscription;
  }, [onTranscription]);

  // Initialize speech recognition on mount
  useEffect(() => {
    console.log('🎤 [VOICE] Initializing voice input hook...');
    const isSupported = isWebSpeechSupported();
    console.log('🎤 [VOICE] Web Speech API supported:', isSupported);
    setState(prev => ({ ...prev, isSupported }));

    if (isSupported) {
      const SpeechRecognitionClass = getSpeechRecognition();
      console.log('🎤 [VOICE] SpeechRecognition class:', !!SpeechRecognitionClass);
      if (SpeechRecognitionClass) {
        recognitionRef.current = new SpeechRecognitionClass();
        console.log('🎤 [VOICE] Recognition instance created successfully');
      }
    } else {
      console.warn('🎤 [VOICE] Speech recognition not available in this browser');
    }
  }, []);

  // T012: Check and request microphone permission
  const checkMicrophonePermission = useCallback(async (): Promise<void> => {
    try {
      // Check permission state
      if (navigator.permissions) {
        const result = await navigator.permissions.query({ name: 'microphone' as PermissionName });
        setState(prev => ({ ...prev, permissionState: result.state }));

        if (result.state === 'denied') {
          throw {
            code: 'permission_denied',
            message: 'Microphone access denied. Please enable it in your browser settings.',
            recoverable: true,
          } as VoiceError;
        }
      }

      // Request microphone access
      await navigator.mediaDevices.getUserMedia({ audio: true });
      setState(prev => ({ ...prev, permissionState: 'granted' }));
    } catch (error: any) {
      if (error.code === 'permission_denied') {
        throw error;
      }
      throw {
        code: 'permission_denied',
        message: 'Failed to access microphone. Please grant permission.',
        recoverable: true,
      } as VoiceError;
    }
  }, []);

  // T011: Start speech recognition
  const startListening = useCallback(async () => {
    console.log('🎤 [VOICE] startListening called');
    console.log('🎤 [VOICE] isSupported:', state.isSupported, 'recognition:', !!recognitionRef.current);

    if (!state.isSupported || !recognitionRef.current) {
      console.error('🎤 [VOICE] Speech recognition not supported');
      setState(prev => ({
        ...prev,
        status: 'error',
        error: {
          code: 'not_supported',
          message: 'Speech recognition is not supported in this browser.',
          recoverable: false,
        },
      }));
      return;
    }

    try {
      // T012: Check microphone permission
      console.log('🎤 [VOICE] Checking microphone permission...');
      await checkMicrophonePermission();
      console.log('🎤 [VOICE] Microphone permission granted');

      const recognition = recognitionRef.current;

      // Configure recognition
      recognition.lang = finalConfig.language;
      recognition.continuous = finalConfig.continuous;
      recognition.interimResults = finalConfig.interimResults;

      // T013: Set up event handlers with detailed logging
      recognition.onstart = () => {
        console.log('🎤 [VOICE] Recognition started');
        setState(prev => ({
          ...prev,
          status: 'listening',
          transcription: null,
          confidence: null,
          error: null,
        }));
      };

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        console.log('🎤 [VOICE] Result received:', event.results);
        const result = event.results[event.results.length - 1];
        const transcript = result[0].transcript;
        const confidence = result[0].confidence;

        console.log('🎤 [VOICE] Transcript:', transcript, 'Confidence:', confidence, 'Final:', result.isFinal);

        setState(prev => ({
          ...prev,
          status: 'processing',
          transcription: transcript,
          confidence,
        }));

        // Call callback if provided (using ref to get latest callback)
        const currentCallback = onTranscriptionRef.current;
        console.log('🎤 [VOICE] Checking callback - onTranscription:', !!currentCallback, 'isFinal:', result.isFinal);
        if (currentCallback && result.isFinal) {
          console.log('🎤 [VOICE] ✅ Calling onTranscription callback with:', transcript);
          currentCallback(transcript);
        } else {
          console.log('🎤 [VOICE] ⚠️ Callback NOT called - onTranscription:', !!currentCallback, 'isFinal:', result.isFinal);
        }
      };

      recognition.onspeechstart = () => {
        console.log('🎤 [VOICE] Speech detected (onspeechstart)');
      };

      recognition.onspeechend = () => {
        console.log('🎤 [VOICE] Speech ended (onspeechend)');
      };

      recognition.onaudiostart = () => {
        console.log('🎤 [VOICE] Audio capture started');
      };

      recognition.onaudioend = () => {
        console.log('🎤 [VOICE] Audio capture ended');
      };

      recognition.onsoundstart = () => {
        console.log('🎤 [VOICE] Sound detected');
      };

      recognition.onsoundend = () => {
        console.log('🎤 [VOICE] Sound ended');
      };

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error('🎤 [VOICE ERROR]', event.error, event);
        let errorCode: VoiceError['code'] = 'transcription_failed';
        let errorMessage = 'Speech recognition failed.';
        let recoverable = true;

        switch (event.error) {
          case 'no-speech':
            errorCode = 'no_speech';
            errorMessage = 'No speech detected. Please try again.';
            console.log('🎤 [VOICE] No speech detected after listening period');
            break;
          case 'audio-capture':
            errorCode = 'audio_capture_error';
            errorMessage = 'Failed to capture audio. Check your microphone.';
            console.error('🎤 [VOICE] Audio capture failed - mic not accessible');
            break;
          case 'not-allowed':
            errorCode = 'permission_denied';
            errorMessage = 'Microphone permission denied.';
            console.error('🎤 [VOICE] Permission denied');
            break;
          case 'network':
            errorCode = 'network_error';
            errorMessage = 'Network error occurred.';
            console.error('🎤 [VOICE] Network error');
            break;
          case 'aborted':
            errorCode = 'aborted';
            errorMessage = 'Speech recognition aborted.';
            console.log('🎤 [VOICE] Recognition aborted by user');
            break;
          default:
            console.error('🎤 [VOICE] Unknown error:', event.error);
        }

        setState(prev => ({
          ...prev,
          status: 'error',
          error: { code: errorCode, message: errorMessage, recoverable },
        }));
      };

      recognition.onend = () => {
        console.log('🎤 [VOICE] Recognition ended');
        // Clear silence timer
        if (silenceTimerRef.current) {
          clearTimeout(silenceTimerRef.current);
          silenceTimerRef.current = null;
        }

        setState(prev => {
          console.log('🎤 [VOICE] Final state - transcription:', prev.transcription, 'error:', prev.error);

          // FALLBACK: If we have a transcription but callback wasn't called, call it now
          const currentCallback = onTranscriptionRef.current;
          if (prev.transcription && !prev.error && currentCallback) {
            console.log('🎤 [VOICE] 🔄 FALLBACK: Calling onTranscription from onend with:', prev.transcription);
            currentCallback(prev.transcription);
          }

          // Return to idle state
          return { ...prev, status: 'idle' };
        });
      };

      // Start recognition
      console.log('🎤 [VOICE] Starting recognition with config:', {
        lang: finalConfig.language,
        continuous: finalConfig.continuous,
        interimResults: finalConfig.interimResults
      });
      recognition.start();

    } catch (error: any) {
      setState(prev => ({
        ...prev,
        status: 'error',
        error: error as VoiceError,
      }));
    }
  }, [state.isSupported, finalConfig, onTranscription, checkMicrophonePermission]);

  // T011: Stop speech recognition
  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  }, []);

  const cancelListening = useCallback(() => {
    // TODO: Implement in Phase 7 (T034)
    if (recognitionRef.current) {
      recognitionRef.current.abort();
    }
    setState(prev => ({
      ...prev,
      status: 'idle',
      transcription: null,
      error: null,
    }));
  }, []);

  return {
    state,
    startListening,
    stopListening,
    cancelListening,
    isListening: state.status === 'listening',
    isProcessing: state.status === 'processing',
    canUseVoice: state.isSupported,
  };
}
