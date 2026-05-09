/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{svelte,js,ts}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      colors: {
        page: '#ffffff',
        surface: '#f8fafc',
        card: '#ffffff',
        border: {
          DEFAULT: '#e2e8f0',
          strong: '#cbd5e1',
        },
        text: {
          primary: '#0f172a',
          secondary: '#475569',
          muted: '#64748b',
        },
        accent: {
          DEFAULT: '#2563eb',
          hover: '#1d4ed8',
          light: '#dbeafe',
          text: '#1e3a8a',
        },
        success: '#059669',
        warning: '#d97706',
        error: '#dc2626',
        // Semantic badge colors — all WCAG AA on their backgrounds
        badge: {
          local: { bg: '#f0fdf4', text: '#166534' },
          global: { bg: '#eff6ff', text: '#1e40af' },
          product: { bg: '#faf5ff', text: '#7c3aed' },
          service: { bg: '#fff7ed', text: '#c2410c' },
          employees: { bg: '#f1f5f9', text: '#334155' },
          tag: { bg: '#f8fafc', text: '#475569', border: '#e2e8f0' },
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
