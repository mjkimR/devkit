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
		await fireEvent.click(screen.getByRole('button', { name: 'Book' }));
		await new Promise((resolve) => setTimeout(resolve, 50));
		expect(screen.getByRole('button', { name: 'Book' }).getAttribute('aria-pressed')).toBe('true');
		expect(document.querySelector('.viewer-layout.hidden')).not.toBeNull();
	});
});
