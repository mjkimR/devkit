import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import App from './App.svelte';
import { readLocation, writeLocation } from './api';

const answers: Record<string, unknown> = {
	'/api/repos': {
		repos: [
			{ id: 'alpha', default_branch: 'main' },
			{ id: 'beta', default_branch: 'main' }
		]
	},
	'/api/repos/alpha/refs': { default_branch: 'main', branches: ['main'] },
	'/api/repos/beta/refs': { default_branch: 'main', branches: ['dev-y', 'main', 'plan-x'] }
};

let calls: string[] = [];

beforeEach(() => {
	calls = [];
	window.location.hash = '';
	vi.stubGlobal(
		'fetch',
		vi.fn(async (input: string) => {
			calls.push(input);
			const path = input.split('?')[0];
			if (path in answers) return new Response(JSON.stringify(answers[path]));
			if (path.endsWith('/info')) return new Response(JSON.stringify({ default_branch: 'main' }));
			if (path.endsWith('/tree')) return new Response(JSON.stringify({ items: [] }));
			return new Response('{}', { status: 404 });
		})
	);
});
afterEach(() => {
	cleanup();
	vi.unstubAllGlobals();
});

const reads = (prefix: string) =>
	calls.filter((url) => url.startsWith(prefix) && !url.endsWith('/refs'));

describe('App', () => {
	it('sends every viewer read to the picked repository and branch', async () => {
		render(App);
		await waitFor(() => expect(reads('/api/repos/alpha/').length).toBeGreaterThan(0));
		expect(reads('/api/repos/alpha/tree').every((url) => url.includes('ref=main'))).toBe(true);

		await fireEvent.change(screen.getByLabelText('저장소'), { target: { value: 'beta' } });
		await waitFor(() => expect(calls).toContain('/api/repos/beta/refs'));
		await waitFor(() => expect(reads('/api/repos/beta/tree').length).toBeGreaterThan(0));

		calls = [];
		await fireEvent.change(screen.getByLabelText('브랜치'), { target: { value: 'plan-x' } });
		await waitFor(() => expect(reads('/api/repos/beta/tree').length).toBeGreaterThan(0));
		const after = calls.filter((url) => url.startsWith('/api/repos/') && url.includes('ref='));
		expect(
			after.every((url) => url.startsWith('/api/repos/beta/') && url.includes('ref=plan-x'))
		).toBe(true);
		expect(window.location.hash).toBe(writeLocation('beta', 'plan-x'));
	});

	it('opens the repository and branch named in the address', async () => {
		window.location.hash = writeLocation('beta', 'dev-y');
		render(App);
		await waitFor(() => expect(reads('/api/repos/beta/tree').length).toBeGreaterThan(0));
		expect(reads('/api/repos/beta/tree').every((url) => url.includes('ref=dev-y'))).toBe(true);
		expect(reads('/api/repos/alpha/')).toEqual([]);
	});
});

describe('location', () => {
	it('round-trips repository and branch', () => {
		expect(readLocation(writeLocation('a b', 'dev-x/y'))).toEqual({ repo: 'a b', ref: 'dev-x/y' });
		expect(readLocation('')).toEqual({ repo: '', ref: '' });
	});
});
