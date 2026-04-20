/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: "#0F172A",
        card: "#1E293B",
        primary: "#3B82F6",
        accent: "#10B981"
      }
    },
  },
  plugins: [],
}
