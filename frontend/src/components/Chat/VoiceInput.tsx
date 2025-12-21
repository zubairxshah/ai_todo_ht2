'use client';

import { useVoiceInput } from '@/hooks/useVoiceInput';

interface VoiceInputProps {
  onTranscription: (text: string) => void;
  disabled?: boolean;
}

/**
 * Voice input button component
 * Handles microphone button and voice recording UI
 */
export function VoiceInput({ onTranscription, disabled = false }: VoiceInputProps) {
  const {
    state,
    startListening,
    stopListening,
    isListening,
    canUseVoice,
  } = useVoiceInput({}, onTranscription);

  const handleClick = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  // Hide button if voice not supported
  if (!canUseVoice) {
    return null;
  }

  // T017: Voice input button styling
  const buttonStyles = isListening
    ? 'px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-xl hover:from-blue-700 hover:to-blue-600 transition-all duration-300 shadow-lg animate-pulse'
    : 'px-4 py-3 bg-white text-gray-700 rounded-xl hover:bg-gray-50 border border-gray-200 transition-all duration-300';

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled}
      className={buttonStyles}
      aria-label={isListening ? 'Stop recording' : 'Start recording'}
      title={isListening ? 'Stop recording' : 'Start voice input'}
    >
      {/* Microphone icon with listening state styling */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={isListening ? 2 : 1.5}
        stroke="currentColor"
        className="w-5 h-5"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z"
        />
      </svg>
    </button>
  );
}
