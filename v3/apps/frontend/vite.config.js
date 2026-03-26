import { defineConfig } from 'vite';
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    tailwindcss(),
    sveltekit({
      onwarn: (warning, handler) => {
        if (warning.code?.startsWith('a11y_')) return;
        if (warning.code === 'css_unused_selector') return;
        if (warning.code?.includes('deprecated')) return;
        handler(warning);
      },
    }),
  ],
  clearScreen: false,
  server: {
    host: '127.0.0.1',
    port: 4173,
    strictPort: true,
  },
  preview: {
    host: '127.0.0.1',
    port: 4173,
    strictPort: true,
  },
});
