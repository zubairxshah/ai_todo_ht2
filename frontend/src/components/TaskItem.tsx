"use client";

import { useState } from "react";
import type { Task } from "@/types";
import { PRIORITY_LABELS, PRIORITY_COLORS } from "@/types";
import TaskNotification from "./TaskNotification";
import { TaskEventType } from "@/lib/task-events";

interface TaskNotificationData {
  id: string;
  taskId: string;
  type: TaskEventType;
  message: string;
  timestamp: number;
}

interface TaskItemProps {
  task: Task;
  onUpdate: (id: string, updates: Partial<Task>) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  notification?: TaskNotificationData;
}

// Format due date for display
function formatDueDate(dateStr: string): { text: string; isOverdue: boolean; isSoon: boolean } {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = date.getTime() - now.getTime();
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

  const isOverdue = diffMs < 0;
  const isSoon = diffDays >= 0 && diffDays <= 2;

  if (isOverdue) {
    const daysAgo = Math.abs(diffDays);
    return {
      text: daysAgo === 0 ? "Due today" : daysAgo === 1 ? "1 day overdue" : `${daysAgo} days overdue`,
      isOverdue: true,
      isSoon: false,
    };
  }

  if (diffDays === 0) {
    return { text: "Due today", isOverdue: false, isSoon: true };
  } else if (diffDays === 1) {
    return { text: "Due tomorrow", isOverdue: false, isSoon: true };
  } else if (diffDays <= 7) {
    return { text: `Due in ${diffDays} days`, isOverdue: false, isSoon };
  } else {
    return {
      text: date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
      isOverdue: false,
      isSoon: false,
    };
  }
}

export default function TaskItem({ task, onUpdate, onDelete, notification }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [loading, setLoading] = useState(false);

  const handleToggleComplete = async () => {
    setLoading(true);
    try {
      await onUpdate(task.id, { completed: !task.completed });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    setLoading(true);
    try {
      await onDelete(task.id);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!editTitle.trim() || editTitle === task.title) {
      setIsEditing(false);
      setEditTitle(task.title);
      return;
    }

    setLoading(true);
    try {
      await onUpdate(task.id, { title: editTitle.trim() });
      setIsEditing(false);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSaveEdit();
    } else if (e.key === "Escape") {
      setIsEditing(false);
      setEditTitle(task.title);
    }
  };

  const dueDateInfo = task.due_date ? formatDueDate(task.due_date) : null;

  return (
    <li
      className={`p-4 bg-white rounded-lg shadow-sm border border-gray-200 ${
        loading ? "opacity-50" : ""
      } ${task.completed ? "bg-gray-50" : ""}`}
    >
      {/* Main Row */}
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={handleToggleComplete}
          disabled={loading}
          className="mt-1 h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
        />

        <div className="flex-1 min-w-0">
          {isEditing ? (
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onBlur={handleSaveEdit}
              onKeyDown={handleKeyDown}
              autoFocus
              className="w-full px-2 py-1 border border-blue-500 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          ) : (
            <span
              className={`block ${
                task.completed ? "line-through text-gray-400" : "text-gray-900"
              }`}
              onDoubleClick={() => setIsEditing(true)}
            >
              {task.title}
            </span>
          )}

          {/* Meta Row: Due Date, Priority, Tags */}
          <div className="flex flex-wrap items-center gap-2 mt-2">
            {/* Priority Badge */}
            {task.priority && (
              <span
                className={`px-2 py-0.5 text-xs font-medium rounded-full border ${
                  PRIORITY_COLORS[task.priority]
                }`}
              >
                {PRIORITY_LABELS[task.priority]}
              </span>
            )}

            {/* Due Date */}
            {dueDateInfo && !task.completed && (
              <span
                className={`flex items-center gap-1 px-2 py-0.5 text-xs rounded-full ${
                  dueDateInfo.isOverdue
                    ? "bg-red-100 text-red-700"
                    : dueDateInfo.isSoon
                    ? "bg-amber-100 text-amber-700"
                    : "bg-gray-100 text-gray-600"
                }`}
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                {dueDateInfo.text}
              </span>
            )}

            {/* Tags */}
            {task.tags && task.tags.length > 0 && (
              <>
                {task.tags.map((tag) => (
                  <span
                    key={tag.id}
                    className="px-2 py-0.5 text-xs rounded-full text-white"
                    style={{ backgroundColor: tag.color }}
                  >
                    {tag.name}
                  </span>
                ))}
              </>
            )}

            {/* Recurrence indicator */}
            {task.recurrence_rule && (
              <span className="flex items-center gap-1 px-2 py-0.5 text-xs bg-purple-100 text-purple-700 rounded-full">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                Recurring
              </span>
            )}
          </div>
        </div>

        {notification && (
          <TaskNotification
            message={notification.message}
            type={notification.type}
          />
        )}

        {/* Action Buttons */}
        <div className="flex gap-2 shrink-0">
          {!isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              disabled={loading}
              className="text-gray-400 hover:text-blue-600 focus:outline-none"
              title="Edit task"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
              </svg>
            </button>
          )}
          <button
            onClick={handleDelete}
            disabled={loading}
            className="text-gray-400 hover:text-red-600 focus:outline-none"
            title="Delete task"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>
      </div>
    </li>
  );
}
