/**
 * TypeScript type definitions per contracts/openapi.yaml
 */

// User types
export interface User {
  id: string
  email: string
  name: string | null
  created_at: string
}

export interface UserRegister {
  email: string
  password: string
  name?: string
}

export interface UserLogin {
  email: string
  password: string
}

// Auth types
export interface AuthResponse {
  user: User
  token: string
  expires_at: string
}

// Task types
export interface Task {
  id: string
  user_id: string
  title: string
  description: string | null
  completed: boolean
  due_date: string | null
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  title: string
  description?: string | null
  due_date?: string | null
}

export interface TaskUpdate {
  title?: string
  description?: string | null
  due_date?: string | null
}

export interface TaskListResponse {
  tasks: Task[]
  total_count: number
  page: number
  per_page: number
  total_pages: number
}

// Filter and sort types
export type TaskStatus = 'all' | 'pending' | 'completed'
export type TaskSortBy = 'title' | 'created_at' | 'due_date'
export type SortOrder = 'asc' | 'desc'

export interface TaskFilters {
  status?: TaskStatus
  sort_by?: TaskSortBy
  sort_order?: SortOrder
  page?: number
  per_page?: number
}

// Error types
export interface ErrorResponse {
  detail: string
  code: string
  field?: string | null
}

export interface ValidationErrorDetail {
  loc: string[]
  msg: string
  type: string
}

export interface ValidationErrorResponse {
  detail: ValidationErrorDetail[]
}

// API response wrapper
export type ApiResponse<T> =
  | { success: true; data: T }
  | { success: false; error: ErrorResponse }
