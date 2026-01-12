/**
 * Chat API client for Phase 3 AI-powered task management
 *
 * Provides functions to:
 * - Send messages to the chat endpoint
 * - Load conversation history
 * - Handle API errors with proper types
 */

/**
 * Chat message interface
 */
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

/**
 * Base API URL from environment variables
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Chat API response interface
 */
export interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls?: Array<{
    tool: string;
    arguments: Record<string, any>;
    result: any;
  }>;
}

/**
 * API Error class for better error handling
 */
export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * Send a message to the chat endpoint
 *
 * @param message - User message content
 * @param conversationId - Optional conversation ID (null for new conversations)
 * @param token - JWT authentication token
 * @returns Chat response with conversation_id and assistant response
 * @throws APIError on request failure
 */
export async function sendMessage(
  message: string,
  conversationId: number | null,
  token: string
): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.detail || `Request failed with status ${response.status}`,
        response.status,
        errorData
      );
    }

    const data = await response.json();
    return data;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new APIError('Network error. Please check your connection.', undefined, error);
    }

    throw new APIError('An unexpected error occurred', undefined, error);
  }
}

/**
 * Load conversation history
 *
 * @param conversationId - ID of the conversation to load
 * @returns Array of messages in chronological order
 * @throws APIError on request failure
 */
export async function loadHistory(conversationId: number): Promise<ChatMessage[]> {
  try {
    const token = localStorage.getItem('todo_auth_token');

    if (!token) {
      throw new APIError('Authentication required', 401);
    }

    const response = await fetch(
      `${API_BASE_URL}/api/conversations/${conversationId}/history`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.detail || `Request failed with status ${response.status}`,
        response.status,
        errorData
      );
    }

    const data = await response.json();
    return data.messages || [];
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new APIError('Network error. Please check your connection.', undefined, error);
    }

    throw new APIError('An unexpected error occurred', undefined, error);
  }
}

/**
 * Create a new conversation
 *
 * @param token - JWT authentication token
 * @returns New conversation ID
 * @throws APIError on request failure
 */
export async function createConversation(token: string): Promise<number> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({}),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.detail || `Request failed with status ${response.status}`,
        response.status,
        errorData
      );
    }

    const data = await response.json();
    return data.conversation_id;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new APIError('Network error. Please check your connection.', undefined, error);
    }

    throw new APIError('An unexpected error occurred', undefined, error);
  }
}

/**
 * Get user's active/latest conversation with history
 *
 * @returns Object with conversation_id and messages, or null conversation_id if none exists
 * @throws APIError on request failure
 */
export async function getActiveConversation(): Promise<{
  conversation_id: number | null;
  messages: ChatMessage[];
}> {
  try {
    const token = localStorage.getItem('todo_auth_token');

    if (!token) {
      throw new APIError('Authentication required', 401);
    }

    const response = await fetch(`${API_BASE_URL}/api/conversations/active`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.detail || `Request failed with status ${response.status}`,
        response.status,
        errorData
      );
    }

    const data = await response.json();
    return {
      conversation_id: data.conversation_id,
      messages: data.messages || [],
    };
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new APIError('Network error. Please check your connection.', undefined, error);
    }

    throw new APIError('An unexpected error occurred', undefined, error);
  }
}
