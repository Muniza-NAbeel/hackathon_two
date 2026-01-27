/**
 * LocalStorage utilities for conversation persistence
 *
 * Provides safe access to localStorage with error handling and type safety.
 * Handles conversation_id persistence across page reloads.
 */

/**
 * Storage keys used throughout the application
 */
export const STORAGE_KEYS = {
  CONVERSATION_ID: 'phase3_conversation_id',
  JWT_TOKEN: 'auth_token',
} as const;

/**
 * Get conversation_id from localStorage
 *
 * @returns Conversation ID as number, or null if not found/invalid
 */
export function getConversationId(): number | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.CONVERSATION_ID);

    if (!stored) {
      return null;
    }

    const parsed = parseInt(stored, 10);

    // Validate that it's a valid number
    if (isNaN(parsed) || parsed <= 0) {
      console.warn('Invalid conversation_id in localStorage, clearing:', stored);
      clearConversationId();
      return null;
    }

    return parsed;
  } catch (error) {
    console.error('Error reading conversation_id from localStorage:', error);
    return null;
  }
}

/**
 * Set conversation_id in localStorage
 *
 * @param conversationId - The conversation ID to store
 * @throws Error if localStorage is not available
 */
export function setConversationId(conversationId: number): void {
  try {
    if (!conversationId || conversationId <= 0) {
      throw new Error('Invalid conversation_id: must be a positive integer');
    }

    localStorage.setItem(STORAGE_KEYS.CONVERSATION_ID, String(conversationId));
  } catch (error) {
    console.error('Error saving conversation_id to localStorage:', error);
    throw error;
  }
}

/**
 * Clear conversation_id from localStorage
 *
 * Used when starting a new conversation or on logout
 */
export function clearConversationId(): void {
  try {
    localStorage.removeItem(STORAGE_KEYS.CONVERSATION_ID);
  } catch (error) {
    console.error('Error clearing conversation_id from localStorage:', error);
  }
}

/**
 * Get JWT token from localStorage
 *
 * @returns JWT token string, or null if not found
 */
export function getAuthToken(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEYS.JWT_TOKEN);
  } catch (error) {
    console.error('Error reading auth token from localStorage:', error);
    return null;
  }
}

/**
 * Set JWT token in localStorage
 *
 * @param token - The JWT token to store
 */
export function setAuthToken(token: string): void {
  try {
    if (!token || token.trim() === '') {
      throw new Error('Invalid token: cannot be empty');
    }

    localStorage.setItem(STORAGE_KEYS.JWT_TOKEN, token);
  } catch (error) {
    console.error('Error saving auth token to localStorage:', error);
    throw error;
  }
}

/**
 * Clear JWT token from localStorage
 *
 * Used on logout
 */
export function clearAuthToken(): void {
  try {
    localStorage.removeItem(STORAGE_KEYS.JWT_TOKEN);
  } catch (error) {
    console.error('Error clearing auth token from localStorage:', error);
  }
}

/**
 * Clear all application data from localStorage
 *
 * Used on logout or when resetting application state
 */
export function clearAllStorage(): void {
  clearConversationId();
  clearAuthToken();
}

/**
 * Check if localStorage is available
 *
 * @returns true if localStorage is available and functional
 */
export function isLocalStorageAvailable(): boolean {
  try {
    const testKey = '__storage_test__';
    localStorage.setItem(testKey, 'test');
    localStorage.removeItem(testKey);
    return true;
  } catch (error) {
    return false;
  }
}
