/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./vex-hero/index.html",
    "./vex-hero/src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
