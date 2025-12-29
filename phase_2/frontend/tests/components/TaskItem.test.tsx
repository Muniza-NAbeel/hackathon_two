import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { TaskItem } from '@/components/tasks/TaskItem'
import type { Task } from '@/types'

const mockTask: Task = {
  id: '123',
  user_id: '456',
  title: 'Test Task',
  description: 'Test description',
  completed: false,
  due_date: null,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}

describe('TaskItem', () => {
  const mockOnToggleComplete = vi.fn()
  const mockOnEdit = vi.fn()
  const mockOnDelete = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders task title and description', () => {
    render(
      <TaskItem
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    )

    expect(screen.getByText('Test Task')).toBeInTheDocument()
    expect(screen.getByText('Test description')).toBeInTheDocument()
  })

  it('shows checkbox as unchecked for incomplete task', () => {
    render(
      <TaskItem
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    )

    const checkbox = screen.getByRole('button', { name: /mark as complete/i })
    expect(checkbox).toBeInTheDocument()
  })

  it('shows checkbox as checked for completed task', () => {
    const completedTask = { ...mockTask, completed: true }
    render(
      <TaskItem
        task={completedTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    )

    const checkbox = screen.getByRole('button', { name: /mark as incomplete/i })
    expect(checkbox).toBeInTheDocument()
  })

  it('calls onToggleComplete when checkbox clicked', async () => {
    mockOnToggleComplete.mockResolvedValue(undefined)

    render(
      <TaskItem
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    )

    const checkbox = screen.getByRole('button', { name: /mark as complete/i })
    fireEvent.click(checkbox)

    await waitFor(() => {
      expect(mockOnToggleComplete).toHaveBeenCalledWith('123')
    })
  })

  it('calls onEdit when edit button clicked', () => {
    render(
      <TaskItem
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    )

    const editButton = screen.getByRole('button', { name: /edit task/i })
    fireEvent.click(editButton)

    expect(mockOnEdit).toHaveBeenCalledWith(mockTask)
  })

  it('shows delete confirmation when delete button clicked', async () => {
    render(
      <TaskItem
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    )

    const deleteButton = screen.getByRole('button', { name: /delete task/i })
    fireEvent.click(deleteButton)

    await waitFor(() => {
      expect(screen.getByText(/are you sure/i)).toBeInTheDocument()
    })
  })

  it('applies line-through style to completed task title', () => {
    const completedTask = { ...mockTask, completed: true }
    render(
      <TaskItem
        task={completedTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    )

    const title = screen.getByText('Test Task')
    expect(title).toHaveClass('line-through')
  })
})
