import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        neon: {
          purple: '#a78bfa',
          blue: '#60a5fa',
          cyan: '#22d3ee',
          pink: '#f472b6',
        },
        dark: {
          bg: '#0a0a0f',
          card: '#1a1a24',
          border: '#2a2a3a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'dark-gradient': 'linear-gradient(135deg, #0a0a0f 0%, #1a0f2e 50%, #0a0a0f 100%)',
        'neon-glow': 'radial-gradient(ellipse at center, rgba(167, 139, 250, 0.15) 0%, transparent 70%)',
      },
      backdropBlur: {
        'glass': '12px',
      },
      boxShadow: {
        'neon-purple': '0 0 20px rgba(167, 139, 250, 0.3)',
        'neon-blue': '0 0 20px rgba(96, 165, 250, 0.3)',
        'neon-cyan': '0 0 20px rgba(34, 211, 238, 0.3)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      },
    },
  },
  plugins: [],
}

export default config
