import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import SddViewer from './SddViewer.svelte';
import type { RepositoryDataSource } from './repository';

const checkout: Record<string, string> = {
	'docs/proposals/PROP-a/proposal.md':
		'---\nid: PROP-a\ntitle: Checkout A\nstatus: draft\n---\n# A\n',
	'docs/proposals/PROP-b/proposal.md':
		'---\nid: PROP-b\ntitle: Checkout B\nstatus: draft\n---\n# B\n'
};
const planned = '---\nid: PROP-a\ntitle: Planned A\nstatus: review\n---\n# Planned A\n';

function repository(): RepositoryDataSource {
	const listing = (path: string) => ({
		items: Object.keys(checkout)
			.filter((file) => file.startsWith(`${path}/`))
			.map((file) => ({ name: file.split('/').at(-1)!, path: file, type: 'blob' }))
	});
	return {
		info: async () => ({ default_branch: 'main' }),
		tree: vi.fn(async (path: string) => listing(path)),
		treeRecursive: vi.fn(async (path: string) => listing(path)),
		blob: vi.fn(async (path: string) => ({ path, content: checkout[path], encoding: 'utf-8' })),
		dashboardList: vi.fn(async (section: string) => ({
			items:
				section === 'proposals'
					? Object.entries(checkout).map(([path, content]) => ({
							path,
							content,
							encoding: 'utf-8'
						}))
					: [],
			errors: []
		})),
		planningProposals: vi.fn(async () => ({
			sources: [
				{ id: 'worktree:plan-a', kind: 'worktree' as const, label: 'worktree plan-a', slug: 'a' }
			],
			items: [
				{
					source: 'worktree:plan-a',
					path: 'docs/proposals/PROP-a/proposal.md',
					content: planned,
					encoding: 'utf-8'
				}
			],
			errors: []
		})),
		planningTree: vi.fn(async () => ({
			items: [{ name: 'proposal.md', path: 'docs/proposals/PROP-a/proposal.md', type: 'blob' }]
		})),
		planningBlob: vi.fn(async (_source: string, path: string) => ({
			path,
			content: planned,
			encoding: 'utf-8'
		}))
	};
}

beforeEach(() => {
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

describe('SddViewer', () => {
	it('opens a Dashboard proposal card in the Proposals tab from the same source', async () => {
		const source = repository();
		render(SddViewer, {
			dataSource: source,
			repoId: 'repo',
			branch: 'main',
			initialView: 'dashboard'
		});
		await waitFor(() => expect(screen.getByText('worktree plan-a')).toBeTruthy());
		await fireEvent.click(screen.getByText('Planned A'));
		await waitFor(() =>
			expect(document.querySelector('.bundle-header h1')?.textContent).toBe('Planned A')
		);
		expect(source.planningTree).toHaveBeenCalledWith(
			'worktree:plan-a',
			'docs/proposals/PROP-a',
			expect.anything()
		);
		expect(source.planningProposals).toHaveBeenCalledTimes(1);
	});

	it('keeps a Dashboard card request in the Proposals tab', async () => {
		const source = repository();
		render(SddViewer, {
			dataSource: source,
			repoId: 'repo',
			branch: 'main',
			initialView: 'dashboard'
		});
		await waitFor(() => expect(screen.getByText('Checkout B')).toBeTruthy());
		await fireEvent.click(screen.getByText('Checkout B'));
		await waitFor(() =>
			expect(document.querySelector('.bundle-header h1')?.textContent).toBe('Checkout B')
		);
		await new Promise((resolve) => setTimeout(resolve, 20));
		await fireEvent.click(screen.getByRole('button', { name: 'Read' }));
		await new Promise((resolve) => setTimeout(resolve, 50));
		expect(screen.getByRole('button', { name: 'Read' }).getAttribute('aria-pressed')).toBe('true');
		expect(document.querySelector('.viewer-layout.hidden')).not.toBeNull();
	});

	it('opens the Files tab for initialView files and the Dashboard by default', async () => {
		const pressed = (name: string) =>
			screen.getByRole('button', { name }).getAttribute('aria-pressed');
		const view = render(SddViewer, {
			dataSource: repository(),
			repoId: 'repo',
			initialView: 'files'
		});
		expect(pressed('Files')).toBe('true');
		view.unmount();
		render(SddViewer, { dataSource: repository(), repoId: 'repo' });
		expect(pressed('Dashboard')).toBe('true');
	});

	it('labels the reading tab Read and keeps its book id', async () => {
		render(SddViewer, { dataSource: repository(), repoId: 'repo', initialView: 'dashboard' });
		const tab = screen.getByRole('button', { name: 'Read' });
		expect(tab.getAttribute('title')).toBe('Handbook and Living Spec book');
		expect(screen.queryByRole('button', { name: 'Book' })).toBeNull();
	});
});

describe('SddViewer reading tab', () => {
	const files: Record<string, string> = {
		'docs/a.md': '---\nid: CAP-a\ntitle: Contract A\n---\n# Contract A\n',
		'docs/b.md': '---\nid: CAP-b\ntitle: Contract B\n---\n# Contract B\n',
		'handbook/manifest.json': '{"tag": "v0.1.4", "langs": ["en", "ko"], "generated": "2026-10-26"}',
		'handbook/en/README.md': '# devkit handbook\n',
		'handbook/ko/README.md': '# devkit 핸드북\n',
		'handbook/ko/concepts.md': '---\ntitle: 개념\n---\n# 개념\n'
	};
	function reading(withHandbook = true) {
		const present = (path: string) =>
			(withHandbook || !path.startsWith('handbook/')) && path in files;
		const listing = (path: string) => ({
			items: Object.keys(files)
				.filter((file) => present(file) && file.startsWith(`${path}/`))
				.map((file) => ({ name: file.split('/').at(-1)!, path: file, type: 'blob' }))
		});
		return {
			info: async () => ({ default_branch: 'main' }),
			tree: vi.fn(async (path: string) => listing(path)),
			treeRecursive: vi.fn(async (path: string) => listing(path)),
			blob: vi.fn(async (path: string) => {
				if (!present(path)) throw new Error('HTTP 404: Not Found');
				return { path, content: files[path], encoding: 'utf-8' };
			}),
			dashboardList: vi.fn(async () => ({ items: [], errors: [] }))
		} satisfies RepositoryDataSource;
	}
	const chapters = () => document.querySelectorAll('section.chapter').length;
	const pageTitle = () => document.querySelector('.handbook-page h1')?.textContent;

	beforeEach(() => vi.stubGlobal('navigator', { languages: ['en'], language: 'en' }));
	afterEach(() => localStorage.clear());

	it('keeps the book request across a Dashboard visit and resets it with the branch', async () => {
		const source = reading(false);
		const view = render(SddViewer, { dataSource: source, repoId: 'repo', initialView: 'book' });
		await fireEvent.click(await screen.findByRole('button', { name: 'Living Spec book' }));
		await waitFor(() => expect(chapters()).toBe(2));
		await fireEvent.click(screen.getByRole('button', { name: 'Dashboard' }));
		await waitFor(() => expect(chapters()).toBe(0));
		await fireEvent.click(screen.getByRole('button', { name: 'Read' }));
		await waitFor(() => expect(chapters()).toBe(2));
		expect(screen.queryByRole('button', { name: 'Living Spec book' })).toBeNull();

		const scanned = source.treeRecursive.mock.calls.length + source.tree.mock.calls.length;
		await view.rerender({ dataSource: source, repoId: 'repo', initialView: 'book', branch: 'dev' });
		await screen.findByText(/This repository has no/);
		await new Promise((resolve) => setTimeout(resolve, 20));
		expect(chapters()).toBe(0);
		expect(source.treeRecursive.mock.calls.length + source.tree.mock.calls.length).toBe(scanned);
	});

	it('drops the book request without scanning when the data source changes', async () => {
		const first = reading(false);
		const view = render(SddViewer, { dataSource: first, repoId: 'repo', initialView: 'book' });
		await fireEvent.click(await screen.findByRole('button', { name: 'Living Spec book' }));
		await waitFor(() => expect(chapters()).toBe(2));
		const second = reading(false);
		await view.rerender({ dataSource: second, repoId: 'repo', initialView: 'book' });
		await screen.findByText(/This repository has no/);
		await new Promise((resolve) => setTimeout(resolve, 20));
		expect(chapters()).toBe(0);
		expect(second.tree).not.toHaveBeenCalled();
		expect(second.treeRecursive).not.toHaveBeenCalled();
		expect(second.blob.mock.calls.map(([path]) => path)).toEqual(['handbook/manifest.json']);
	});

	it('keeps the book request when a host later changes initialView', async () => {
		const source = reading(false);
		const view = render(SddViewer, { dataSource: source, repoId: 'repo', initialView: 'book' });
		await fireEvent.click(await screen.findByRole('button', { name: 'Living Spec book' }));
		await waitFor(() => expect(chapters()).toBe(2));
		await view.rerender({ dataSource: source, repoId: 'repo', initialView: 'proposals' });
		await waitFor(() =>
			expect(screen.getByRole('button', { name: 'Proposals' }).getAttribute('aria-pressed')).toBe(
				'true'
			)
		);
		await fireEvent.click(screen.getByRole('button', { name: 'Read' }));
		await waitFor(() => expect(chapters()).toBe(2));
	});

	it('treats a deep link to a docs/ file as the book request', async () => {
		const source = reading();
		render(SddViewer, {
			dataSource: source,
			repoId: 'repo',
			initialView: 'book',
			initialPath: 'docs/b.md'
		});
		await waitFor(() => expect(chapters()).toBe(2));
		await waitFor(() =>
			expect(vi.mocked(Element.prototype.scrollIntoView).mock.contexts.at(-1)).toBe(
				document.getElementById('doc-docs%2Fb.md')
			)
		);
		expect(source.blob.mock.calls.map(([path]) => path)).not.toContain('handbook/manifest.json');
	});

	it('opens the handbook for the default path and a requested handbook page', async () => {
		const source = reading();
		render(SddViewer, { dataSource: source, repoId: 'repo', initialView: 'book' });
		await waitFor(() => expect(pageTitle()).toBe('devkit handbook'));
		expect(chapters()).toBe(0);
		cleanup();

		const events: any[] = [];
		const listener = (event: Event) => events.push((event as CustomEvent).detail);
		document.addEventListener('sdd:path-change', listener);
		try {
			render(SddViewer, {
				dataSource: reading(),
				repoId: 'repo',
				initialView: 'book',
				initialPath: 'handbook/ko/concepts.md'
			});
			await waitFor(() => expect(pageTitle()).toBe('개념'));
			await waitFor(() =>
				expect(events.at(-1)).toMatchObject({
					path: 'handbook/ko/concepts.md',
					view: 'book',
					repoId: 'repo'
				})
			);
		} finally {
			document.removeEventListener('sdd:path-change', listener);
		}
	});
});
