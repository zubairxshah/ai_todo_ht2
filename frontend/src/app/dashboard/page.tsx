"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useSession, signOut, getJwtToken } from "@/lib/auth";
import { api } from "@/lib/api";
import type { Task } from "@/types";
import TaskForm from "@/components/TaskForm";
import TaskList from "@/components/TaskList";
import { ChatWidget } from "@/components/Chat";
import { taskEvents, TaskEvent, TaskEventType } from "@/lib/task-events";
import { ToastContainer } from "@/components/ToastNotification";

interface TaskNotification {
  id: string;
  taskId: string;
  taskTitle?: string;
  type: TaskEventType;
  message: string;
  timestamp: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const { data: session, isPending } = useSession();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [tokenReady, setTokenReady] = useState(false);
  const [notifications, setNotifications] = useState<TaskNotification[]>([]);

  useEffect(() => {
    if (!isPending && !session) {
      router.push("/login");
    }
  }, [session, isPending, router]);

  // Fetch JWT token when session is available
  useEffect(() => {
    async function fetchToken() {
      if (session) {
        const token = await getJwtToken();
        if (token) {
          api.setToken(token);
          setTokenReady(true);
        } else {
          setError("Failed to get authentication token");
          setLoading(false);
        }
      }
    }
    fetchToken();
  }, [session]);

  // Load tasks once token is ready
  useEffect(() => {
    if (tokenReady) {
      loadTasks();
    }
  }, [tokenReady]);

  // Subscribe to task events from chatbot
  useEffect(() => {
    const unsubscribe = taskEvents.subscribe((event: TaskEvent) => {
      // Create notification
      const notificationMessages: Record<TaskEventType, string> = {
        added: "Task added via chat",
        completed: "Completed via chat",
        updated: "Updated via chat",
        deleted: "Deleted via chat",
      };

      const notification: TaskNotification = {
        id: `notif-${Date.now()}-${Math.random()}`,
        taskId: event.taskId || "",
        taskTitle: event.taskTitle,
        type: event.type,
        message: notificationMessages[event.type],
        timestamp: event.timestamp,
      };

      setNotifications((prev) => [...prev, notification]);

      // Reload tasks to reflect changes from chatbot
      loadTasks();
    });

    return () => unsubscribe();
  }, [tokenReady]);

  // Remove notification handler
  const removeNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const loadTasks = async () => {
    if (!tokenReady) return;
    try {
      setLoading(true);
      const data = await api.getTasks();
      setTasks(data);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (title: string) => {
    try {
      const newTask = await api.createTask({ title });
      setTasks([newTask, ...tasks]);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create task");
    }
  };

  const handleUpdateTask = async (id: string, updates: Partial<Task>) => {
    try {
      const updatedTask = await api.updateTask(id, updates);
      setTasks(tasks.map((t) => (t.id === id ? updatedTask : t)));
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update task");
    }
  };

  const handleDeleteTask = async (id: string) => {
    try {
      await api.deleteTask(id);
      setTasks(tasks.filter((t) => t.id !== id));
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete task");
    }
  };

  const handleLogout = async () => {
    await signOut();
    api.setToken(null);
    router.push("/login");
  };

  // Get notification for a specific task
  const getTaskNotification = (taskId: string): TaskNotification | undefined => {
    return notifications.find((n) => n.taskId === taskId);
  };

  if (isPending) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!session) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex flex-col">
      {/* Toast Notifications */}
      <ToastContainer notifications={notifications} onRemove={removeNotification} />

      {/* Header with Logo */}
      <header className="bg-white/80 backdrop-blur-md shadow-sm border-b border-white/20 sticky top-0 z-40">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            {/* Logo */}
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg animate-pulse-glow">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-white animate-pulse"></div>
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
                AI Todo
              </h1>
              <p className="text-xs text-gray-500">Powered by MCP</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600 hidden sm:block">{session.user?.email}</span>
            <button
              onClick={handleLogout}
              className="px-3 py-1.5 text-sm text-gray-600 hover:text-white hover:bg-gradient-to-r hover:from-red-500 hover:to-rose-500 rounded-lg transition-all duration-300"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-4xl mx-auto px-4 py-8 w-full">
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl shadow-sm">
            {error}
          </div>
        )}

        <TaskForm onSubmit={handleCreateTask} />

        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <TaskList
            tasks={tasks}
            onUpdate={handleUpdateTask}
            onDelete={handleDeleteTask}
            notifications={notifications}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white/60 backdrop-blur-md border-t border-white/20 py-6">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex flex-col sm:flex-row items-center justify-center gap-2 text-center">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center shadow-md">
                <span className="text-white font-bold text-sm">M</span>
              </div>
              <span className="font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                MZS CodeWorks 2025
              </span>
            </div>
            <span className="text-gray-400 hidden sm:block">|</span>
            <div className="flex items-center gap-1.5 text-gray-600">
              <span>Made with</span>
              <span className="text-red-500 animate-pulse text-lg">&#10084;</span>
              <span>for</span>
              <span className="font-semibold bg-gradient-to-r from-amber-500 to-orange-500 bg-clip-text text-transparent">
                Hackathon 2
              </span>
            </div>
          </div>
          <div className="mt-3 flex justify-center">
            <div
              className="h-1 w-32 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"
              style={{
                backgroundSize: '200% 100%',
                animation: 'shimmer 2s linear infinite',
              }}
            ></div>
          </div>
        </div>
      </footer>

      {/* AI Chat Widget */}
      {tokenReady && <ChatWidget />}
    </div>
  );
}
