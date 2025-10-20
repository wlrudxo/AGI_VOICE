import { defineConfig } from "vite";
import { sveltekit } from "@sveltejs/kit/vite";
import tailwindcss from "@tailwindcss/vite";

// @ts-expect-error process is a nodejs global
const host = process.env.TAURI_DEV_HOST;

// https://vite.dev/config/
export default defineConfig(async () => ({
  plugins: [
    tailwindcss(),
    sveltekit({
      onwarn: (warning, handler) => {
        // Ignore all a11y warnings (Svelte 5 uses underscores)
        if (warning.code.startsWith('a11y_')) return;

        // Ignore unused CSS selector warnings
        if (warning.code === 'css_unused_selector') return;

        // Ignore deprecated warnings
        if (warning.code.includes('deprecated')) return;

        // Let all other warnings through
        handler(warning);
      }
    })
  ],

  // Vite options tailored for Tauri development and only applied in `tauri dev` or `tauri build`
  //
  // 1. prevent Vite from obscuring rust errors
  clearScreen: false,
  // 2. tauri expects a fixed port, fail if that port is not available
  server: {
    port: 1420,
    strictPort: true,
    host: host || false,
    hmr: host
      ? {
          protocol: "ws",
          host,
          port: 1421,
        }
      : undefined,
    watch: {
      // 3. tell Vite to ignore watching `src-tauri`, `backend`, and documentation files
      ignored: [
        "**/src-tauri/**",
        "**/backend/**",
        "**/CLAUDE.md",
        "**/README.md",
        "**/ARCHITECTURE.md",
        "**/*.md"
      ],
    },
  },
}));
