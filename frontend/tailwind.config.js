/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        navy: { 900: '#0a1428', 800: '#10203a', 700: '#172c4d' },
        teal: { 400: '#2dd4bf', 500: '#14b8a6', 600: '#0d9488' },
      },
    },
  },
  plugins: [],
}
