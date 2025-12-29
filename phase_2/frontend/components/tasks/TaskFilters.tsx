'use client'

import type { TaskStatus, TaskSortBy, SortOrder } from '@/types'

interface TaskFiltersProps {
  status: TaskStatus
  sortBy: TaskSortBy
  sortOrder: SortOrder
  onStatusChange: (status: TaskStatus) => void
  onSortByChange: (sortBy: TaskSortBy) => void
  onSortOrderChange: (sortOrder: SortOrder) => void
}

export function TaskFilters({
  status,
  sortBy,
  sortOrder,
  onStatusChange,
  onSortByChange,
  onSortOrderChange,
}: TaskFiltersProps) {
  return (
    <div className="flex flex-wrap gap-4">
      {/* Status filter */}
      <div className="flex-1 min-w-[150px]">
        <label
          htmlFor="status-filter"
          className="block text-sm font-medium text-gray-300 mb-2"
        >
          Status
        </label>
        <select
          id="status-filter"
          value={status}
          onChange={(e) => onStatusChange(e.target.value as TaskStatus)}
          className="w-full px-4 py-2.5 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-neon-blue focus:border-transparent hover:border-neon-blue/50 transition-all"
        >
          <option value="all">All tasks</option>
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      {/* Sort by */}
      <div className="flex-1 min-w-[150px]">
        <label
          htmlFor="sort-by"
          className="block text-sm font-medium text-gray-300 mb-2"
        >
          Sort by
        </label>
        <select
          id="sort-by"
          value={sortBy}
          onChange={(e) => onSortByChange(e.target.value as TaskSortBy)}
          className="w-full px-4 py-2.5 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-neon-blue focus:border-transparent hover:border-neon-blue/50 transition-all"
        >
          <option value="created_at">Created date</option>
          <option value="title">Title</option>
          <option value="due_date">Due date</option>
        </select>
      </div>

      {/* Sort order */}
      <div className="flex-1 min-w-[150px]">
        <label
          htmlFor="sort-order"
          className="block text-sm font-medium text-gray-300 mb-2"
        >
          Order
        </label>
        <select
          id="sort-order"
          value={sortOrder}
          onChange={(e) => onSortOrderChange(e.target.value as SortOrder)}
          className="w-full px-4 py-2.5 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-neon-blue focus:border-transparent hover:border-neon-blue/50 transition-all"
        >
          <option value="desc">Newest first</option>
          <option value="asc">Oldest first</option>
        </select>
      </div>
    </div>
  )
}
