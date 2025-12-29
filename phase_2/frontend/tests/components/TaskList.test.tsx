import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { TaskList } from '@/components/tasks/TaskList'
import type { Task } from '@/types'

const mockTasks: Task[] = [
  {
    id: '1',
    user_id: '456',
    title: 'Task 1',
    description: 'Description 1',
    completed: false,
    due_date: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '2',
    user_id: '456',
    title: 'Task 2',
    description: null,
    completed: true,
    due_date: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

describe('TaskList', () => {
  const mockOnToggleComplete = vi.fn()
  const mockOnEdit = vi.fn()
  const mockOnDelete = vi.fn()
  const mockOnCreateFirst = vi.fn()

  it('shows loading spinner when loading', () => {
    render(
      <TaskList
        tasks={[]}
        loading={true}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onCreateFirst={mockOnCreateFirst}
      />
    )

    expect(screen.getByRole('status', { name: /loading/i })).toBeInTheDocument()
  })

  it('shows empty state when no tasks', () => {
    render(
      <TaskList
        tasks={[]}
        loading={false}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onCreateFirst={mockOnCreateFirst}
      />
    )

    expect(screen.getByText(/no tasks yet/i)).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /create task/i })
    ).toBeInTheDocument()
  })

  it('renders list of tasks', () => {
    render(
      <TaskList
        tasks={mockTasks}
        loading={false}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onCreateFirst={mockOnCreateFirst}
      />
    )

    expect(screen.getByText('Task 1')).toBeInTheDocument()
    expect(screen.getByText('Task 2')).toBeInTheDocument()
  })

  it('renders correct number of task items', () => {
    render(
      <TaskList
        tasks={mockTasks}
        loading={false}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onCreateFirst={mockOnCreateFirst}
      />
    )

    const editButtons = screen.getAllByRole('button', { name: /edit task/i })
    expect(editButtons).toHaveLength(2)
  })
})
