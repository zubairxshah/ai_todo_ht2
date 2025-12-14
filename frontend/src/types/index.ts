export interface Task {
  id: string;
  title: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
}

export interface TaskUpdate {
  title?: string;
  completed?: boolean;
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
