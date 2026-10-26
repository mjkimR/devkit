import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import KnowledgeViews from './KnowledgeViews.svelte';
import type { RepositoryDataSource } from '../../api/repository';

const checkout: Record<string, string> = {
	'docs/proposals/PROP-a/proposal.md':
		'---\nid: PROP-a\ntitle: Checkout A\nstatus: draft\n---\n# A\n',
	'docs/proposals/PROP-b/proposal.md':
		'---\nid: PROP-b\ntitle: Checkout B\nstatus: draft\n---\n# B\n'
};
const planned: Record<string, string> = {
	'docs/proposals/PROP-a/proposal.md':
		'---\nid: PROP-a\ntitle: Planned A\nstatus: review\n---\n# Planned A\nBody from the worktree.\n',
	'docs/proposals/PROP-a/materials/notes.md': '# Planning notes\nUntracked material.\n',
	'docs/proposals/PROP-n/proposal.md':
		'---\nid: PROP-n\ntitle: Planned only\nstatus: draft\n---\n# N\n'
};
const sources = [
	{ id: 'worktree:plan-a', kind: 'worktree' as const, label: 'worktree plan-a', slug: 'a' },
	{ id: 'remote:origin/plan-n', kind: 'remote' as const, label: 'origin/plan-n', slug: 'n' }
];

function repository(withOverlay = true): RepositoryDataSource {
	const listing = (files: Record<string, string>, root: string) => ({
		items: Object.keys(files)
			.filter((path) => path.startsWith(`${root}/`))
			.map((path) => ({ name: path.split('/').at(-1)!, path, type: 'blob' }))
	});
	const source: RepositoryDataSource = {
		info: async () => ({ default_branch: 'main' }),
		tree: vi.fn(async (path: string) => listing(checkout, path)),
		treeRecursive: vi.fn(async (path: string) => listing(checkout, path)),
		blob: vi.fn(async (path: string) => ({ path, content: checkout[path], encoding: 'utf-8' }))
	};
	if (withOverlay) {
		source.planningProposals = vi.fn(async () => ({
			sources,
			items: [
				{
					source: 'worktree:plan-a',
					path: 'docs/proposals/PROP-a/proposal.md',
					content: planned['docs/proposals/PROP-a/proposal.md'],
					encoding: 'utf-8'
				},
				{
					source: 'remote:origin/plan-n',
					path: 'docs/proposals/PROP-n/proposal.md',
					content: planned['docs/proposals/PROP-n/proposal.md'],
					encoding: 'utf-8'
				}
			],
			errors: []
		}));
		source.planningTree = vi.fn(async (planning: string, path: string) =>
			listing(
				Object.fromEntries(
					Object.entries(planned).filter(([file]) =>
						file.startsWith(`docs/proposals/PROP-${planning.split('plan-')[1]}/`)
					)
				),
				path
			)
		);
		source.planningBlob = vi.fn(async (_planning: string, path: string) => ({
			path,
			content: planned[path],
			encoding: 'utf-8'
		}));
	}
	return source;
}

const props = (source: RepositoryDataSource, requestedPath = '') => ({
	view: 'proposals' as const,
	source,
	branch: 'main',
	theme: 'dark',
	requestedPath,
	requestedAnchor: '',
	onOpen: vi.fn(),
	onLocation: vi.fn(),
	diagrams: () => ({ destroy() {} })
});

beforeEach(() => {
	// jsdom implements neither; the tests assert content, not scrolling.
	Element.prototype.scrollIntoView = vi.fn();
	vi.stubGlobal(
		'IntersectionObserver',
		class {
			observe() {}
			disconnect() {}
		}
	);
});
afterEach(() => {
	cleanup();
	vi.unstubAllGlobals();
});

describe('KnowledgeViews Planning overlay', () => {
	it('lists overlaid proposals with their source and reads their bundle from it', async () => {
		const source = repository();
		const view = props(source);
		render(KnowledgeViews, view);
		await screen.findByText('Planned A');
		expect(screen.queryByText('Checkout A')).toBeNull();
		expect(screen.getByText('Checkout B')).toBeTruthy();
		expect(screen.getByText('Planned only')).toBeTruthy();
		expect(screen.getAllByText('worktree plan-a')).toHaveLength(1);
		expect(screen.getByText('origin/plan-n')).toBeTruthy();
		const entries = [...document.querySelectorAll('.entry strong')].map((e) => e.textContent);
		expect(entries).toEqual(['Planned A', 'Checkout B', 'Planned only']);

		await fireEvent.click(screen.getByText('Planned A'));
		await screen.findByRole('button', { name: 'materials/notes.md' });
		expect(source.planningTree).toHaveBeenCalledWith(
			'worktree:plan-a',
			'docs/proposals/PROP-a',
			expect.anything()
		);
		expect(screen.queryByRole('button', { name: 'View raw' })).toBeNull();
		expect(screen.getAllByText('worktree plan-a').length).toBeGreaterThan(1);
		await fireEvent.click(screen.getByRole('button', { name: 'materials/notes.md' }));
		await screen.findByText('Untracked material.');
		expect(
			vi
				.mocked(source.blob)
				.mock.calls.filter(([path]) => path.startsWith('docs/proposals/PROP-a/'))
		).toHaveLength(1);

		await fireEvent.click(screen.getByText('Checkout B'));
		await screen.findByRole('button', { name: 'View raw' });
	});

	it('opens a Planning-only proposal requested before the overlay arrives', async () => {
		let release!: () => void;
		const pending = new Promise<void>((resolve) => (release = resolve));
		const source = repository();
		const original = source.planningProposals!;
		source.planningProposals = vi.fn(async (signal: AbortSignal) => {
			await pending;
			return original(signal);
		});
		render(KnowledgeViews, props(source, 'docs/proposals/PROP-n/proposal.md'));
		await screen.findByText('Checkout B');
		release();
		await waitFor(() =>
			expect(document.querySelector('.bundle-header h1')?.textContent).toBe('Planned only')
		);
	});

	it('shows the checkout only for a host without the overlay', async () => {
		const source = repository(false);
		render(KnowledgeViews, props(source));
		await screen.findByText('Checkout A');
		expect(screen.queryByText('worktree plan-a')).toBeNull();
	});
});
