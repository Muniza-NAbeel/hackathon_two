/**
 * API client with JWT authentication headers.
 */

import { getToken, clearAuth } from './auth'
import type {
  AuthResponse,
  Task,
  TaskCreate,
  TaskFilters,
  TaskListResponse,
  TaskUpdate,
  UserLogin,
  UserRegister,
  ErrorResponse,
} from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Custom API error with structured error response.
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public field?: string | null
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

/**
 * Make an authenticated API request.
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  let response: Response
  try {
    response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    })
  } catch (error) {
    // Handle network errors (connection refused, timeout, etc.)
    console.error('Network error:', error)
    throw new ApiError(
      0,
      'NETWORK_ERROR',
      'Unable to connect to the server. Please check your connection and try again.'
    )
  }

  // Handle 401 - redirect to login (but not for auth endpoints)
  if (response.status === 401) {
    // Don't redirect if we're trying to login/register (let the form handle it)
    const isAuthEndpoint = endpoint.includes('/api/auth/login') || endpoint.includes('/api/auth/register')

    if (!isAuthEndpoint) {
      clearAuth()
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }
    throw new ApiError(401, 'UNAUTHORIZED', 'Invalid credentials or session expired.')
  }

  // Handle error responses
  if (!response.ok) {
    let errorData: ErrorResponse
    try {
      const data = await response.json()
      // Handle FastAPI's error format
      if (data.detail && typeof data.detail === 'object') {
        errorData = data.detail
      } else if (data.detail && typeof data.detail === 'string') {
        errorData = { detail: data.detail, code: 'ERROR' }
      } else {
        errorData = data
      }
    } catch {
      errorData = {
        detail: 'An unexpected error occurred',
        code: 'INTERNAL_ERROR',
      }
    }
    throw new ApiError(
      response.status,
      errorData.code || 'ERROR',
      errorData.detail || 'An error occurred',
      errorData.field
    )
  }

  // Handle empty responses
  if (response.status === 204) {
    return {} as T
  }

  return response.json()
}

// ============================================================================
// Auth API
// ============================================================================

export async function register(data: UserRegister): Promise<AuthResponse> {
  return apiRequest<AuthResponse>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function login(data: UserLogin): Promise<AuthResponse> {
  return apiRequest<AuthResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function logout(): Promise<void> {
  await apiRequest<{ message: string }>('/api/auth/logout', {
    method: 'POST',
  })
}

export async function getCurrentUser(): Promise<AuthResponse['user']> {
  return apiRequest<AuthResponse['user']>('/api/auth/me')
}

// ============================================================================
// Tasks API
// ============================================================================

export async function getTasks(
  userId: string,
  filters?: TaskFilters
): Promise<TaskListResponse> {
  const params = new URLSearchParams()
  if (filters?.status && filters.status !== 'all') {
    params.append('status', filters.status)
  }
  if (filters?.sort_by) {
    params.append('sort_by', filters.sort_by)
  }
  if (filters?.sort_order) {
    params.append('sort_order', filters.sort_order)
  }
  if (filters?.page) {
    params.append('page', filters.page.toString())
  }
  if (filters?.per_page) {
    params.append('per_page', filters.per_page.toString())
  }

  const queryString = params.toString()
  const endpoint = `/api/${userId}/tasks${queryString ? `?${queryString}` : ''}`
  return apiRequest<TaskListResponse>(endpoint)
}

export async function getTask(userId: string, taskId: number): Promise<Task> {
  return apiRequest<Task>(`/api/${userId}/tasks/${taskId}`)
}

export async function createTask(
  userId: string,
  data: TaskCreate
): Promise<Task> {
  return apiRequest<Task>(`/api/${userId}/tasks`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateTask(
  userId: string,
  taskId: number,
  data: TaskUpdate
): Promise<Task> {
  return apiRequest<Task>(`/api/${userId}/tasks/${taskId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteTask(userId: string, taskId: number): Promise<void> {
  await apiRequest<void>(`/api/${userId}/tasks/${taskId}`, {
    method: 'DELETE',
  })
}

export async function toggleTaskComplete(
  userId: string,
  taskId: number
): Promise<Task> {
  return apiRequest<Task>(`/api/${userId}/tasks/${taskId}/complete`, {
    method: 'PATCH',
  })
}
