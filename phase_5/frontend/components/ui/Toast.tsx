'use client'

import { useEffect, useState } from 'react'

export interface ToastData {
  id: string
  type: 'info' | 'success' | 'warning' | 'error' | 'reminder'
  title: string
  message: string
  duration?: number // ms, 0 for persistent
}

interface ToastProps {
  toast: ToastData
  onDismiss: (id: string) => void
}

const toastConfig = {
  info: {
    bg: 'bg-blue-500/90',
    border: 'border-blue-400',
    icon: 'ℹ️',
  },
  success: {
    bg: 'bg-green-500/90',
    border: 'border-green-400',
    icon: '✅',
  },
  warning: {
    bg: 'bg-amber-500/90',
    border: 'border-amber-400',
    icon: '⚠️',
  },
  error: {
    bg: 'bg-red-500/90',
    border: 'border-red-400',
    icon: '❌',
  },
  reminder: {
    bg: 'bg-purple-500/90',
    border: 'border-purple-400',
    icon: '🔔',
  },
}

export function Toast({ toast, onDismiss }: ToastProps) {
  const [isExiting, setIsExiting] = useState(false)
  const config = toastConfig[toast.type]

  useEffect(() => {
    if (toast.duration && toast.duration > 0) {
      const timer = setTimeout(() => {
        setIsExiting(true)
        setTimeout(() => onDismiss(toast.id), 300)
      }, toast.duration)

      return () => clearTimeout(timer)
    }
  }, [toast.duration, toast.id, onDismiss])

  const handleDismiss = () => {
    setIsExiting(true)
    setTimeout(() => onDismiss(toast.id), 300)
  }

  return (
    <div
      className={`
        ${config.bg} ${config.border}
        border backdrop-blur-xl rounded-xl shadow-2xl
        p-4 min-w-[320px] max-w-[420px]
        transform transition-all duration-300 ease-out
        ${isExiting ? 'translate-x-full opacity-0' : 'translate-x-0 opacity-100'}
        animate-slide-in
      `}
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl flex-shrink-0">{config.icon}</span>
        <div className="flex-1 min-w-0">
          <h4 className="text-white font-semibold text-sm">{toast.title}</h4>
          <p className="text-white/80 text-xs mt-1 leading-relaxed">{toast.message}</p>
        </div>
        <button
          onClick={handleDismiss}
          className="text-white/60 hover:text-white transition-colors p-1 -m-1"
          aria-label="Dismiss notification"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  )
}

interface ToastContainerProps {
  toasts: ToastData[]
  onDismiss: (id: string) => void
}

export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-3">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  )
}
