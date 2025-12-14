'use client';

import { useState, useEffect } from 'react';
import { TaskEventType } from '@/lib/task-events';

interface ToastNotificationProps {
  id: string;
  message: string;
  taskTitle?: string;
  type: TaskEventType;
  onRemove: (id: string) => void;
}

const typeConfig = {
  added: {
    bg: 'from-green-500 to-emerald-600',
    icon: '✨',
    label: 'Task Added',
  },
  completed: {
    bg: 'from-blue-500 to-indigo-600',
    icon: '✅',
    label: 'Task Completed',
  },
  updated: {
    bg: 'from-amber-500 to-orange-600',
    icon: '✏️',
    label: 'Task Updated',
  },
  deleted: {
    bg: 'from-red-500 to-rose-600',
    icon: '🗑️',
    label: 'Task Deleted',
  },
};

export default function ToastNotification({
  id,
  message,
  taskTitle,
  type,
  onRemove,
}: ToastNotificationProps) {
  const [isLeaving, setIsLeaving] = useState(false);

  useEffect(() => {
    // Start exit animation after 2.5 seconds
    const fadeTimer = setTimeout(() => {
      setIsLeaving(true);
    }, 2500);

    // Remove after animation completes
    const removeTimer = setTimeout(() => {
      onRemove(id);
    }, 3000);

    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(removeTimer);
    };
  }, [id, onRemove]);

  const config = typeConfig[type];

  return (
    <div
      className={`
        flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg
        bg-gradient-to-r ${config.bg} text-white
        transform transition-all duration-500 ease-out
        ${isLeaving ? 'animate-slide-up' : 'animate-slide-down'}
        backdrop-blur-sm border border-white/20
      `}
    >
      <span className="text-2xl animate-float">{config.icon}</span>
      <div className="flex flex-col">
        <span className="text-xs font-medium opacity-90">{config.label}</span>
        <span className="font-semibold">
          {taskTitle ? `"${taskTitle}"` : message}
        </span>
      </div>
      <button
        onClick={() => {
          setIsLeaving(true);
          setTimeout(() => onRemove(id), 400);
        }}
        className="ml-auto p-1 hover:bg-white/20 rounded-full transition-colors"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}

interface ToastContainerProps {
  notifications: Array<{
    id: string;
    taskId: string;
    taskTitle?: string;
    type: TaskEventType;
    message: string;
  }>;
  onRemove: (id: string) => void;
}

export function ToastContainer({ notifications, onRemove }: ToastContainerProps) {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
      {notifications.map((notification) => (
        <ToastNotification
          key={notification.id}
          id={notification.id}
          message={notification.message}
          taskTitle={notification.taskTitle}
          type={notification.type}
          onRemove={onRemove}
        />
      ))}
    </div>
  );
}
