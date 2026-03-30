/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        vajra: {
          bg: "#0a0a0f",
          surface: "rgba(30, 30, 45, 0.6)",
          border: "rgba(255, 255, 255, 0.08)",
          accent: "#6366f1",
          "accent-glow": "rgba(99, 102, 241, 0.3)",
          success: "#22c55e",
          warning: "#f59e0b",
          danger: "#ef4444",
          muted: "rgba(255, 255, 255, 0.5)",
        },
      },
      backdropBlur: {
        glass: "20px",
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
        dock: "0 0 30px rgba(99, 102, 241, 0.15)",
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "SF Pro Display",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        mono: ["SF Mono", "Fira Code", "monospace"],
      },
    },
  },
  plugins: [],
};
