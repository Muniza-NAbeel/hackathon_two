'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useEffect, useState } from 'react'
import { getToken, getUser, clearAuth } from '@/lib/auth'
import { LogOut, LayoutDashboard, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'
import NotificationBell from '@/components/notifications/NotificationBell'

export default function Navbar() {
  const pathname = usePathname()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [userName, setUserName] = useState<string | null>(null)

  useEffect(() => {
    const token = getToken()
    setIsAuthenticated(!!token)

    // Get user name
    const user = getUser()
    if (user?.name) {
      setUserName(user.name)
    } else if (user?.email) {
      // Fallback to email prefix if no name
      setUserName(user.email.split('@')[0])
    }
  }, [pathname])

  // Logout - clear auth and navigate to landing page
  const handleLogout = () => {
    // Clear auth data from localStorage
    clearAuth()

    // Direct navigation to landing page (avoid reload race condition)
    window.location.href = '/'
  }

  return (
    <motion.nav
      className="bg-dark-card/50 backdrop-blur-xl border-b border-dark-border shadow-lg sticky top-0 z-[100]"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">

          <Link href="/" className="flex items-center space-x-2 group">
            <Sparkles className="w-6 h-6 text-neon-purple group-hover:text-neon-cyan transition-colors" />
            <span className="text-xl font-bold bg-gradient-to-r from-neon-purple via-neon-blue to-neon-cyan bg-clip-text text-transparent">
              TaskFlow AI
            </span>
          </Link>

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link
                  href="/dashboard"
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    pathname.startsWith('/dashboard') || pathname.startsWith('/tasks')
                      ? 'text-white bg-neon-purple/20 border border-neon-purple/50'
                      : 'text-gray-300 hover:text-white hover:bg-dark-border/50'
                  }`}
                  title="View your tasks and manage your todo list"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  <span>Dashboard</span>
                </Link>

                <NotificationBell />

                <div className="relative z-[101]">
                  <button
                    onClick={() => setShowUserMenu(!showUserMenu)}
                    className="flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium text-gray-300 hover:text-white hover:bg-dark-border/50 transition-all border border-dark-border hover:border-neon-blue/50"
                  >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-neon-purple to-neon-blue flex items-center justify-center">
                      <span className="text-white text-sm font-semibold">
                        {userName ? userName.charAt(0).toUpperCase() : 'U'}
                      </span>
                    </div>
                    {userName && (
                      <span className="hidden sm:inline text-gray-200">{userName}</span>
                    )}
                  </button>

                  {showUserMenu && (
                    <div className="fixed right-4 top-16 w-56 bg-dark-card rounded-lg shadow-2xl border-2 border-dark-border p-2 z-[9999]">
                      <button
                        onClick={handleLogout}
                        onMouseDown={(e) => e.stopPropagation()}
                        className="flex items-center justify-center w-full px-5 py-4 text-white text-base font-bold bg-red-600 hover:bg-red-700 active:bg-red-800 rounded-lg transition-all duration-150 shadow-lg hover:shadow-xl transform hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
                      >
                        <LogOut className="w-5 h-5 mr-3" />
                        Logout
                      </button>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="px-6 py-2 border border-dark-border text-sm font-medium rounded-lg text-gray-300 hover:text-white hover:border-neon-blue/50 transition-all"
                >
                  Login
                </Link>
                <Link
                  href="/signup"
                  className="px-6 py-2 text-sm font-medium rounded-lg text-white bg-gradient-to-r from-neon-purple to-neon-blue hover:shadow-neon-purple transition-all"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </motion.nav>
  )
}
