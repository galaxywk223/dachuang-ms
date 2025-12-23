import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  build: {
    chunkSizeWarningLimit: 900,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes("node_modules")) return;
          if (id.includes("@element-plus/icons-vue")) return "element-plus-icons";
          if (id.includes("element-plus")) return "element-plus";
          if (id.includes("vue-router")) return "vue-router";
          if (id.includes("pinia")) return "pinia";
          if (id.includes("axios")) return "axios";
          return "vendor";
        },
      },
    },
  },
  server: {
    // Use polling so file changes on Windows/WSL mounts are detected reliably
    watch: {
      usePolling: true,
      interval: 150,
    },
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        api: "modern-compiler", // 使用现代 Sass API
        additionalData: `@use "@/styles/variables.scss" as *;`,
      },
    },
  },
});
