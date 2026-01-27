'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { LoginForm } from '@/components/auth/LoginForm'
import { getToken } from '@/lib/auth'
import { motion } from 'framer-motion'
import { Sparkles } from 'lucide-react'

export default function LoginPage() {
  const router = useRouter()

  useEffect(() => {
    const token = getToken()
    if (token) {
      router.replace('/dashboard')
    }
  }, [router])

  return (
    <div className="min-h-screen bg-dark-bg relative overflow-hidden flex items-center justify-center">
      {/* Animated Background - Same as Landing Page */}
      <div className="absolute inset-0 bg-dark-gradient">
        <motion.div
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-neon-purple opacity-20 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.2, 0.3, 0.2],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-neon-cyan opacity-20 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.2, 0.25, 0.2],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1
          }}
        />
        <motion.div
          className="absolute top-1/2 right-1/3 w-80 h-80 bg-neon-blue opacity-15 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.4, 1],
            opacity: [0.15, 0.25, 0.15],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2
          }}
        />
      </div>

      {/* Back to Home Link */}
      <Link
        href="/"
        className="absolute top-8 left-8 flex items-center space-x-2 text-gray-400 hover:text-white transition-colors z-10"
      >
        <Sparkles className="w-5 h-5 text-neon-purple" />
        <span className="text-sm font-medium">Back to Home</span>
      </Link>

      {/* Login Card */}
      <motion.div
        className="relative z-10 w-full max-w-md px-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Glass Card */}
        <div className="relative">
          {/* Glow Effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-neon-purple/30 via-neon-blue/30 to-neon-cyan/30 rounded-3xl blur-2xl opacity-50" />

          {/* Card Content */}
          <div className="relative bg-dark-card/50 backdrop-blur-xl border border-dark-border rounded-3xl p-8 sm:p-10 shadow-glass">
            {/* Header */}
            <div className="text-center mb-8">
              <motion.h1
                className="text-3xl sm:text-4xl font-bold text-white mb-2"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                Welcome Back
              </motion.h1>
              <motion.p
                className="text-gray-400"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                Sign in to continue to{' '}
                <span className="bg-gradient-to-r from-neon-purple to-neon-cyan bg-clip-text text-transparent font-semibold">
                  TaskFlow AI
                </span>
              </motion.p>
            </div>

            {/* Login Form */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <LoginForm />
            </motion.div>

            {/* Sign Up Link */}
            <motion.div
              className="mt-6 text-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <p className="text-sm text-gray-400">
                Don't have an account?{' '}
                <Link
                  href="/signup"
                  className="text-neon-cyan hover:text-neon-blue transition-colors font-medium"
                >
                  Sign up
                </Link>
              </p>
            </motion.div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
