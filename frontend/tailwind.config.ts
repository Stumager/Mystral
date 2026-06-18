import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          deep:    '#060414',
          surface: '#0D0B1F',
          card:    'rgba(13,11,31,0.72)',
        },
        violet: {
          600: '#6B4EFF',
          400: '#9B8AFF',
          200: '#B6A6FF',
        },
        gold: {
          600: '#C9A84C',
          300: '#EFD080',
        },
        text: {
          primary: '#F0EAFF',
          warm:    '#FBF3D8',
          muted:   '#9B8FBB',
          faint:   'rgba(200,180,255,0.45)',
        },
        border: {
          subtle: 'rgba(140,110,255,0.15)',
          medium: 'rgba(140,110,255,0.30)',
        },
      },
      fontFamily: {
        display: ['Cormorant Garamond', 'Georgia', 'serif'],
        sans:    ['-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config;
