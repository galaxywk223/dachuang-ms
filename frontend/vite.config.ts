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
          const normalized = id.replace(/\\/g, "/");
          if (id.includes("@element-plus/icons-vue")) return "element-plus-icons";
          if (id.includes("element-plus")) return "element-plus";
          if (normalized.includes("node_modules/vue-router")) return "vue-router";
          if (normalized.includes("node_modules/pinia")) return "pinia";
          if (normalized.includes("node_modules/axios")) return "axios";
          if (
            normalized.includes("node_modules/@vue/") ||
            normalized.includes("node_modules/vue/")
          ) {
            return "vue-core";
          }
          if (
            normalized.includes("node_modules/echarts") ||
            normalized.includes("node_modules/zrender")
          ) {
            return "echarts";
          }
          if (normalized.includes("node_modules/@antv/")) return "antv";
          if (normalized.includes("node_modules/@headlessui/")) return "headlessui";
          if (normalized.includes("node_modules/@heroicons/")) return "heroicons";
          if (
            normalized.includes("node_modules/read-excel-file") ||
            normalized.includes("node_modules/xlsx")
          ) {
            return "excel";
          }
          if (
            normalized.includes("node_modules/lodash") ||
            normalized.includes("node_modules/lodash-es")
          ) {
            return "lodash";
          }
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
