'use client'

import { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react'
import { ToastData } from '@/components/ui/Toast'
import { getAuthToken } from '@/lib/utils/storage'

interface NotificationContextType {
  addNotification: (notification: Omit<ToastData, 'id'>) => void
  removeNotification: (id: string) => void
  showReminder: (taskTitle: string, dueDate: string) => void
  showSuccess: (title: string, message: string) => void
  showError: (title: string, message: string) => void
  showInfo: (title: string, message: string) => void
  bellNotifications: ToastData[]
}

const NotificationContext = createContext<NotificationContextType | null>(null)

export function useNotifications() {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider')
  }
  return context
}

interface NotificationProviderProps {
  children: React.ReactNode
}

export function NotificationProvider({ children }: NotificationProviderProps) {
  // State for managing notifications for the bell icon
  const [bellNotifications, setBellNotifications] = useState<ToastData[]>([])
  const shownRemindersRef = useRef<Set<string>>(new Set())
  const pollingRef = useRef<NodeJS.Timeout | null>(null)

  const addNotification = useCallback((notification: Omit<ToastData, 'id'>) => {
    const id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    setBellNotifications((prev) => [...prev, { ...notification, id }])
  }, [])

  const removeNotification = useCallback((id: string) => {
    setBellNotifications((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const showReminder = useCallback((taskTitle: string, dueDate: string) => {
    const dueTime = new Date(dueDate)
    const now = new Date()
    const diffMs = dueTime.getTime() - now.getTime()
    const diffMins = Math.round(diffMs / 60000)

    let timeText = ''
    if (diffMins <= 0) {
      timeText = 'now!'
    } else if (diffMins < 60) {
      timeText = `in ${diffMins} minute${diffMins !== 1 ? 's' : ''}`
    } else {
      const hours = Math.floor(diffMins / 60)
      timeText = `in ${hours} hour${hours !== 1 ? 's' : ''}`
    }

    addNotification({
      type: 'reminder',
      title: '🔔 Task Reminder',
      message: `"${taskTitle}" is due ${timeText}`,
      duration: 10000, // 10 seconds
    })
  }, [addNotification])

  const showSuccess = useCallback((title: string, message: string) => {
    addNotification({ type: 'success', title, message, duration: 5000 })
  }, [addNotification])

  const showError = useCallback((title: string, message: string) => {
    addNotification({ type: 'error', title, message, duration: 8000 })
  }, [addNotification])

  const showInfo = useCallback((title: string, message: string) => {
    addNotification({ type: 'info', title, message, duration: 5000 })
  }, [addNotification])

  // Poll for reminders and recurring task notifications
  useEffect(() => {
    const checkNotifications = async () => {
      const token = getAuthToken()
      if (!token) return

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

        // Fetch recent notifications from the backend
        const response = await fetch(`${apiUrl}/api/notifications`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        if (response.ok) {
          const data = await response.json()

          // Process notifications and show relevant ones
          for (const notification of data.notifications || []) {
            if (!notification.read) {
              const notificationKey = `notif-${notification.id}`

              // Show notification if not already shown
              if (!shownRemindersRef.current.has(notificationKey)) {
                shownRemindersRef.current.add(notificationKey)

                // Show different types of notifications based on their type
                switch(notification.type) {
                  case 'reminder':
                    showReminder(notification.title, notification.message)
                    break
                  case 'success':
                    showSuccess(notification.title, notification.message)
                    break
                  case 'error':
                    showError(notification.title, notification.message)
                    break
                  case 'info':
                  default:
                    showInfo(notification.title, notification.message)
                    break
                }
              }
            }
          }
        }

        // Also check for tasks with reminders (fallback)
        const tasksResponse = await fetch(`${apiUrl}/api/tasks?status=pending&status=in_progress`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        if (tasksResponse.ok) {
          const tasksData = await tasksResponse.json()
          const now = new Date()
          const fiveMinutesFromNow = new Date(now.getTime() + 5 * 60 * 1000)

          // Check for tasks with reminders due in the next 5 minutes
          for (const task of tasksData.tasks || []) {
            if (task.remind_at && !task.reminder_sent) {
              const remindAt = new Date(task.remind_at)
              const reminderKey = `${task.id}-${task.remind_at}`

              // If reminder is due (past or within next minute) and not shown yet
              if (remindAt <= fiveMinutesFromNow && !shownRemindersRef.current.has(reminderKey)) {
                shownRemindersRef.current.add(reminderKey)
                showReminder(task.title, task.due_date || task.remind_at)
              }
            }
          }
        }
      } catch (error) {
        console.error('Error checking notifications:', error)
      }
    }

    // Initial check
    checkNotifications()

    // Poll every 30 seconds
    pollingRef.current = setInterval(checkNotifications, 30000)

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
      }
    }
  }, [showReminder, showSuccess, showError, showInfo])

  return (
    <NotificationContext.Provider
      value={{
        addNotification,
        removeNotification,
        showReminder,
        showSuccess,
        showError,
        showInfo,
        bellNotifications,
      }}
    >
      {children}
    </NotificationContext.Provider>
  )
}
