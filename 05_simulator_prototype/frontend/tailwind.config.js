/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        neonBlue: '#00f3ff',
        neonPurple: '#bc13fe',
        darkSurface: '#0f172a',
        darkerBg: '#020617',
      },
      boxShadow: {
        'neon-blue': '0 0 10px #00f3ff, 0 0 20px #00f3ff',
        'neon-red': '0 0 10px #ff003c, 0 0 20px #ff003c',
        'neon-green': '0 0 10px #00ff66, 0 0 20px #00ff66',
      }
    },
  },
  plugins: [],
}
