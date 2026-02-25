/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'soc': {
                    'bg': '#0a0e1a',
                    'surface': '#111827',
                    'card': '#1a1f35',
                    'border': '#1e293b',
                    'hover': '#243044',
                    'cyan': '#06b6d4',
                    'cyan-dim': '#0891b2',
                    'green': '#10b981',
                    'amber': '#f59e0b',
                    'red': '#ef4444',
                    'purple': '#8b5cf6',
                    'blue': '#3b82f6',
                    'text': '#e2e8f0',
                    'muted': '#94a3b8',
                    'dim': '#64748b',
                }
            },
            fontFamily: {
                'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
                'sans': ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
                'slide-up': 'slideUp 0.3s ease-out',
                'fade-in': 'fadeIn 0.5s ease-out',
            },
            keyframes: {
                glow: {
                    '0%': { boxShadow: '0 0 5px rgba(6, 182, 212, 0.2)' },
                    '100%': { boxShadow: '0 0 20px rgba(6, 182, 212, 0.4)' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(10px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
            },
            backdropBlur: {
                'xs': '2px',
            },
        },
    },
    plugins: [],
}
