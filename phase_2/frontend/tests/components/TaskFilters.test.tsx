import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { TaskFilters } from '@/components/tasks/TaskFilters'

describe('TaskFilters', () => {
  const mockOnStatusChange = vi.fn()
  const mockOnSortByChange = vi.fn()
  const mockOnSortOrderChange = vi.fn()

  it('renders all filter dropdowns', () => {
    render(
      <TaskFilters
        status="all"
        sortBy="created_at"
        sortOrder="desc"
        onStatusChange={mockOnStatusChange}
        onSortByChange={mockOnSortByChange}
        onSortOrderChange={mockOnSortOrderChange}
      />
    )

    expect(screen.getByLabelText(/status/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/sort by/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/order/i)).toBeInTheDocument()
  })

  it('shows correct initial values', () => {
    render(
      <TaskFilters
        status="pending"
        sortBy="title"
        sortOrder="asc"
        onStatusChange={mockOnStatusChange}
        onSortByChange={mockOnSortByChange}
        onSortOrderChange={mockOnSortOrderChange}
      />
    )

    expect(screen.getByLabelText(/status/i)).toHaveValue('pending')
    expect(screen.getByLabelText(/sort by/i)).toHaveValue('title')
    expect(screen.getByLabelText(/order/i)).toHaveValue('asc')
  })

  it('calls onStatusChange when status filter changed', () => {
    render(
      <TaskFilters
        status="all"
        sortBy="created_at"
        sortOrder="desc"
        onStatusChange={mockOnStatusChange}
        onSortByChange={mockOnSortByChange}
        onSortOrderChange={mockOnSortOrderChange}
      />
    )

    const statusSelect = screen.getByLabelText(/status/i)
    fireEvent.change(statusSelect, { target: { value: 'completed' } })

    expect(mockOnStatusChange).toHaveBeenCalledWith('completed')
  })

  it('calls onSortByChange when sort by changed', () => {
    render(
      <TaskFilters
        status="all"
        sortBy="created_at"
        sortOrder="desc"
        onStatusChange={mockOnStatusChange}
        onSortByChange={mockOnSortByChange}
        onSortOrderChange={mockOnSortOrderChange}
      />
    )

    const sortBySelect = screen.getByLabelText(/sort by/i)
    fireEvent.change(sortBySelect, { target: { value: 'due_date' } })

    expect(mockOnSortByChange).toHaveBeenCalledWith('due_date')
  })

  it('calls onSortOrderChange when sort order changed', () => {
    render(
      <TaskFilters
        status="all"
        sortBy="created_at"
        sortOrder="desc"
        onStatusChange={mockOnStatusChange}
        onSortByChange={mockOnSortByChange}
        onSortOrderChange={mockOnSortOrderChange}
      />
    )

    const orderSelect = screen.getByLabelText(/order/i)
    fireEvent.change(orderSelect, { target: { value: 'asc' } })

    expect(mockOnSortOrderChange).toHaveBeenCalledWith('asc')
  })

  it('has all expected status options', () => {
    render(
      <TaskFilters
        status="all"
        sortBy="created_at"
        sortOrder="desc"
        onStatusChange={mockOnStatusChange}
        onSortByChange={mockOnSortByChange}
        onSortOrderChange={mockOnSortOrderChange}
      />
    )

    const statusSelect = screen.getByLabelText(/status/i)
    expect(statusSelect).toContainHTML('All tasks')
    expect(statusSelect).toContainHTML('Pending')
    expect(statusSelect).toContainHTML('Completed')
  })

  it('has all expected sort by options', () => {
    render(
      <TaskFilters
        status="all"
        sortBy="created_at"
        sortOrder="desc"
        onStatusChange={mockOnStatusChange}
        onSortByChange={mockOnSortByChange}
        onSortOrderChange={mockOnSortOrderChange}
      />
    )

    const sortBySelect = screen.getByLabelText(/sort by/i)
    expect(sortBySelect).toContainHTML('Created date')
    expect(sortBySelect).toContainHTML('Title')
    expect(sortBySelect).toContainHTML('Due date')
  })
})
