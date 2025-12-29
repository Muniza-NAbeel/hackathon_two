import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { SignupForm } from '@/components/auth/SignupForm'

// Mock the API module
vi.mock('@/lib/api', () => ({
  register: vi.fn(),
  ApiError: class ApiError extends Error {
    constructor(
      public status: number,
      public code: string,
      message: string,
      public field?: string
    ) {
      super(message)
    }
  },
}))

// Mock auth utilities
vi.mock('@/lib/auth', () => ({
  storeAuthData: vi.fn(),
}))

describe('SignupForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders signup form with all required fields', () => {
    render(<SignupForm />)

    expect(screen.getByLabelText(/name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^email$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /create account/i })
    ).toBeInTheDocument()
  })

  it('shows validation error for empty email', async () => {
    render(<SignupForm />)

    const submitButton = screen.getByRole('button', { name: /create account/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument()
    })
  })

  it('shows validation error for short password', async () => {
    render(<SignupForm />)

    const emailInput = screen.getByLabelText(/^email$/i)
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })

    const passwordInput = screen.getByLabelText(/^password$/i)
    fireEvent.change(passwordInput, { target: { value: 'short' } })

    const confirmInput = screen.getByLabelText(/confirm password/i)
    fireEvent.change(confirmInput, { target: { value: 'short' } })

    const submitButton = screen.getByRole('button', { name: /create account/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(
        screen.getByText(/password must be at least 8 characters/i)
      ).toBeInTheDocument()
    })
  })

  it('shows validation error for mismatched passwords', async () => {
    render(<SignupForm />)

    const emailInput = screen.getByLabelText(/^email$/i)
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })

    const passwordInput = screen.getByLabelText(/^password$/i)
    fireEvent.change(passwordInput, { target: { value: 'password123' } })

    const confirmInput = screen.getByLabelText(/confirm password/i)
    fireEvent.change(confirmInput, { target: { value: 'different123' } })

    const submitButton = screen.getByRole('button', { name: /create account/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument()
    })
  })

  it('has link to login page', () => {
    render(<SignupForm />)

    const loginLink = screen.getByRole('link', { name: /sign in/i })
    expect(loginLink).toHaveAttribute('href', '/login')
  })
})
