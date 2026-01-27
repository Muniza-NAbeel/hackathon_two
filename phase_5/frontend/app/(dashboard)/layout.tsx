'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getToken } from '@/lib/auth'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import Navbar from '@/components/ui/Navbar'
import { motion } from 'framer-motion'
import { NotificationProvider } from '@/components/notifications/NotificationProvider'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = getToken()

    if (!token) {
      // Redirect to login page when not authenticated
      // (Logout button handles direct navigation to landing page)
      router.replace('/login')
      return
    }

    setLoading(false)
  }, [router])

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <NotificationProvider>
      <div className="min-h-screen bg-dark-bg relative">
        {/* Subtle background glow */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-0 right-1/4 w-96 h-96 bg-neon-purple/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-neon-cyan/10 rounded-full blur-3xl" />
        </div>

        {/* Navbar */}
        <Navbar />

        {/* Main content */}
        <motion.main
          className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          {children}
        </motion.main>
      </div>
    </NotificationProvider>
  )
}
