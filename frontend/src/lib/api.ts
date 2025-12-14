import type { Task, TaskCreate, TaskUpdate } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null): void {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (this.token) {
      (headers as Record<string, string>)["Authorization"] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Unauthorized - please log in again");
      }
      if (response.status === 403) {
        throw new Error("Forbidden - you don't have permission for this action");
      }
      if (response.status === 404) {
        throw new Error("Not found");
      }
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || "An error occurred");
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  // Task operations
  async getTasks(): Promise<Task[]> {
    return this.request<Task[]>("/api/tasks");
  }

  async createTask(data: TaskCreate): Promise<Task> {
    return this.request<Task>("/api/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateTask(id: string, data: TaskUpdate): Promise<Task> {
    return this.request<Task>(`/api/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async deleteTask(id: string): Promise<void> {
    return this.request<void>(`/api/tasks/${id}`, {
      method: "DELETE",
    });
  }
}

export const api = new ApiClient();
