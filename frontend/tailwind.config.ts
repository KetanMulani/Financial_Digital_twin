import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#080b10",
        "bg-2": "#0b0f16",
        panel: "#10151d",
        "panel-2": "#141a23",
        line: "rgba(255,255,255,0.07)",
        "line-strong": "rgba(255,255,255,0.12)",
        text: {
          DEFAULT: "#eef2f6",
          dim: "#8a94a3",
          faint: "#5a6472",
        },
        accent: {
          DEFAULT: "#2dd4c8",
          soft: "rgba(45, 212, 200, 0.14)",
          glow: "rgba(45, 212, 200, 0.35)",
        },
        greyline: "#4a5568",
        pos: "#8fe3d4",
        neg: "#e39a8f",
      },
      fontFamily: {
        display: ["Space Grotesk", "Inter", "system-ui", "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
      },
      borderRadius: {
        lg: "22px",
        md: "16px",
        sm: "10px",
      },
      keyframes: {
        fadeIn: {
          from: { opacity: "0", transform: "translateY(6px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        blink: {
          "0%, 100%": { opacity: "0" },
          "50%": { opacity: "1" },
        },
        drawLine: {
          "0%": { strokeDashoffset: "400" },
          "60%": { strokeDashoffset: "0" },
          "100%": { strokeDashoffset: "-400" },
        },
      },
      animation: {
        fadeIn: "fadeIn 0.35s ease",
        blink: "blink 1.4s infinite",
        drawLine: "drawLine 1.8s ease-in-out infinite",
      },
      boxShadow: {
        card: "0 30px 60px -30px rgba(0,0,0,.6)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config;
