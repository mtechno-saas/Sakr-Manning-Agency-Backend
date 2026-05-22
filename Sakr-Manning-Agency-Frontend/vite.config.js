import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import svgr from "vite-plugin-svgr";
// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), svgr()],
  server: {
    historyApiFallback: true,
    proxy: {
      "/ai": {
        target: "https://backend.sakrshipping.com",
        changeOrigin: true,
        secure: true,
      },
    },
  },
});

