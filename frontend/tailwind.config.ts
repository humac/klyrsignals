import type { Config } from "tailwindcss";

export default {
  darkMode: 'class', // Enable class-based dark mode
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Add dark mode color palette
        dark: {
          bg: '#0f172a',      // slate-950
          surface: '#1e293b', // slate-800
          border: '#334155',  // slate-700
          text: '#f1f5f9',    // slate-100
          muted: '#94a3b8',   // slate-400
        }
      }
    },
  },
  plugins: [],
} satisfies Config;
