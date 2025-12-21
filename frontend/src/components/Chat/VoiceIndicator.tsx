'use client';

import type { VoiceStatus } from '@/types/voice';

interface VoiceIndicatorProps {
  status: VoiceStatus;
  message?: string;
}

/**
 * Visual indicator for voice input states
 * Shows listening, processing, error states with animations (T023-T025, T028)
 */
export function VoiceIndicator({ status, message }: VoiceIndicatorProps) {
  if (status === 'idle') {
    return null;
  }

  // T023-T025: State-specific styles and animations
  const getStatusConfig = () => {
    switch (status) {
      case 'listening':
        return {
          styles: 'bg-blue-100 text-blue-700 border-blue-300 animate-voice-pulse',
          icon: (
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
              <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
            </svg>
          ),
          text: message || 'Listening...'
        };
      case 'processing':
        return {
          styles: 'bg-blue-100 text-blue-700 border-blue-300',
          icon: (
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ),
          text: message || 'Processing...'
        };
      case 'error':
        return {
          styles: 'bg-red-100 text-red-700 border-red-300 animate-voice-error-shake',
          icon: (
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          ),
          text: message || 'Error occurred'
        };
      default:
        return {
          styles: 'bg-gray-100 text-gray-700 border-gray-300',
          icon: null,
          text: ''
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div
      className={'px-3 py-2 rounded-md border flex items-center gap-2 text-sm transition-all duration-300 ' + config.styles}
      role="status"
      aria-live="polite"
    >
      {config.icon}
      <span>{config.text}</span>
    </div>
  );
}
