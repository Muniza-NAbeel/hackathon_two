'use client'

interface HeaderSummaryProps {
  totalCount: number
  completedCount: number
  pendingCount: number
  onAddTask: () => void
}

export function HeaderSummary({
  totalCount,
  completedCount,
  pendingCount,
}: HeaderSummaryProps) {
  return (
    <div className="bg-dark-card/50 backdrop-blur-xl border border-dark-border rounded-lg p-3 sm:p-4">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-neon-blue/20 rounded-lg flex items-center justify-center ring-2 ring-neon-blue/30">
            <svg className="w-6 h-6 text-neon-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs sm:text-sm text-gray-400">Total Tasks</p>
            <p className="text-xl sm:text-2xl font-bold text-white">{totalCount}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center ring-2 ring-green-500/30">
            <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs sm:text-sm text-gray-400">Completed</p>
            <p className="text-xl sm:text-2xl font-bold text-green-400">{completedCount}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center ring-2 ring-yellow-500/30">
            <svg className="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs sm:text-sm text-gray-400">Pending</p>
            <p className="text-xl sm:text-2xl font-bold text-yellow-400">{pendingCount}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
