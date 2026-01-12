'use client'

import { useState } from 'react'
import type { TaskStatus, TaskSortBy, SortOrder } from '@/types'

interface LeftSidebarProps {
  onStatusChange: (status: TaskStatus) => void
  onTagFilter: (tag: string | null) => void
  onQuickView: (view: 'today' | 'week' | 'overdue' | 'all') => void
  onSortChange: (sortBy: TaskSortBy, order: SortOrder) => void
  onPriorityFilter: (priority: string | null) => void
  selectedStatus: TaskStatus
  selectedTag: string | null
  selectedView: string
  selectedPriority: string | null
  availableTags: string[]
  onClose?: () => void
}

export function LeftSidebar({
  onStatusChange,
  onTagFilter,
  onQuickView,
  onSortChange,
  onPriorityFilter,
  selectedStatus,
  selectedTag,
  selectedView,
  selectedPriority,
  availableTags,
  onClose,
}: LeftSidebarProps) {
  const [sortBy, setSortBy] = useState<TaskSortBy>('due_date')
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc')

  const handleSortChange = (newSortBy: TaskSortBy) => {
    const newOrder = sortBy === newSortBy && sortOrder === 'asc' ? 'desc' : 'asc'
    setSortBy(newSortBy)
    setSortOrder(newOrder)
    onSortChange(newSortBy, newOrder)
  }

  return (
    <div className="w-64 sm:w-56 lg:w-48 bg-gradient-to-b from-dark-card/30 to-dark-card/10 backdrop-blur-xl p-3 space-y-5 h-full overflow-y-auto scrollbar-thin">
      {/* Mobile Close Button */}
      {onClose && (
        <div className="lg:hidden flex justify-between items-center mb-3 pb-3 border-b border-dark-border">
          <h2 className="text-sm font-semibold text-white">Filters & Sort</h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
            aria-label="Close menu"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Status Filters */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2 px-2">
          Status
        </h3>
        <div className="space-y-1">
          {[
            { value: 'all', label: 'All', icon: '📋' },
            { value: 'pending', label: 'Pending', icon: '⏳' },
            { value: 'in_progress', label: 'Progress', icon: '🔄' },
            { value: 'completed', label: 'Done', icon: '✅' },
          ].map((status) => (
            <button
              key={status.value}
              onClick={() => onStatusChange(status.value as TaskStatus)}
              className={`w-full text-left px-2.5 py-1.5 rounded-md transition-all duration-200 flex items-center gap-2 group ${
                selectedStatus === status.value
                  ? 'bg-neon-blue/20 text-neon-blue shadow-sm shadow-neon-blue/20'
                  : 'text-gray-400 hover:bg-white/5 hover:text-white'
              }`}
            >
              <span className="text-base">{status.icon}</span>
              <span className="text-xs font-medium">{status.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Priority Filter */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2 px-2">
          Priority
        </h3>
        <div className="space-y-1">
          {[
            { value: null, label: 'All', icon: '🎯' },
            { value: 'low', label: 'Low', icon: '⬇️' },
            { value: 'medium', label: 'Medium', icon: '➡️' },
            { value: 'high', label: 'High', icon: '⬆️' },
            { value: 'urgent', label: 'Urgent', icon: '🔥' },
          ].map((priority) => (
            <button
              key={priority.value ?? 'all'}
              onClick={() => onPriorityFilter(priority.value)}
              className={`w-full text-left px-2.5 py-1.5 rounded-md transition-all duration-200 flex items-center gap-2 group ${
                selectedPriority === priority.value
                  ? 'bg-neon-blue/20 text-neon-blue shadow-sm shadow-neon-blue/20'
                  : 'text-gray-400 hover:bg-white/5 hover:text-white'
              }`}
            >
              <span className="text-base">{priority.icon}</span>
              <span className="text-xs font-medium">{priority.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Tags */}
      {availableTags.length > 0 && (
        <div>
          <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2 px-2">
            Tags
          </h3>
          <div className="space-y-1">
            <button
              onClick={() => onTagFilter(null)}
              className={`w-full text-left px-2.5 py-1.5 rounded-md transition-all duration-200 flex items-center gap-2 ${
                selectedTag === null
                  ? 'bg-neon-blue/20 text-neon-blue shadow-sm shadow-neon-blue/20'
                  : 'text-gray-400 hover:bg-white/5 hover:text-white'
              }`}
            >
              <span className="text-base">🏷️</span>
              <span className="text-xs font-medium">All</span>
            </button>
            {availableTags.slice(0, 5).map((tag) => (
              <button
                key={tag}
                onClick={() => onTagFilter(tag)}
                className={`w-full text-left px-2.5 py-1.5 rounded-md transition-all duration-200 flex items-center gap-2 truncate ${
                  selectedTag === tag
                    ? 'bg-neon-blue/20 text-neon-blue shadow-sm shadow-neon-blue/20'
                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                }`}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-current flex-shrink-0"></span>
                <span className="text-xs font-medium truncate">{tag}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Quick Views */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2 px-2">
          Views
        </h3>
        <div className="space-y-1">
          {[
            { value: 'today', label: 'Today', icon: '📅' },
            { value: 'week', label: 'Week', icon: '📆' },
            { value: 'overdue', label: 'Overdue', icon: '⏰' },
            { value: 'all', label: 'All', icon: '🌐' },
          ].map((view) => (
            <button
              key={view.value}
              onClick={() => onQuickView(view.value as any)}
              className={`w-full text-left px-2.5 py-1.5 rounded-md transition-all duration-200 flex items-center gap-2 ${
                selectedView === view.value
                  ? 'bg-neon-blue/20 text-neon-blue shadow-sm shadow-neon-blue/20'
                  : 'text-gray-400 hover:bg-white/5 hover:text-white'
              }`}
            >
              <span className="text-base">{view.icon}</span>
              <span className="text-xs font-medium">{view.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Sort By */}
      <div>
        <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2 px-2">
          Sort
        </h3>
        <div className="space-y-1">
          {[
            { value: 'due_date', label: 'Due', icon: '📅' },
            { value: 'priority', label: 'Priority', icon: '⚡' },
            { value: 'title', label: 'A–Z', icon: '🔤' },
            { value: 'created_at', label: 'Recent', icon: '🕐' },
          ].map((sort) => (
            <button
              key={sort.value}
              onClick={() => handleSortChange(sort.value as TaskSortBy)}
              className={`w-full text-left px-2.5 py-1.5 rounded-md transition-all duration-200 flex items-center justify-between ${
                sortBy === sort.value
                  ? 'bg-neon-blue/20 text-neon-blue shadow-sm shadow-neon-blue/20'
                  : 'text-gray-400 hover:bg-white/5 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-2">
                <span className="text-base">{sort.icon}</span>
                <span className="text-xs font-medium">{sort.label}</span>
              </div>
              {sortBy === sort.value && (
                <span className="text-xs opacity-70">
                  {sortOrder === 'asc' ? '↑' : '↓'}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
