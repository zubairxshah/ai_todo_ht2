'use client';

/**
 * ChatKit Widget Component
 *
 * Integrates with OpenAI ChatKit frontend or provides a fallback
 * SSE-based chat implementation for the Todo Assistant.
 *
 * Features:
 * - SSE streaming for real-time responses
 * - Task event emission for dashboard updates
 * - Thread/conversation management
 * - JWT authentication pass-through
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import { taskEvents } from '@/lib/task-events';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ToolCallEvent {
  tool_name: string;
  arguments: Record<string, unknown>;
  result: {
    success?: boolean;
    task?: { id: string; title: string };
    deleted?: Array<{ id: string; title: string }>;
  };
}

// Process tool call events and emit task events
function processToolCall(toolCall: ToolCallEvent): void {
  const { tool_name, result } = toolCall;

  if (!result.success) return;

  switch (tool_name) {
    case 'add_task':
      if (result.task) {
        taskEvents.taskAdded(result.task.id, result.task.title);
      }
      break;

    case 'complete_task':
      if (result.task) {
        taskEvents.taskCompleted(result.task.id, result.task.title);
      }
      break;

    case 'update_task':
      if (result.task) {
        taskEvents.taskUpdated(result.task.id, result.task.title);
      }
      break;

    case 'delete_task':
      if (result.deleted && Array.isArray(result.deleted)) {
        for (const deleted of result.deleted) {
          taskEvents.taskDeleted(deleted.id, deleted.title);
        }
      }
      break;
  }
}

export default function ChatKitWidget() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [streamingContent, setStreamingContent] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

  const getToken = useCallback(() => {
    if (typeof window !== 'undefined') {
      return sessionStorage.getItem('auth-jwt');
    }
    return null;
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const token = getToken();
    if (!token) {
      setError('Not authenticated. Please log in again.');
      return;
    }

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);
    setStreamingContent('');

    // Create AbortController for this request
    abortControllerRef.current = new AbortController();

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/chatkit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: userMessage.content,
          thread_id: threadId,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      // Get thread ID from header
      const newThreadId = response.headers.get('X-Thread-Id');
      if (newThreadId) {
        setThreadId(newThreadId);
      }

      // Process SSE stream
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantContent = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const eventData = JSON.parse(line.slice(6));

                switch (eventData.type) {
                  case 'thread.created':
                    setThreadId(eventData.thread_id);
                    break;

                  case 'tool_call':
                    processToolCall(eventData);
                    break;

                  case 'message.delta':
                    if (eventData.delta?.content) {
                      assistantContent += eventData.delta.content;
                      setStreamingContent(assistantContent);
                    }
                    break;

                  case 'message.done':
                    assistantContent = eventData.content || assistantContent;
                    break;

                  case 'done':
                    // Stream complete
                    break;
                }
              } catch {
                // Ignore parse errors for incomplete chunks
              }
            }
          }
        }
      }

      // Add final assistant message
      if (assistantContent) {
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: assistantContent,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      }
      setStreamingContent('');
    } catch (err) {
      if ((err as Error).name === 'AbortError') {
        // Request was cancelled
        return;
      }
      console.error('Chat error:', err);
      setError('Failed to send message. Please try again.');
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleNewChat = () => {
    // Cancel any in-flight request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setMessages([]);
    setThreadId(null);
    setError(null);
    setStreamingContent('');
  };

  const handleClearChat = async () => {
    const token = getToken();
    if (!token || !threadId) {
      handleNewChat();
      return;
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      await fetch(`${apiUrl}/api/chatkit/threads/${threadId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    } catch (err) {
      console.error('Failed to delete thread:', err);
    }

    handleNewChat();
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 w-14 h-14 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full shadow-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-300 flex items-center justify-center z-50 hover:scale-110"
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
      >
        {isOpen ? (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-20 right-4 w-96 h-[500px] bg-white/95 backdrop-blur-lg rounded-2xl shadow-2xl border border-gray-200/50 flex flex-col z-50 overflow-hidden">
          {/* Header */}
          <div className="p-4 border-b border-gray-200/50 flex justify-between items-center bg-gradient-to-r from-blue-600 to-purple-600 text-white">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-sm">Todo Assistant</h3>
                <p className="text-xs text-white/70">Powered by MCP</p>
              </div>
            </div>
            <div className="flex gap-1">
              <button
                onClick={handleNewChat}
                className="text-xs hover:bg-white/20 px-2 py-1 rounded-lg transition-colors"
                title="New conversation"
              >
                New
              </button>
              <button
                onClick={handleClearChat}
                className="text-xs hover:bg-white/20 px-2 py-1 rounded-lg transition-colors"
                title="Clear history"
              >
                Clear
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-gray-50/50 to-white/50">
            {messages.length === 0 && !streamingContent && (
              <div className="text-center text-gray-500 mt-8">
                <div className="text-4xl mb-4">👋</div>
                <p className="text-lg mb-2 font-medium">Hi! I&apos;m your todo assistant.</p>
                <p className="text-sm mb-4 text-gray-400">Try saying:</p>
                <div className="space-y-2">
                  <button
                    onClick={() => setInput('Add buy groceries')}
                    className="block w-full text-sm text-blue-600 hover:bg-blue-50 px-3 py-2 rounded-lg border border-blue-200/50 transition-colors"
                  >
                    &quot;Add buy groceries&quot;
                  </button>
                  <button
                    onClick={() => setInput('Show my tasks')}
                    className="block w-full text-sm text-blue-600 hover:bg-blue-50 px-3 py-2 rounded-lg border border-blue-200/50 transition-colors"
                  >
                    &quot;Show my tasks&quot;
                  </button>
                  <button
                    onClick={() => setInput('Mark groceries as done')}
                    className="block w-full text-sm text-blue-600 hover:bg-blue-50 px-3 py-2 rounded-lg border border-blue-200/50 transition-colors"
                  >
                    &quot;Mark groceries as done&quot;
                  </button>
                </div>
              </div>
            )}
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-2xl whitespace-pre-wrap shadow-sm ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-br-md'
                      : 'bg-white text-gray-800 border border-gray-100 rounded-bl-md'
                  }`}
                >
                  {message.content}
                </div>
              </div>
            ))}
            {/* Streaming content */}
            {streamingContent && (
              <div className="flex justify-start">
                <div className="max-w-[80%] p-3 rounded-2xl rounded-bl-md whitespace-pre-wrap bg-white text-gray-800 border border-gray-100 shadow-sm">
                  {streamingContent}
                  <span className="inline-block w-2 h-4 bg-blue-500 ml-1 animate-pulse" />
                </div>
              </div>
            )}
            {loading && !streamingContent && (
              <div className="flex justify-start">
                <div className="bg-white p-3 rounded-2xl rounded-bl-md border border-gray-100 shadow-sm">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            {error && (
              <div className="text-center text-red-500 text-sm bg-red-50 rounded-lg p-2">
                {error}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200/50 bg-white/80 backdrop-blur-sm">
            <div className="flex space-x-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type a message..."
                className="flex-1 p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent bg-white/80 transition-all"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  );
}
