import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { TaskForm } from '@/components/tasks/TaskForm'
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

describe('TaskForm', () => {
  const mockOnClose = vi.fn()
  const mockOnSubmit = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders create form with empty fields', () => {
    render(
      <TaskForm
        isOpen={true}
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
        task={null}
        mode="create"
      />
    )

    expect(screen.getByText('Create Task')).toBeInTheDocument()
    expect(screen.getByLabelText(/title/i)).toHaveValue('')
  })

  it('renders edit form with task data', () => {
    render(
      <TaskForm
        isOpen={true}
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
        task={mockTask}
        mode="edit"
      />
    )

    expect(screen.getByText('Edit Task')).toBeInTheDocument()
    expect(screen.getByLabelText(/title/i)).toHaveValue('Test Task')
  })

  it('shows validation error for empty title', async () => {
    render(
      <TaskForm
        isOpen={true}
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
        task={null}
        mode="create"
      />
    )

    const submitButton = screen.getByRole('button', { name: /create/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument()
    })
  })

  it('shows validation error for title exceeding 200 characters', async () => {
    render(
      <TaskForm
        isOpen={true}
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
        task={null}
        mode="create"
      />
    )

    const titleInput = screen.getByLabelText(/title/i)
    fireEvent.change(titleInput, { target: { value: 'A'.repeat(201) } })

    const submitButton = screen.getByRole('button', { name: /create/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(
        screen.getByText(/title must be 200 characters or less/i)
      ).toBeInTheDocument()
    })
  })

  it('calls onClose when cancel button clicked', () => {
    render(
      <TaskForm
        isOpen={true}
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
        task={null}
        mode="create"
      />
    )

    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    fireEvent.click(cancelButton)

    expect(mockOnClose).toHaveBeenCalled()
  })

  it('calls onSubmit with form data on valid submit', async () => {
    mockOnSubmit.mockResolvedValue(undefined)

    render(
      <TaskForm
        isOpen={true}
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
        task={null}
        mode="create"
      />
    )

    const titleInput = screen.getByLabelText(/title/i)
    fireEvent.change(titleInput, { target: { value: 'New Task' } })

    const submitButton = screen.getByRole('button', { name: /create/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'New Task',
        })
      )
    })
  })

  it('does not render when isOpen is false', () => {
    render(
      <TaskForm
        isOpen={false}
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
        task={null}
        mode="create"
      />
    )

    expect(screen.queryByText('Create Task')).not.toBeInTheDocument()
  })
})
