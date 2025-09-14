// vite.config.js
import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  build: {
    outDir: 'app/static/dist', // ✅ put build output inside Flask's static folder
    emptyOutDir: true,
    rollupOptions: {
      input: {
        student_calendar: resolve(__dirname, 'app/static/js/student_calendar.js'),
        teacher_calendar: resolve(__dirname, 'app/static/js/teacher_calendar.js'),
      },
      output: {
        entryFileNames: 'assets/[name].js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name].[ext]',
      },
    },
  },
});
