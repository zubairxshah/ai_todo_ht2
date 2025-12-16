import type {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskFilterParams,
  Tag,
  TagCreate,
  TagUpdate,
  TagWithCount,
} from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null): void {
    this.token = token;
  }

  async request<T>(
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

  // Build query string from filter params
  private buildQueryString(params: TaskFilterParams): string {
    const searchParams = new URLSearchParams();

    if (params.status && params.status !== "all") {
      searchParams.append("status", params.status);
    }
    if (params.priority !== undefined) {
      searchParams.append("priority", params.priority.toString());
    }
    if (params.tag_id) {
      searchParams.append("tag_id", params.tag_id);
    }
    if (params.search) {
      searchParams.append("search", params.search);
    }
    if (params.overdue) {
      searchParams.append("overdue", "true");
    }
    if (params.sort_by) {
      searchParams.append("sort_by", params.sort_by);
    }
    if (params.sort_order) {
      searchParams.append("sort_order", params.sort_order);
    }

    const queryString = searchParams.toString();
    return queryString ? `?${queryString}` : "";
  }

  // Task operations
  async getTasks(filters?: TaskFilterParams): Promise<Task[]> {
    const query = filters ? this.buildQueryString(filters) : "";
    return this.request<Task[]>(`/api/tasks${query}`);
  }

  async getTask(id: string): Promise<Task> {
    return this.request<Task>(`/api/tasks/${id}`);
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

  // Tag operations
  async getTags(): Promise<TagWithCount[]> {
    return this.request<TagWithCount[]>("/api/tags");
  }

  async getTag(id: string): Promise<TagWithCount> {
    return this.request<TagWithCount>(`/api/tags/${id}`);
  }

  async createTag(data: TagCreate): Promise<Tag> {
    return this.request<Tag>("/api/tags", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateTag(id: string, data: TagUpdate): Promise<Tag> {
    return this.request<Tag>(`/api/tags/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async deleteTag(id: string): Promise<void> {
    return this.request<void>(`/api/tags/${id}`, {
      method: "DELETE",
    });
  }
}

export const api = new ApiClient();
