'use client'

import { useState, useEffect, useMemo } from 'react'
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
import { LeftSidebar } from '@/components/tasks/LeftSidebar'
import { EnhancedTaskCard } from '@/components/tasks/EnhancedTaskCard'
import { EnhancedTaskForm } from '@/components/tasks/EnhancedTaskForm'
import { SearchBar } from '@/components/tasks/SearchBar'
import { HeaderSummary } from '@/components/tasks/HeaderSummary'
import { AIChatPanel } from '@/components/chat/AIChatPanel'
import { EmptyState } from '@/components/tasks/EmptyState'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import type {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskStatus,
  TaskSortBy,
  SortOrder,
} from '@/types'

export default function EnhancedTasksPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingTask, setEditingTask] = useState<Task | null>(null)

  // AI Chat Panel
  const [isChatOpen, setIsChatOpen] = useState(false)

  // Mobile sidebar
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  // Track toggling tasks to prevent multiple simultaneous requests
  const [togglingTasks, setTogglingTasks] = useState<Set<number>>(new Set())

  // Filters
  const [statusFilter, setStatusFilter] = useState<TaskStatus>('all')
  const [tagFilter, setTagFilter] = useState<string | null>(null)
  const [priorityFilter, setPriorityFilter] = useState<string | null>(null)
  const [quickView, setQuickView] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<TaskSortBy>('due_date')
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc')

  const [user] = useState(() => getUser())

  useEffect(() => {
    if (!user) return

    const loadTasks = async () => {
      setLoading(true)
      setError(null)

      try {
        const response = await getTasks(user.id, {
          status: 'all',
          sort_by: 'created_at',
          sort_order: 'desc',
          page: 1,
          per_page: 100,
        })
        setTasks(response.tasks)
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message)
        } else {
          setError('Failed to load tasks')
        }
      } finally {
        setLoading(false)
      }
    }

    loadTasks()

    // Listen for task modifications from chatbot
    const handleTaskModified = () => {
      console.log('Task modified event received - refreshing tasks')
      loadTasks()
    }

    window.addEventListener('taskModified', handleTaskModified)

    // Cleanup listener on unmount
    return () => {
      window.removeEventListener('taskModified', handleTaskModified)
    }
  }, [user])

  const availableTags = useMemo(() => {
    const set = new Set<string>()
    tasks.forEach(t => t.tags?.forEach(tag => set.add(tag)))
    return Array.from(set).sort()
  }, [tasks])

  const filteredAndSortedTasks = useMemo(() => {
    let filtered = [...tasks]

    if (statusFilter !== 'all') {
      if (statusFilter === 'completed') {
        filtered = filtered.filter(t => t.completed || t.status === 'completed')
      } else if (statusFilter === 'pending') {
        filtered = filtered.filter(t => !t.completed && t.status !== 'completed')
      } else {
        filtered = filtered.filter(t => t.status === statusFilter)
      }
    }

    if (tagFilter) {
      filtered = filtered.filter(t => t.tags?.includes(tagFilter))
    }

    if (priorityFilter) {
      filtered = filtered.filter(t => {
        // Normalize priority values for comparison (handle case sensitivity)
        const taskPriority = (t.priority || 'medium').toLowerCase()
        const filterPriority = priorityFilter.toLowerCase()
        return taskPriority === filterPriority
      })
    }

    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const weekFromNow = new Date(today.getTime() + 7 * 86400000)

    if (quickView === 'today') {
      filtered = filtered.filter(t => {
        if (!t.due_date) return false
        const d = new Date(t.due_date)
        return d >= today && d < new Date(today.getTime() + 86400000)
      })
    } else if (quickView === 'week') {
      filtered = filtered.filter(t => {
        if (!t.due_date) return false
        const d = new Date(t.due_date)
        return d >= today && d < weekFromNow
      })
    } else if (quickView === 'overdue') {
      filtered = filtered.filter(t => {
        if (!t.due_date) return false
        if (t.completed || t.status === 'completed') return false
        return new Date(t.due_date) < now
      })
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      filtered = filtered.filter(
        t =>
          t.title.toLowerCase().includes(q) ||
          t.description?.toLowerCase().includes(q) ||
          t.tags?.some(tag => tag.toLowerCase().includes(q))
      )
    }

    filtered.sort((a, b) => {
      let cmp = 0
      if (sortBy === 'title') cmp = a.title.localeCompare(b.title)
      if (sortBy === 'due_date') {
        cmp =
          (a.due_date ? new Date(a.due_date).getTime() : Infinity) -
          (b.due_date ? new Date(b.due_date).getTime() : Infinity)
      }
      if (sortBy === 'priority') {
        const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1 }
        cmp = (priorityOrder[a.priority as keyof typeof priorityOrder] || 0) -
              (priorityOrder[b.priority as keyof typeof priorityOrder] || 0)
      }
      if (sortBy === 'created_at') {
        cmp = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      }
      return sortOrder === 'asc' ? cmp : -cmp
    })

    return filtered
  }, [tasks, statusFilter, tagFilter, priorityFilter, quickView, searchQuery, sortBy, sortOrder])

  const totalCount = tasks.length
  const completedCount = tasks.filter(t => t.status === 'completed').length
  const pendingCount = tasks.filter(t => t.status !== 'completed').length

  const handleCreateTask = async (data: TaskCreate) => {
    if (!user) return
    const created = await createTask(user.id, data)
    setTasks([created, ...tasks])
  }

  const handleUpdateTask = async (data: TaskUpdate) => {
    if (!user || !editingTask) return
    const updated = await updateTask(user.id, editingTask.id, data)
    setTasks(tasks.map(t => (t.id === updated.id ? updated : t)))
  }

  const handleDeleteTask = async (id: number) => {
    if (!user) return
    await deleteTask(user.id, id)
    setTasks(tasks.filter(t => t.id !== id))
  }

  const handleToggleComplete = async (id: number) => {
    if (!user) return

    // Prevent multiple simultaneous toggles for the same task
    if (togglingTasks.has(id)) return

    // Add to toggling set
    setTogglingTasks(prev => new Set(prev).add(id))

    try {
      const updated = await toggleTaskComplete(user.id, id)
      setTasks(tasks.map(t => (t.id === id ? updated : t)))
    } catch (err) {
      console.error('Failed to toggle task:', err)
      if (err instanceof ApiError) {
        alert(`Failed to update task: ${err.message}`)
      } else {
        alert('Failed to update task. Please check your connection and try again.')
      }
    } finally {
      // Remove from toggling set after request completes
      setTogglingTasks(prev => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    }
  }

  const handleFormSubmit = async (data: TaskCreate | TaskUpdate) => {
    if (editingTask) {
      await handleUpdateTask(data as TaskUpdate)
    } else {
      await handleCreateTask(data as TaskCreate)
    }
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] transition-all duration-500 ease-in-out">
      {/* MOBILE SIDEBAR OVERLAY */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* SIDEBAR - Hidden on mobile, shown as drawer */}
      <div
        className={`
          fixed lg:static inset-y-0 left-0 z-50
          transform transition-transform duration-300 ease-in-out
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <LeftSidebar
          onStatusChange={setStatusFilter}
          onTagFilter={setTagFilter}
          onPriorityFilter={setPriorityFilter}
          onQuickView={setQuickView}
          onSortChange={(s, o) => {
            setSortBy(s)
            setSortOrder(o)
          }}
          selectedStatus={statusFilter}
          selectedTag={tagFilter}
          selectedPriority={priorityFilter}
          selectedView={quickView}
          availableTags={availableTags}
          onClose={() => setIsSidebarOpen(false)}
        />
      </div>

      {/* MAIN CONTENT */}
      <div
        className="
          flex-1 min-w-0 px-3 sm:px-4 md:ml-5 md:pr-2 space-y-3 sm:space-y-5 overflow-y-auto
          transition-all duration-500
          scrollbar-thin
          scrollbar-thumb-neon-blue/40
          scrollbar-track-transparent
          hover:scrollbar-thumb-neon-blue/70
        "
      >
        {/* HEADER WITH MOBILE MENU BUTTON */}
        <div className="flex items-center justify-between sticky top-0 bg-dark-bg/90 backdrop-blur-xl z-10 pb-3 sm:pb-5 pt-1">
          <div className="flex items-center gap-2 sm:gap-4 flex-1 min-w-0">
            {/* Mobile menu button */}
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg bg-dark-card/50 hover:bg-dark-card border border-dark-border text-gray-400 hover:text-white transition-colors"
              aria-label="Open menu"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            <div className="flex-1 min-w-0">
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white truncate">My Tasks</h1>
              <p className="text-xs sm:text-sm text-gray-400 hidden sm:block">Manage and organize your work</p>
            </div>
          </div>

          <Button
            onClick={() => setIsFormOpen(true)}
            className="ml-2 text-sm sm:text-base whitespace-nowrap"
          >
            <span className="hidden sm:inline">Add Task</span>
            <span className="sm:hidden">+</span>
          </Button>
        </div>

        <HeaderSummary
          totalCount={totalCount}
          completedCount={completedCount}
          pendingCount={pendingCount}
          onAddTask={() => setIsFormOpen(true)}
        />

        <SearchBar onSearch={setSearchQuery} />

        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : filteredAndSortedTasks.length === 0 ? (
          <EmptyState onCreateFirst={() => setIsFormOpen(true)} />
        ) : (
          <div className="space-y-3 sm:space-y-4 pb-16 sm:pb-10">
            {filteredAndSortedTasks.map(task => (
              <EnhancedTaskCard
                key={task.id}
                task={task}
                onToggleComplete={handleToggleComplete}
                onEdit={setEditingTask}
                onDelete={handleDeleteTask}
                isToggling={togglingTasks.has(task.id)}
              />
            ))}
          </div>
        )}
      </div>

      {/* AI CHAT PANEL */}
      <AIChatPanel isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />

      {/* FLOATING AI BUTTON - Enhanced with animations and effects */}
      {!isChatOpen && (
        <div className="fixed bottom-4 right-4 sm:bottom-8 sm:right-8 z-30">
          {/* Pulsing background glow */}
          <div className="absolute inset-0 rounded-full bg-neon-cyan/30 blur-2xl animate-pulse" />

          {/* Rotating ring */}
          <div className="absolute inset-0 rounded-full border-2 border-neon-cyan/50 animate-spin-slow"
               style={{ animation: 'spin 3s linear infinite' }} />

          {/* Main button */}
          <button
            onClick={() => setIsChatOpen(true)}
            className="relative w-14 h-14 sm:w-16 sm:h-16 rounded-full
              bg-gradient-to-br from-neon-cyan via-neon-blue to-purple-600
              shadow-[0_0_30px_rgba(34,211,238,0.6),0_0_60px_rgba(34,211,238,0.4),0_0_90px_rgba(34,211,238,0.2)]
              hover:shadow-[0_0_40px_rgba(34,211,238,0.8),0_0_80px_rgba(34,211,238,0.6),0_0_120px_rgba(34,211,238,0.4)]
              flex items-center justify-center text-white text-2xl
              transition-all duration-300 ease-out
              hover:scale-110 hover:rotate-12
              active:scale-95
              ring-4 ring-neon-cyan/20 hover:ring-neon-cyan/40
              group
              animate-bounce-subtle"
            aria-label="Open AI Chat"
          >
            {/* Sparkle effect */}
            <span className="absolute top-0 right-0 w-3 h-3 bg-white rounded-full opacity-0 group-hover:opacity-100 group-hover:animate-ping" />

            {/* Icon with hover animation */}
            <span className="relative transform group-hover:scale-110 transition-transform duration-300">
              🤖
            </span>

            {/* Tooltip */}
            <span className="absolute -top-12 left-1/2 -translate-x-1/2 px-3 py-1.5
              bg-gray-900 text-white text-xs rounded-lg whitespace-nowrap
              opacity-0 group-hover:opacity-100 transition-opacity duration-200
              pointer-events-none shadow-xl border border-neon-cyan/30">
              AI Assistant
              <span className="absolute top-full left-1/2 -translate-x-1/2 -mt-px
                border-4 border-transparent border-t-gray-900" />
            </span>
          </button>

          {/* Notification dot (optional - for new messages) */}
          <div className="absolute top-0 right-0 w-3 h-3 sm:w-4 sm:h-4 bg-red-500 rounded-full
            border-2 border-dark-bg shadow-lg animate-pulse hidden"
            id="chat-notification" />
        </div>
      )}

      <EnhancedTaskForm
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false)
          setEditingTask(null)
        }}
        onSubmit={handleFormSubmit}
        task={editingTask}
        mode={editingTask ? 'edit' : 'create'}
      />
    </div>
  )
}
