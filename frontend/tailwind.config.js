/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f2f7fb',
          100: '#e3eef6',
          200: '#c2ddeb',
          300: '#90c2db',
          400: '#56a1c7',
          500: '#3385b0',
          600: '#256b92',
          700: '#1f5777',
          800: '#1c4a63',
          900: '#1b3f54',
          950: '#112938',
        },
      },
    },
  },
  plugins: [],
}
