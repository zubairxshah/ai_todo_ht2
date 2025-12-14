'use client';

import { useState, useEffect } from 'react';

interface TaskNotificationProps {
  message: string;
  type: 'added' | 'completed' | 'updated' | 'deleted';
  onComplete?: () => void;
}

const typeConfig = {
  added: {
    bg: 'bg-green-100',
    text: 'text-green-700',
    border: 'border-green-300',
    icon: '✨',
  },
  completed: {
    bg: 'bg-blue-100',
    text: 'text-blue-700',
    border: 'border-blue-300',
    icon: '✅',
  },
  updated: {
    bg: 'bg-yellow-100',
    text: 'text-yellow-700',
    border: 'border-yellow-300',
    icon: '✏️',
  },
  deleted: {
    bg: 'bg-red-100',
    text: 'text-red-700',
    border: 'border-red-300',
    icon: '🗑️',
  },
};

export default function TaskNotification({
  message,
  type,
  onComplete,
}: TaskNotificationProps) {
  const [isVisible, setIsVisible] = useState(true);
  const [isLeaving, setIsLeaving] = useState(false);

  useEffect(() => {
    // Start fade out after 2.5 seconds
    const fadeTimer = setTimeout(() => {
      setIsLeaving(true);
    }, 2500);

    // Remove after animation completes (3 seconds total)
    const removeTimer = setTimeout(() => {
      setIsVisible(false);
      onComplete?.();
    }, 3000);

    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(removeTimer);
    };
  }, [onComplete]);

  if (!isVisible) return null;

  const config = typeConfig[type];

  return (
    <div
      className={`
        inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium
        ${config.bg} ${config.text} border ${config.border}
        transition-all duration-500 ease-out
        ${isLeaving ? 'opacity-0 translate-x-2' : 'opacity-100 translate-x-0'}
        animate-slide-in
      `}
    >
      <span>{config.icon}</span>
      <span>{message}</span>
    </div>
  );
}
