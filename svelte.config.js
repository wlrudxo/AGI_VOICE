// Tauri doesn't have a Node.js server to do proper SSR
// so we use adapter-static with a fallback to index.html to put the site in SPA mode
// See: https://svelte.dev/docs/kit/single-page-apps
// See: https://v2.tauri.app/start/frontend/sveltekit/ for more info
import adapter from "@sveltejs/adapter-static";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  onwarn: (warning, handler) => {
    // Ignore all a11y warnings (Svelte 5 uses underscores)
    if (warning.code.startsWith('a11y_')) return;

    // Ignore unused CSS selector warnings
    if (warning.code === 'css_unused_selector') return;

    // Ignore deprecated warnings
    if (warning.code.includes('deprecated')) return;

    // Let all other warnings through
    handler(warning);
  },
  kit: {
    adapter: adapter({
      fallback: "index.html",
    }),
  },
};

export default config;
