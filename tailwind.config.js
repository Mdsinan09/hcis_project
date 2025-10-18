/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        // Ensures the professional "Inter" font is available
        inter: ['Inter', 'sans-serif'], 
      },
      colors: {
        // Defined custom colors used in the App.jsx file
        'charcoal': '#1a1a1a',
      }
    },
  },
  plugins: [],
}
