import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#11221E",
          light: "#1A322C",
        },
        parchment: {
          DEFAULT: "#F6F2EA",
          dim: "#EFE9DC",
        },
        gold: {
          DEFAULT: "#C9A05C",
          dark: "#2A2008",
        },
        sage: {
          DEFAULT: "#5B7A6E",
          light: "#7B998D",
        },
        crisis: {
          DEFAULT: "#C23B3B",
          dim: "rgba(194, 59, 59, 0.18)",
        },
        warm: {
          DEFAULT: "#9A958A",
          light: "#c9c4b8",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "Georgia", "serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      transitionTimingFunction: {
        "mb-ease": "cubic-bezier(0.16, 1, 0.3, 1)",
      },
    },
  },
  plugins: [],
};

export default config;
