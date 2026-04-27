// tailwind.config.js
import forms from "@tailwindcss/forms";
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        maritime: {
          50: "#eff8ff",
          100: "#daf0ff",
          200: "#bde4ff",
          300: "#8dd4ff",
          400: "#56baff",
          500: "#2e9cff",
          600: "#1a7ef5",
          700: "#1365e1",
          800: "#1651b6",
          900: "#184590",
          950: "#132b57",
        },
        blue: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
          800: "#1e40af",
          900: "#1e3a8a",
          950: "#172554",
        },
        navy: {
          50: "#f4f6fa",
          100: "#e9ecf5",
          200: "#c7d1e6",
          300: "#9fb3d6",
          400: "#5a78b7",
          500: "#314d8a",
          600: "#24396a",
          700: "#1a2c54",
          800: "#0f1d38",
          900: "#0a1427",
        },
        gray: {
          50: "#fafafa",
          100: "#f5f5f5",
          200: "#e5e5e5",
          300: "#d4d4d4",
          400: "#a3a3a3",
          500: "#737373",
          600: "#525252",
          700: "#404040",
          800: "#262626",
          900: "#171717",
        },
      },
      backgroundImage: {
        "maritime-gradient":
          "linear-gradient(135deg, #1a7ef5 0%, #2e9cff 50%, #56baff 100%)",
        "maritime-gradient-dark":
          "linear-gradient(135deg, #1365e1 0%, #1a7ef5 50%, #2e9cff 100%)",
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease-in-out",
        "slide-up": "slideUp 0.6s ease-out",
        "pulse-slow": "pulse 3s infinite",
        float: "float 3s ease-in-out infinite",
        "gradient-x": "gradient-x 15s ease infinite",
        "gradient-y": "gradient-y 15s ease infinite",
        "gradient-xy": "gradient-xy 15s ease infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(30px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        "gradient-y": {
          "0%, 100%": {
            "background-size": "400% 400%",
            "background-position": "center top",
          },
          "50%": {
            "background-size": "200% 200%",
            "background-position": "center center",
          },
        },
        "gradient-x": {
          "0%, 100%": {
            "background-size": "200% 200%",
            "background-position": "left center",
          },
          "50%": {
            "background-size": "200% 200%",
            "background-position": "right center",
          },
        },
        "gradient-xy": {
          "0%, 100%": {
            "background-size": "400% 400%",
            "background-position": "left center",
          },
          "50%": {
            "background-size": "200% 200%",
            "background-position": "right center",
          },
        },
      },
      fontFamily: {
        sans: ["Poppins", "Inter", "system-ui", "sans-serif"],
      },
      spacing: {
        18: "4.5rem",
        88: "22rem",
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.5rem",
        "3xl": "2rem",
        full: "9999px",
      },
      boxShadow: {
        maritime: "0 4px 20px rgba(26, 126, 245, 0.15)",
        "maritime-lg": "0 10px 40px rgba(26, 126, 245, 0.2)",
        "inner-light": "inset 0 1px 0 rgba(255, 255, 255, 0.1)",
        card: "0 4px 10px rgba(0,0,0,0.08)",
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [
    forms({
      strategy: "class",
    }),
  ],
};
