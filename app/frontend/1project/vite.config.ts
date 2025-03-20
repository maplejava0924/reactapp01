import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  base: "./",
  plugins: [react(), tailwindcss()],
  server: {
    host: true, //localhostに加えてホストのIPアドレス指定でのアクセスを許可
    watch: {
      usePolling: true, // ファイル変更をポーリングして確実に検知
    },
    port: 3000, //3000ポートでリクエストを受付するよう指定
  },
  resolve: {
    preserveSymlinks: true,
  },
});
