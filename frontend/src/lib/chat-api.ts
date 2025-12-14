import { api } from './api';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tool_calls?: Record<string, unknown>;
  created_at: string;
}

export interface TaskResult {
  id: string;
  title: string;
  completed?: boolean;
}

export interface ActionResult {
  success: boolean;
  task?: TaskResult;
  tasks?: TaskResult[];
  deleted?: TaskResult[];
  message?: string;
}

export interface ActionTaken {
  tool: string;
  input: Record<string, unknown>;
  result: ActionResult;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  actions_taken: ActionTaken[];
  metadata?: Record<string, unknown>;
}

export interface Conversation {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface HistoryResponse {
  conversations: Conversation[];
  messages: ChatMessage[];
  total: number;
  has_more: boolean;
}

export const chatApi = {
  async sendMessage(message: string, conversationId?: string): Promise<ChatResponse> {
    return api.request<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    });
  },

  async getHistory(conversationId?: string, limit = 50): Promise<HistoryResponse> {
    const params = new URLSearchParams();
    if (conversationId) params.set('conversation_id', conversationId);
    params.set('limit', limit.toString());

    return api.request<HistoryResponse>(`/api/chat/history?${params}`);
  },

  async clearHistory(conversationId?: string): Promise<{ deleted: boolean }> {
    const params = conversationId ? `?conversation_id=${conversationId}` : '';
    return api.request<{ deleted: boolean }>(`/api/chat/history${params}`, {
      method: 'DELETE',
    });
  },
};
