/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#e8f6f3',
        mint: '#b8e6dd',
        'mint-active': '#7dd3c4',
        card: '#ffffff',
        main: '#fafdfc',
        content: '#1a3d36',
        contentSecondary: '#5a7a73',
        contentMuted: '#8fa39e',
        onMint: '#ffffff',
        borderLight: 'rgba(26, 61, 54, 0.08)',
        borderInput: '#c5e0db',
        error: '#dc2626',
      },
      fontFamily: {
        sans: ['Segoe UI', 'Poppins', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      fontSize: {
        xs: '12px',
        sm: '14px',
        base: '16px',
        lg: '18px',
        xl: '22px',
        '2xl': '24px',
      },
      spacing: {
        '1': '8px',
        '2': '16px',
        '3': '24px',
        '4': '32px',
        '5': '40px',
        '6': '48px',
        sidebar: '220px',
        'sidebar-right': '260px',
      },
      borderRadius: {
        sm: '8px',
        md: '12px',
        card: '16px',
      },
      boxShadow: {
        soft: '0 4px 20px rgba(26, 61, 54, 0.06)',
        card: '0 4px 24px rgba(26, 61, 54, 0.08)',
      },
      width: {
        sidebar: '220px',
        'sidebar-right': '260px',
      },
      minWidth: {
        sidebar: '220px',
        'sidebar-right': '260px',
      },
      ringColor: {
        focus: 'rgba(125, 211, 196, 0.25)',
      },
      screens: {
        'home-sm': '600px',
      },
    },
  },
  plugins: [],
}
