import { svelte } from '@sveltejs/vite-plugin-svelte';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';

// The page devkit viewer serve ships: built into the Python package and committed (viewer-assets).
const outDir = fileURLToPath(new URL('../src/devkit_viewer/static', import.meta.url));

export default defineConfig({
	plugins: [svelte()],
	base: './',
	build: {
		outDir,
		emptyOutDir: true,
		chunkSizeWarningLimit: 4096,
		rollupOptions: {
			output: {
				// What the page and Mermaid's lazily loaded chunks share (the libraries and Vite's preload helper)
				// gets a chunk of its own, so an edit to the viewer's code rewrites the page's chunk only.
				manualChunks: (id) =>
					/node_modules\/(svelte|dompurify|marked|yaml)\/|vite\/preload-helper/.test(id)
						? 'vendor'
						: undefined
			}
		}
	},
	resolve: { conditions: ['browser'] },
	test: { environment: 'jsdom', include: ['src/**/*.test.ts'] }
});
