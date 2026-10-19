import { svelte } from '@sveltejs/vite-plugin-svelte';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';

// The page devkit viewer serve ships: built into the Python package and committed (viewer-assets).
const outDir = fileURLToPath(new URL('../src/devkit_viewer/static', import.meta.url));

export default defineConfig({
	plugins: [svelte()],
	base: './',
	build: { outDir, emptyOutDir: true, chunkSizeWarningLimit: 4096 },
	resolve: { conditions: ['browser'] },
	test: { environment: 'jsdom', include: ['src/**/*.test.ts'] }
});
