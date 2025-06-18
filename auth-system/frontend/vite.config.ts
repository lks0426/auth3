import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    }
  },
  server: {
    host: '0.0.0.0', // 允许外部访问，Docker 容器必需
    port: 3000,      // 明确指定端口
    watch: {
      usePolling: true, // Docker 中文件监听需要轮询
    },
  },
  build: {
    outDir: 'dist',  // 确保输出目录正确
  }
})