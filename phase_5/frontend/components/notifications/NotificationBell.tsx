'use client'

import { useState, useEffect, useRef } from 'react'
import { Bell, X } from 'lucide-react'
import { useNotifications } from './NotificationProvider'
import { getAuthToken } from '@/lib/utils/storage'
import { ToastData } from '@/components/ui/Toast'

interface Notification {
  id: string
  title: string
  message: string
  type: 'info' | 'success' | 'error' | 'reminder' | 'recurring'
  timestamp: Date
  read: boolean
}

export default function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false)
  const [backendNotifications, setBackendNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const bellRef = useRef<HTMLDivElement>(null)

  const { showSuccess, showError, addNotification, bellNotifications, removeNotification } = useNotifications()

  // Fetch notifications from backend
  const fetchNotifications = async () => {
    const token = getAuthToken()
    if (!token) {
      setLoading(false)
      return
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/notifications`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      // Convert received data to our Notification format
      const fetchedNotifications = (data.notifications || []).map((item: any) => ({
        id: item.id || `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        title: item.title || 'Notification',
        message: item.message || item.description || 'You have a new notification',
        type: item.type || 'info',
        timestamp: new Date(item.timestamp || item.created_at || Date.now()),
        read: item.read || false,
      }))

      setBackendNotifications(fetchedNotifications)
    } catch (error) {
      console.error('Error fetching notifications:', error)
      // Show error notification
      showError('Error', 'Could not load notifications')
    } finally {
      setLoading(false)
    }
  }

  // Combine backend notifications with context notifications
  const allNotifications = [...backendNotifications, ...bellNotifications.map((toast: any) => ({
    id: toast.id,
    title: toast.title,
    message: toast.message,
    type: toast.type,
    timestamp: new Date(),
    read: false
  }))]

  // Calculate unread count for all notifications
  const totalUnreadCount = allNotifications.filter(n => !n.read).length

  // Fetch notifications when component mounts and refresh periodically
  useEffect(() => {
    // Initially fetch notifications
    setLoading(true)
    fetchNotifications()

    // Refresh notifications every 30 seconds
    const interval = setInterval(fetchNotifications, 30000)

    return () => clearInterval(interval)
  }, [])

  // Toggle dropdown visibility
  const toggleDropdown = () => {
    setIsOpen(!isOpen)
    if (!isOpen) {
      // Mark backend notifications as read when opening the dropdown
      setBackendNotifications(prev =>
        prev.map(n => ({ ...n, read: true }))
      )
    }
  }

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (bellRef.current && !bellRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  // Format time ago
  const formatTimeAgo = (date: Date) => {
    const now = new Date()
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (diffInSeconds < 60) return 'just now'
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
    return `${Math.floor(diffInSeconds / 86400)}d ago`
  }

  return (
    <div className="relative" ref={bellRef}>
      <button
        onClick={toggleDropdown}
        className="relative p-2 rounded-full hover:bg-dark-border/50 transition-colors"
        aria-label="Notifications"
      >
        <Bell className="w-6 h-6 text-gray-300 hover:text-white" />
        {totalUnreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {totalUnreadCount > 9 ? '9+' : totalUnreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-dark-card rounded-lg shadow-2xl border-2 border-dark-border z-50 overflow-hidden">
          <div className="p-4 border-b border-dark-border flex justify-between items-center">
            <h3 className="font-semibold text-white">Notifications</h3>
            <button
              onClick={() => {
                setBackendNotifications([])
                setIsOpen(false)
              }}
              className="text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center text-gray-400">Loading...</div>
            ) : allNotifications.length === 0 ? (
              <div className="p-4 text-center text-gray-400">No notifications</div>
            ) : (
              <div className="divide-y divide-dark-border">
                {allNotifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`p-4 hover:bg-dark-border/30 transition-colors ${
                      !notification.read ? 'bg-dark-border/20' : ''
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <h4 className={`font-medium ${notification.type === 'error' ? 'text-red-400' : notification.type === 'success' ? 'text-green-400' : notification.type === 'reminder' ? 'text-yellow-400' : notification.type === 'recurring' ? 'text-purple-400' : 'text-blue-400'}`}>
                        {notification.title}
                      </h4>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-gray-500">
                          {formatTimeAgo(notification.timestamp)}
                        </span>
                        <button
                          onClick={() => {
                            // Check if this is a backend notification or context notification
                            const isBackendNotification = backendNotifications.some(n => n.id === notification.id)

                            if (isBackendNotification) {
                              // Remove from backend notifications
                              setBackendNotifications(prev =>
                                prev.filter(n => n.id !== notification.id)
                              )
                            } else {
                              // Remove from context notifications (bellNotifications)
                              // Find the original toast in bellNotifications to get the correct ID
                              const toastToRemove = bellNotifications.find(toast =>
                                toast.title === notification.title &&
                                toast.message === notification.message &&
                                toast.type === notification.type
                              )
                              if (toastToRemove) {
                                removeNotification(toastToRemove.id);
                              }
                            }
                          }}
                          className="text-gray-400 hover:text-white ml-2"
                          aria-label="Dismiss notification"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <p className="mt-1 text-sm text-gray-300">
                      {notification.message}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}