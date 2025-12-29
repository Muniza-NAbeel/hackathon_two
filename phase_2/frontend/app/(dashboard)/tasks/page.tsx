'use client'

import { useState, useEffect, useCallback } from 'react'
import { getUser } from '@/lib/auth'
import {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
  toggleTaskComplete,
  ApiError,
} from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { TaskList } from '@/components/tasks/TaskList'
import { TaskForm } from '@/components/tasks/TaskForm'
import { TaskFilters } from '@/components/tasks/TaskFilters'
import type {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskStatus,
  TaskSortBy,
  SortOrder,
} from '@/types'

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Form modal state
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingTask, setEditingTask] = useState<Task | null>(null)

  // Filter state
  const [status, setStatus] = useState<TaskStatus>('all')
  const [sortBy, setSortBy] = useState<TaskSortBy>('created_at')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')

  // Pagination state
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [totalCount, setTotalCount] = useState(0)

  // Get user once on mount to avoid infinite loop
  const [user] = useState(() => getUser())

  const fetchTasks = useCallback(async () => {
    if (!user) return

    setLoading(true)
    setError(null)

    try {
      const response = await getTasks(user.id, {
        status,
        sort_by: sortBy,
        sort_order: sortOrder,
        page,
        per_page: 50,
      })
      setTasks(response.tasks)
      setTotalPages(response.total_pages)
      setTotalCount(response.total_count)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Failed to load tasks')
      }
    } finally {
      setLoading(false)
    }
  }, [user, status, sortBy, sortOrder, page])

  useEffect(() => {
    fetchTasks()
  }, [fetchTasks])

  // Persist filter preferences
  useEffect(() => {
    if (typeof window !== 'undefined') {
      sessionStorage.setItem(
        'taskFilters',
        JSON.stringify({ status, sortBy, sortOrder })
      )
    }
  }, [status, sortBy, sortOrder])

  // Load filter preferences
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const saved = sessionStorage.getItem('taskFilters')
      if (saved) {
        try {
          const { status: s, sortBy: sb, sortOrder: so } = JSON.parse(saved)
          if (s) setStatus(s)
          if (sb) setSortBy(sb)
          if (so) setSortOrder(so)
        } catch {
          // Ignore parse errors
        }
      }
    }
  }, [])

  const handleCreateTask = async (data: TaskCreate | TaskUpdate) => {
    if (!user) return
    try {
      await createTask(user.id, data as TaskCreate)
      await fetchTasks()
    } catch (err) {
      // Re-throw to let TaskForm handle it
      throw err
    }
  }

  const handleUpdateTask = async (data: TaskCreate | TaskUpdate) => {
    if (!user || !editingTask) return
    try {
      await updateTask(user.id, editingTask.id, data as TaskUpdate)
      await fetchTasks()
    } catch (err) {
      // Re-throw to let TaskForm handle it
      throw err
    }
  }

  const handleDeleteTask = async (taskId: string) => {
    if (!user) return
    await deleteTask(user.id, taskId)
    await fetchTasks()
  }

  const handleToggleComplete = async (taskId: string) => {
    if (!user) return
    await toggleTaskComplete(user.id, taskId)
    await fetchTasks()
  }

  const handleOpenCreate = () => {
    setEditingTask(null)
    setIsFormOpen(true)
  }

  const handleOpenEdit = (task: Task) => {
    setEditingTask(task)
    setIsFormOpen(true)
  }

  const handleCloseForm = () => {
    setIsFormOpen(false)
    setEditingTask(null)
  }

  // Calculate stats from current tasks
  const completedCount = tasks.filter((t) => t.completed).length
  const pendingCount = tasks.filter((t) => !t.completed).length

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">My Tasks</h1>
          <p className="text-gray-400 text-lg">
            {totalCount} {totalCount === 1 ? 'task' : 'tasks'} total
          </p>
        </div>
        <Button onClick={handleOpenCreate}>
          <svg
            className="-ml-1 mr-2 h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          Add Task
        </Button>
      </div>

      {/* Task Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-dark-card/50 backdrop-blur-xl p-6 rounded-lg border border-dark-border hover:border-neon-blue/50 transition-all">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-400">Total</p>
              <p className="text-3xl font-bold text-white mt-1">{totalCount}</p>
            </div>
            <div className="h-14 w-14 bg-neon-blue/20 rounded-full flex items-center justify-center ring-2 ring-neon-blue/30">
              <svg className="h-7 w-7 text-neon-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-dark-card/50 backdrop-blur-xl p-6 rounded-lg border border-dark-border hover:border-green-500/50 transition-all">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-400">Completed</p>
              <p className="text-3xl font-bold text-green-400 mt-1">{completedCount}</p>
            </div>
            <div className="h-14 w-14 bg-green-500/20 rounded-full flex items-center justify-center ring-2 ring-green-500/30">
              <svg className="h-7 w-7 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-dark-card/50 backdrop-blur-xl p-6 rounded-lg border border-dark-border hover:border-yellow-500/50 transition-all">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-400">Pending</p>
              <p className="text-3xl font-bold text-yellow-400 mt-1">{pendingCount}</p>
            </div>
            <div className="h-14 w-14 bg-yellow-500/20 rounded-full flex items-center justify-center ring-2 ring-yellow-500/30">
              <svg className="h-7 w-7 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-dark-card/50 backdrop-blur-xl p-6 rounded-lg border border-dark-border">
        <TaskFilters
          status={status}
          sortBy={sortBy}
          sortOrder={sortOrder}
          onStatusChange={(s) => {
            setStatus(s)
            setPage(1)
          }}
          onSortByChange={(s) => {
            setSortBy(s)
            setPage(1)
          }}
          onSortOrderChange={(s) => {
            setSortOrder(s)
            setPage(1)
          }}
        />
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 backdrop-blur-xl">
          {error}
          <button
            onClick={fetchTasks}
            className="ml-2 underline hover:no-underline hover:text-red-300 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Task list */}
      <TaskList
        tasks={tasks}
        loading={loading}
        onToggleComplete={handleToggleComplete}
        onEdit={handleOpenEdit}
        onDelete={handleDeleteTask}
        onCreateFirst={handleOpenCreate}
      />

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <span className="px-4 py-2 text-sm text-gray-600">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            Next
          </Button>
        </div>
      )}

      {/* Task form modal */}
      <TaskForm
        isOpen={isFormOpen}
        onClose={handleCloseForm}
        onSubmit={editingTask ? handleUpdateTask : handleCreateTask}
        task={editingTask}
        mode={editingTask ? 'edit' : 'create'}
      />
    </div>
  )
}
