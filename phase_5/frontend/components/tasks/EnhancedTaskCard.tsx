'use client'

import { format } from 'date-fns'
import type { Task } from '@/types'
import { Button } from '@/components/ui/Button'

interface EnhancedTaskCardProps {
  task: Task
  onToggleComplete: (id: number) => void
  onEdit: (task: Task) => void
  onDelete: (id: number) => void
  isToggling?: boolean
}

const priorityConfig = {
  low: {
    strip: 'bg-gray-500',
    badge: 'bg-gray-500/20 text-gray-300',
    glow: 'hover:shadow-gray-500/20',
    label: 'Low',
    icon: '⬇️'
  },
  medium: {
    strip: 'bg-blue-500',
    badge: 'bg-blue-500/20 text-blue-300',
    glow: 'hover:shadow-blue-500/20',
    label: 'Medium',
    icon: '➡️'
  },
  high: {
    strip: 'bg-orange-500',
    badge: 'bg-orange-500/20 text-orange-300',
    glow: 'hover:shadow-orange-500/20',
    label: 'High',
    icon: '⬆️'
  },
  urgent: {
    strip: 'bg-red-500',
    badge: 'bg-red-500/20 text-red-300',
    glow: 'hover:shadow-red-500/20',
    label: 'Urgent',
    icon: '🔥'
  },
}

export function EnhancedTaskCard({
  task,
  onToggleComplete,
  onEdit,
  onDelete,
  isToggling = false,
}: EnhancedTaskCardProps) {
  const priority = priorityConfig[task.priority as keyof typeof priorityConfig] || priorityConfig.medium
  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'completed'
  const isCompleted = task.status === 'completed'

  return (
    <div
      className={`group relative bg-dark-card/40 backdrop-blur-xl rounded-xl overflow-hidden transition-all duration-300 hover:-translate-y-1 ${
        priority.glow
      } hover:shadow-xl ${isOverdue && !isCompleted ? 'ring-1 ring-red-500/30' : ''} ${
        isCompleted ? 'opacity-60' : ''
      }`}
    >
      {/* Priority Color Strip */}
      <div className={`absolute left-0 top-0 bottom-0 w-1 ${priority.strip}`} />

      <div className="flex items-start gap-2 sm:gap-3 md:gap-4 p-3 sm:p-4 md:p-5 pl-4 sm:pl-5 md:pl-6">
        {/* Completion Checkbox */}
        <button
          onClick={() => onToggleComplete(task.id)}
          disabled={isToggling}
          className={`mt-0.5 flex-shrink-0 w-5 h-5 sm:w-6 sm:h-6 rounded-lg flex items-center justify-center transition-all duration-300 ${
            isToggling
              ? 'bg-blue-500/50 cursor-wait'
              : isCompleted
              ? 'bg-green-500 shadow-md shadow-green-500/30 scale-100'
              : 'bg-white/5 hover:bg-white/10 hover:scale-110 ring-1 ring-white/20 cursor-pointer'
          }`}
          aria-label={isToggling ? 'Updating task...' : isCompleted ? 'Mark as incomplete' : 'Mark as complete'}
        >
          {isToggling ? (
            <svg className="w-3 h-3 sm:w-4 sm:h-4 text-white animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          ) : isCompleted ? (
            <svg className="w-3 h-3 sm:w-4 sm:h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          ) : null}
        </button>

        {/* Task Content */}
        <div className="flex-1 min-w-0 space-y-2 sm:space-y-3">
          {/* Title and Priority Badge */}
          <div className="flex items-start justify-between gap-2 sm:gap-3">
            <h3
              className={`text-sm sm:text-base font-semibold leading-tight flex-1 ${
                isCompleted ? 'line-through text-gray-500' : 'text-white'
              }`}
            >
              {task.title}
            </h3>
            <span
              className={`px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-lg text-xs font-medium flex items-center gap-1 sm:gap-1.5 flex-shrink-0 ${priority.badge}`}
            >
              <span className="text-xs sm:text-sm">{priority.icon}</span>
              <span className="hidden sm:inline">{priority.label}</span>
            </span>
          </div>

          {/* Description */}
          {task.description && (
            <p className="text-xs sm:text-sm text-gray-400 leading-relaxed line-clamp-2">{task.description}</p>
          )}

          {/* Metadata Row */}
          <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
            {/* Due Date */}
            {task.due_date && (
              <span
                className={`px-2.5 py-1 rounded-md text-xs font-medium flex items-center gap-1.5 ${
                  isOverdue && !isCompleted
                    ? 'bg-red-500/20 text-red-300 ring-1 ring-red-500/30'
                    : 'bg-white/5 text-gray-300'
                }`}
              >
                <span>🗓</span>
                <span>{format(new Date(task.due_date), 'MMM d, h:mm a')}</span>
              </span>
            )}

            {/* Recurring */}
            {task.recurrence && task.recurrence !== 'none' && (
              <span className="px-2.5 py-1 rounded-md bg-purple-500/20 text-purple-300 text-xs font-medium flex items-center gap-1.5">
                <span>🔄</span>
                <span className="capitalize">{task.recurrence}</span>
              </span>
            )}

            {/* Reminder */}
            {task.remind_at && !task.reminder_sent && (
              <span className="px-2.5 py-1 rounded-md bg-amber-500/20 text-amber-300 text-xs font-medium flex items-center gap-1.5">
                <span>🔔</span>
                <span>{format(new Date(task.remind_at), 'MMM d, h:mm a')}</span>
              </span>
            )}
            {task.reminder_sent && (
              <span className="px-2.5 py-1 rounded-md bg-green-500/20 text-green-300 text-xs font-medium flex items-center gap-1.5">
                <span>✅</span>
                <span>Reminded</span>
              </span>
            )}

            {/* Tags */}
            {task.tags && task.tags.length > 0 && (
              <>
                {task.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-2.5 py-1 rounded-md bg-indigo-500/20 text-indigo-300 text-xs font-medium flex items-center gap-1.5"
                  >
                    <span>🏷</span>
                    <span>{tag}</span>
                  </span>
                ))}
              </>
            )}

            {/* Status (if in_progress) */}
            {task.status === 'in_progress' && (
              <span className="px-2.5 py-1 rounded-md bg-yellow-500/20 text-yellow-300 text-xs font-medium flex items-center gap-1.5">
                <span>🔄</span>
                <span>In Progress</span>
              </span>
            )}
          </div>
        </div>

        {/* Actions - Always visible on mobile, slightly visible on desktop, fully visible on hover */}
        <div className="flex-shrink-0 flex gap-0.5 sm:gap-1 opacity-100 sm:opacity-30 sm:group-hover:opacity-100 transition-opacity duration-200">
          <button
            onClick={() => onEdit(task)}
            className="p-1.5 sm:p-2 text-gray-400 hover:text-neon-blue hover:bg-neon-blue/10 rounded-lg transition-all"
            title="Edit task"
            aria-label="Edit task"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
          </button>
          <button
            onClick={() => {
              if (confirm('Are you sure you want to delete this task?')) {
                onDelete(task.id)
              }
            }}
            className="p-1.5 sm:p-2 text-gray-400 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-all"
            title="Delete task"
            aria-label="Delete task"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
