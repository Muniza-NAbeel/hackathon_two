'use client'

import { Button } from '@/components/ui/Button'

interface EmptyStateProps {
  onCreateFirst: () => void
}

export function EmptyState({ onCreateFirst }: EmptyStateProps) {
  return (
    <div className="text-center py-16 bg-dark-card/30 backdrop-blur-xl rounded-lg border border-dark-border">
      <div className="max-w-md mx-auto px-6">
        <div className="w-20 h-20 mx-auto bg-neon-purple/10 rounded-full flex items-center justify-center ring-2 ring-neon-purple/30">
          <svg
            className="h-10 w-10 text-neon-purple"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
            />
          </svg>
        </div>
        <h3 className="mt-6 text-xl font-semibold text-white">No tasks yet</h3>
        <p className="mt-3 text-gray-400">
          Get started by creating your first task and stay organized.
        </p>
        <div className="mt-8">
          <Button onClick={onCreateFirst}>
            <svg
              className="-ml-1 mr-2 h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Create Your First Task
          </Button>
        </div>
      </div>
    </div>
  )
}
