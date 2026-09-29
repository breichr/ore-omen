import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		// Same origin as in production (Caddy strips /api before the API)
		proxy: {
			'/api': {
				target: process.env.API_URL ?? 'http://localhost:8000',
				rewrite: (path) => path.replace(/^\/api/, '')
			}
		}
	},
	test: {
		include: ['src/**/*.test.ts']
	}
});
