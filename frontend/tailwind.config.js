/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "1rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      fontFamily: {
        display: ["'Playfair Display'", "serif"],
        sans: ["Outfit", "system-ui", "sans-serif"],
        admin: ["'IBM Plex Sans'", "system-ui", "sans-serif"],
      },
      colors: {
        afro: {
          bg: "#FDFBF7",
          surface: "#FFFFFF",
          "surface-alt": "#F5F0E6",
          primary: "#8C3219",
          "primary-hover": "#6D2511",
          secondary: "#2A4526",
          accent: "#D19C4C",
          ink: "#1A1716",
          "ink-soft": "#5C5654",
          border: "#E8DFD3",
          error: "#B82F2F",
        },
        admin: {
          bg: "#F9FAFB",
          surface: "#FFFFFF",
          ink: "#111827",
          "ink-soft": "#4B5563",
          border: "#E5E7EB",
          accent: "#8C3219",
        },
      },
      borderRadius: {
        lg: "0.625rem",
        md: "0.5rem",
        sm: "0.375rem",
      },
      boxShadow: {
        card: "0 1px 2px rgba(17,24,39,.04), 0 2px 8px rgba(17,24,39,.04)",
        pop: "0 20px 40px -12px rgba(26,23,22,.18)",
      },
      keyframes: {
        "fade-up": {
          from: { opacity: 0, transform: "translateY(12px)" },
          to: { opacity: 1, transform: "translateY(0)" },
        },
        "slide-in": {
          from: { transform: "translateX(100%)" },
          to: { transform: "translateX(0)" },
        },
      },
      animation: {
        "fade-up": "fade-up .6s ease-out",
        "slide-in": "slide-in .3s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
