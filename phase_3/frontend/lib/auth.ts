/**
 * Authentication utilities for token storage and management.
 */

const TOKEN_KEY = 'todo_auth_token'
const USER_KEY = 'todo_user'

import type { User } from '@/types'

/**
 * Get the stored JWT token.
 */
export function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * Set the JWT token in storage.
 */
export function setToken(token: string): void {
  if (typeof window === 'undefined') return
  localStorage.setItem(TOKEN_KEY, token)
}

/**
 * Clear the JWT token from storage.
 */
export function clearToken(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem(TOKEN_KEY)
}

/**
 * Get the stored user data.
 */
export function getUser(): User | null {
  if (typeof window === 'undefined') return null
  const userStr = localStorage.getItem(USER_KEY)
  if (!userStr) return null
  try {
    return JSON.parse(userStr) as User
  } catch {
    return null
  }
}

/**
 * Set the user data in storage.
 */
export function setUser(user: User): void {
  if (typeof window === 'undefined') return
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

/**
 * Clear the user data from storage.
 */
export function clearUser(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem(USER_KEY)
}

/**
 * Clear all auth data (token, user, and conversation).
 */
export function clearAuth(): void {
  clearToken()
  clearUser()
  // Clear conversation ID to prevent "conversation not found" errors for new users
  if (typeof window !== 'undefined') {
    localStorage.removeItem('phase3_conversation_id')
  }
}

/**
 * Check if user is authenticated.
 */
export function isAuthenticated(): boolean {
  return getToken() !== null
}

/**
 * Store auth response data.
 */
export function storeAuthData(token: string, user: User): void {
  setToken(token)
  setUser(user)
}
