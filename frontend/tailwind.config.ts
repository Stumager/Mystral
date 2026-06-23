import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          deep:    '#07060F',
          dark:    '#050409',
          base:    '#07060F',
          surface: '#0D0B1F',
          card:    'rgba(255,255,255,0.025)',
        },
        gold: {
          DEFAULT: '#C9A84C',
          light:   '#E8CD7E',
          dark:    '#A9882F',
          darker:  '#8A6E2E',
          600:     '#C9A84C',
          300:     '#EFD080',
        },
        indigo: {
          DEFAULT: '#4B3C86',
          light:   '#8A7FC0',
          lighter: '#A99BE0',
        },
        violet: {
          600: '#6B4EFF',
          400: '#9B8AFF',
          200: '#B6A6FF',
        },
        text: {
          primary:   '#F0E9DA',
          secondary: '#B6AC98',
          warm:      '#FBF3D8',
          muted:     '#A89E8B',
          dim:       '#6E6757',
          dimmer:    '#8A8170',
          faint:     'rgba(200,180,255,0.45)',
        },
        border: {
          subtle:  'rgba(255,255,255,0.06)',
          default: 'rgba(255,255,255,0.07)',
          medium:  'rgba(140,110,255,0.30)',
          gold:    'rgba(201,168,76,0.14)',
        },
        danger: {
          DEFAULT: '#D98A8A',
        },
      },
      fontFamily: {
        cinzel:     ['Cinzel', 'serif'],
        cormorant:  ['Cormorant Garamond', 'serif'],
        display:    ['Cormorant Garamond', 'Georgia', 'serif'],
        inter:      ['Inter', 'sans-serif'],
        sans:       ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      borderRadius: {
        xl:  '22px',
        lg:  '18px',
        md:  '14px',
        sm:  '12px',
        xs:  '9px',
      },
    },
  },
  plugins: [],
} satisfies Config;
