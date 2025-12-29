'use client'

import { TaskItem } from './TaskItem'
import { EmptyState } from './EmptyState'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import type { Task } from '@/types'

interface TaskListProps {
  tasks: Task[]
  loading: boolean
  onToggleComplete: (taskId: string) => Promise<void>
  onEdit: (task: Task) => void
  onDelete: (taskId: string) => Promise<void>
  onCreateFirst: () => void
}

export function TaskList({
  tasks,
  loading,
  onToggleComplete,
  onEdit,
  onDelete,
  onCreateFirst,
}: TaskListProps) {
  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (tasks.length === 0) {
    return <EmptyState onCreateFirst={onCreateFirst} />
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onToggleComplete={onToggleComplete}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  )
}
