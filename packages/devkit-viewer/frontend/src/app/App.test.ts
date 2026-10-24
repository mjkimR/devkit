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
	}
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
			if (path.endsWith('/dashboard-list'))
				return new Response(JSON.stringify({ items: [], errors: [] }));
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
	it('sends reads to the selected repository and displays its current branch without a selector', async () => {
		render(App);
		await waitFor(() => expect(reads('/api/repos/alpha/').length).toBeGreaterThan(0));
		expect(reads('/api/repos/alpha/dashboard-list').every((url) => !url.includes('ref='))).toBe(
			true
		);

		await fireEvent.change(screen.getByLabelText('Repository'), { target: { value: 'beta' } });
		await waitFor(() => expect(reads('/api/repos/beta/dashboard-list').length).toBeGreaterThan(0));
		expect(reads('/api/repos/beta/dashboard-list').every((url) => !url.includes('ref='))).toBe(
			true
		);
		expect(screen.queryByLabelText('Branch')).toBeNull();
		expect(screen.getByText('Branch: main')).toBeTruthy();
		expect(window.location.hash).toBe(writeLocation('beta'));
	});

	it('opens the repository in the address and ignores an old branch fragment', async () => {
		window.location.hash = '#repo=beta&ref=dev-y';
		render(App);
		await waitFor(() => expect(reads('/api/repos/beta/dashboard-list').length).toBeGreaterThan(0));
		expect(reads('/api/repos/beta/dashboard-list').every((url) => !url.includes('ref='))).toBe(
			true
		);
		expect(reads('/api/repos/alpha/')).toEqual([]);
	});
});

describe('location', () => {
	it('round-trips the repository and ignores branch selection', () => {
		expect(readLocation(writeLocation('a b'))).toEqual({ repo: 'a b' });
		expect(readLocation('#repo=a&ref=dev-x')).toEqual({ repo: 'a' });
		expect(readLocation('')).toEqual({ repo: '' });
	});
});
