// Phase V: Enhanced types with due dates, priorities, tags, and recurrence

export interface Tag {
  id: string;
  name: string;
  color: string;
}

export interface Task {
  id: string;
  title: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  // Phase V fields
  due_date?: string | null;
  remind_at?: string | null;
  priority?: number | null; // 1=High, 2=Medium, 3=Low
  recurrence_rule?: string | null;
  recurrence_end_date?: string | null;
  parent_task_id?: string | null;
  tags?: Tag[];
}

export interface TaskCreate {
  title: string;
  due_date?: string;
  remind_at?: string;
  priority?: number;
  recurrence_rule?: string;
  recurrence_end_date?: string;
  tag_ids?: string[];
}

export interface TaskUpdate {
  title?: string;
  completed?: boolean;
  due_date?: string | null;
  remind_at?: string | null;
  priority?: number | null;
  recurrence_rule?: string | null;
  recurrence_end_date?: string | null;
  tag_ids?: string[];
}

export interface TaskFilterParams {
  status?: "all" | "completed" | "pending";
  priority?: number;
  tag_id?: string;
  search?: string;
  overdue?: boolean;
  sort_by?: "due_date" | "priority" | "title" | "created_at";
  sort_order?: "asc" | "desc";
}

export interface TagCreate {
  name: string;
  color?: string;
}

export interface TagUpdate {
  name?: string;
  color?: string;
}

export interface TagWithCount extends Tag {
  created_at: string;
  task_count: number;
}

export interface User {
  id: string;
  email: string;
  name?: string;
}

export interface AuthSession {
  user: User;
  token: string;
}

// Priority helpers
export const PRIORITY_LABELS: Record<number, string> = {
  1: "High",
  2: "Medium",
  3: "Low",
};

export const PRIORITY_COLORS: Record<number, string> = {
  1: "text-red-600 bg-red-50 border-red-200",
  2: "text-yellow-600 bg-yellow-50 border-yellow-200",
  3: "text-green-600 bg-green-50 border-green-200",
};
