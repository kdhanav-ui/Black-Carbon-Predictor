/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#0a0e17',
        surface: '#111827',
        'surface-elevated': '#1e293b',
        border: '#1f293d',
        accent: {
          blue: '#3b82f6',
          teal: '#14b8a6',
          emerald: '#10b981',
          amber: '#f59e0b',
          rose: '#ef4444',
          purple: '#8b5cf6',
          cyan: '#06b6d4',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      }
    },
  },
  plugins: [],
}
