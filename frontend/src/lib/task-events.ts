/**
 * Task Event System
 *
 * Enables real-time communication between ChatWidget and Dashboard
 * when tasks are modified via the chatbot.
 */

export type TaskEventType = 'added' | 'completed' | 'updated' | 'deleted';

export interface TaskEvent {
  type: TaskEventType;
  taskId?: string;
  taskTitle?: string;
  timestamp: number;
}

type TaskEventListener = (event: TaskEvent) => void;

class TaskEventEmitter {
  private listeners: Set<TaskEventListener> = new Set();

  subscribe(listener: TaskEventListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  emit(event: TaskEvent): void {
    this.listeners.forEach((listener) => listener(event));
  }

  // Convenience methods
  taskAdded(taskId: string, taskTitle: string): void {
    this.emit({ type: 'added', taskId, taskTitle, timestamp: Date.now() });
  }

  taskCompleted(taskId: string, taskTitle: string): void {
    this.emit({ type: 'completed', taskId, taskTitle, timestamp: Date.now() });
  }

  taskUpdated(taskId: string, taskTitle: string): void {
    this.emit({ type: 'updated', taskId, taskTitle, timestamp: Date.now() });
  }

  taskDeleted(taskId: string, taskTitle: string): void {
    this.emit({ type: 'deleted', taskId, taskTitle, timestamp: Date.now() });
  }
}

// Singleton instance
export const taskEvents = new TaskEventEmitter();
