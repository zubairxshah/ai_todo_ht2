"use client";

import type { Task } from "@/types";
import TaskItem from "./TaskItem";
import { TaskEventType } from "@/lib/task-events";

interface TaskNotification {
  id: string;
  taskId: string;
  type: TaskEventType;
  message: string;
  timestamp: number;
}

interface TaskListProps {
  tasks: Task[];
  onUpdate: (id: string, updates: Partial<Task>) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  notifications?: TaskNotification[];
}

export default function TaskList({ tasks, onUpdate, onDelete, notifications = [] }: TaskListProps) {
  // Get notification for a specific task
  const getTaskNotification = (taskId: string): TaskNotification | undefined => {
    return notifications.find((n) => n.taskId === taskId);
  };

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">No tasks yet</p>
        <p className="text-sm mt-1">Add a task above to get started</p>
      </div>
    );
  }

  return (
    <ul className="space-y-2">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onUpdate={onUpdate}
          onDelete={onDelete}
          notification={getTaskNotification(task.id)}
        />
      ))}
    </ul>
  );
}
