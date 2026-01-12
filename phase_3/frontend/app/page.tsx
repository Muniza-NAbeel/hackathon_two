'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { getToken } from '@/lib/auth'
import { CheckCircle, Sparkles, Bot, LayoutDashboard, ShieldCheck } from 'lucide-react'
import { motion } from 'framer-motion'

export default function LandingPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const token = getToken()
    setIsAuthenticated(!!token)
  }, [])

 const features = [
  {
    icon: <Bot className="w-8 h-8 text-neon-cyan" />,
    title: 'AI Task Assistant',
    description:
      'Use natural language to create, update, and manage tasks with the help of an intelligent AI chatbot.'
  },
  {
    icon: <CheckCircle className="w-8 h-8 text-neon-blue" />,
    title: 'Smart Task Management',
    description:
      'Easily add, edit, complete, and organize tasks with a clean and intuitive interface.'
  },
  {
    icon: <LayoutDashboard className="w-8 h-8 text-neon-purple" />,
    title: 'Interactive Dashboard',
    description:
      'View all your tasks in one place with real-time updates and smooth user experience.'
  },
  {
    icon: <ShieldCheck className="w-8 h-8 text-neon-pink" />,
    title: 'Secure Authentication',
    description:
      'Your tasks are protected with secure login and user-based access control.'
  }
]


  return (
    <div className="min-h-screen bg-dark-bg relative overflow-hidden">
      {/* Animated Background */}
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

      {/* Navigation Bar */}
      <nav className="relative z-10 border-b border-dark-border bg-dark-card/30 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <motion.div
              className="flex items-center"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
            >
              <h1 className="text-2xl font-bold bg-gradient-to-r from-neon-purple via-neon-blue to-neon-cyan bg-clip-text text-transparent">
                TaskFlow AI
              </h1>
            </motion.div>
            <motion.div
              className="flex items-center space-x-4"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              {isAuthenticated ? (
                <Link
                  href="/dashboard"
                  className="inline-flex items-center px-6 py-2.5 border border-neon-purple/50 text-sm font-medium rounded-lg text-white bg-neon-purple/10 hover:bg-neon-purple/20 focus:outline-none focus:ring-2 focus:ring-neon-purple transition-all shadow-neon-purple hover:shadow-neon-purple"
                >
                  Go to Dashboard
                </Link>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="inline-flex items-center px-6 py-2.5 border border-dark-border text-sm font-medium rounded-lg text-gray-300 hover:text-white hover:border-neon-blue/50 transition-all"
                  >
                    Login
                  </Link>
                  <Link
                    href="/signup"
                    className="inline-flex items-center px-6 py-2.5 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-neon-purple to-neon-blue hover:shadow-neon-purple focus:outline-none focus:ring-2 focus:ring-neon-purple transition-all"
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </motion.div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
        <div className="text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-5xl sm:text-6xl md:text-7xl font-extrabold text-white mb-6">
              <span className="block">Organize Your Future,</span>
              <span className="block mt-2 bg-gradient-to-r from-neon-purple via-neon-blue to-neon-cyan bg-clip-text text-transparent">
              Powered by AI Assistant .
              </span>
            </h2>
          </motion.div>

          <motion.p
            className="text-xl sm:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
             Manage your tasks efficiently with an intelligent AI chatbot that helps you
      create, organize, prioritize, and complete tasks faster — all in one place.
          </motion.p>

          <motion.div
            className="flex flex-col sm:flex-row justify-center gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            {!isAuthenticated && (
              <>
                <Link
                  href="/signup"
                  className="group inline-flex items-center justify-center px-8 py-4 text-lg font-medium rounded-xl text-white bg-gradient-to-r from-neon-purple to-neon-blue hover:shadow-neon-purple transition-all transform hover:scale-105"
                >
                  <Sparkles className="w-5 h-5 mr-2 group-hover:animate-pulse" />
                  Get Started Free
                </Link>
                <Link
                  href="/login"
                  className="inline-flex items-center justify-center px-8 py-4 border-2 border-neon-cyan/50 text-lg font-medium rounded-xl text-white hover:bg-neon-cyan/10 hover:border-neon-cyan transition-all backdrop-blur-sm"
                >
                  Sign In
                </Link>
              </>
            )}
            {isAuthenticated && (
              <Link
                href="/dashboard"
                className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium rounded-xl text-white bg-gradient-to-r from-neon-purple to-neon-blue hover:shadow-neon-purple transition-all transform hover:scale-105"
              >
                Go to Your Dashboard
              </Link>
            )}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h3 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Smart Features for Smarter Productivity!
          </h3>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
           Everything you need to manage tasks efficiently — enhanced with an intelligent AI assistant.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              className="relative group"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ y: -5 }}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-neon-purple/20 to-neon-cyan/20 rounded-2xl blur-xl group-hover:blur-2xl transition-all opacity-0 group-hover:opacity-100" />
              <div className="relative bg-dark-card/50 backdrop-blur-md p-6 rounded-2xl border border-dark-border group-hover:border-neon-purple/50 transition-all">
                <div className="mb-4">{feature.icon}</div>
                <h4 className="text-xl font-semibold text-white mb-2">
                  {feature.title}
                </h4>
                <p className="text-gray-400 leading-relaxed">{feature.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA Section - Always Visible */}
      <section className="relative z-10 py-16 sm:py-20">
        <motion.div
          className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-neon-purple/30 via-neon-blue/30 to-neon-cyan/30 rounded-3xl blur-2xl" />
            <div className="relative bg-dark-card/30 backdrop-blur-xl border border-neon-purple/30 rounded-3xl p-12">
                <>
                  <h3 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                    Let AI Help You Get Things Done!
                  </h3>
                  <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
                    Manage tasks smarter with an AI-powered assistant that understands your workflow
            and helps you stay productive every day.
                  </p>
                  <Link
                    href="/signup"
                    className="inline-flex items-center justify-center px-10 py-4 text-lg font-medium rounded-xl text-white bg-gradient-to-r from-neon-purple via-neon-blue to-neon-cyan hover:shadow-neon-purple transition-all transform hover:scale-105"
                  >
                    <Sparkles className="w-5 h-5 mr-2" />
                    Create Your Free Account
                  </Link>
                </> 
            </div>
          </div>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-dark-border bg-dark-card/30 backdrop-blur-md py-8 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-500 text-sm">
            © 2026 TaskFlow AI — AI-Powered Todo Application.  Built by Muniza Nabeel using Next.js, FastAPI & AI.
          </p>
        </div>
      </footer>
    </div>
  )
}
