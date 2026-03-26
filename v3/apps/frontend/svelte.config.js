import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

const config = {
  preprocess: vitePreprocess(),
  onwarn: (warning, handler) => {
    if (warning.code?.startsWith('a11y_')) return;
    if (warning.code === 'css_unused_selector') return;
    if (warning.code?.includes('deprecated')) return;
    handler(warning);
  },
  kit: {
    adapter: adapter({
      fallback: 'index.html',
    }),
  },
};

export default config;
