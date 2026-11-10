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

describe('Read decision supersession', () => {
	function decisions(): RepositoryDataSource {
		const files: Record<string, string> = {
			'docs/packages/a/decisions/old.md':
				'---\nid: ADR-old\ntitle: Old decision\nstatus: accepted\n---\n# Old decision',
			'docs/packages/b/decisions/new.md':
				'---\nid: ADR-new\ntitle: New decision\nstatus: accepted\nsupersedes: ADR-old\n---\n# New decision\n\nSupersedes in part `ADR-old`: old clause.'
		};
		const listing = (root: string) => ({
			items: Object.keys(files)
				.filter((path) => path.startsWith(`${root}/`))
				.map((path) => ({ path, name: path.split('/').at(-1)!, type: 'blob' }))
		});
		return {
			info: async () => ({ default_branch: 'main' }),
			tree: vi.fn(async (root) => listing(root)),
			treeRecursive: vi.fn(async (root) => listing(root)),
			blob: vi.fn(async (path) => ({ path, content: files[path], encoding: 'utf-8' }))
		};
	}
	it('reuses its index and reveals cross-namespace related decisions in Read', async () => {
		const source = decisions(),
			onOpen = vi.fn();
		render(KnowledgeViews, { ...props(source), view: 'book', bookRequested: true, onOpen });
		await screen.findAllByText('old clause.');
		expect(document.querySelector('section.chapter header .decision-status')?.textContent).toBe(
			'accepted'
		);
		expect(source.treeRecursive).toHaveBeenCalledTimes(2);
		await fireEvent.change(screen.getByRole('combobox', { name: 'Scope' }), {
			target: { value: 'a' }
		});
		expect(document.querySelectorAll('section.chapter')).toHaveLength(1);
		await fireEvent.click(screen.getByRole('link', { name: /ADR-new — New decision/ }));
		await waitFor(() => expect(document.querySelectorAll('section.chapter')).toHaveLength(2));
		expect(onOpen).not.toHaveBeenCalled();
		expect(source.treeRecursive).toHaveBeenCalledTimes(2);
	});
	it('labels a Planning PADR proposed and opens checkout target via Files callback', async () => {
		const source = decisions();
		const proposal =
			'---\nid: PROP-test\ntitle: Test proposal\nstatus: reviewing\n---\n# Test proposal';
		const padr =
			'---\nid: PADR-test\ntitle: Test decision\nstatus: draft\nsupersedes: ADR-old\n---\nSupersedes in part `ADR-old`: proposed scope.';
		source.planningProposals = vi.fn(async () => ({
			sources: [
				{
					id: 'worktree:plan-test',
					kind: 'worktree' as const,
					label: 'worktree plan-test',
					slug: 'test'
				}
			],
			items: [
				{
					source: 'worktree:plan-test',
					path: 'docs/proposals/PROP-test/proposal.md',
					content: proposal,
					encoding: 'utf-8'
				}
			],
			errors: []
		}));
		source.planningTree = vi.fn(async () => ({
			items: [
				{ path: 'docs/proposals/PROP-test/proposal.md', name: 'proposal.md', type: 'blob' },
				{
					path: 'docs/proposals/PROP-test/decisions/PADR-test.md',
					name: 'PADR-test.md',
					type: 'blob'
				}
			]
		}));
		source.planningBlob = vi.fn(async (_source, path) => ({
			path,
			content: path.endsWith('proposal.md') ? proposal : padr,
			encoding: 'utf-8'
		}));
		const onOpen = vi.fn();
		render(KnowledgeViews, { ...props(source), onOpen });
		await fireEvent.click(await screen.findByText('Test proposal'));
		await fireEvent.click(await screen.findByRole('button', { name: 'decisions/PADR-test.md' }));
		await screen.findByText('Proposed supersession');
		expect(document.querySelector('section.chapter header .decision-status')?.textContent).toBe(
			'draft'
		);
		expect(document.querySelector('.source-badge')?.textContent).toBe('worktree plan-test');
		await fireEvent.click(screen.getByRole('link', { name: /ADR-old — Old decision/ }));
		expect(onOpen).toHaveBeenCalledWith('docs/packages/a/decisions/old.md');
	});
});

it('Read relation reload refreshes peers while retaining each displayed subject body', async () => {
	let scope = 'initial scope';
	const files = () => ({
		'docs/decisions/old.md':
			'---\nid: ADR-old\ntitle: Earlier\nstatus: accepted\n---\n# Earlier body',
		'docs/decisions/new.md': `---\nid: ADR-new\ntitle: Later\nstatus: accepted\nsupersedes: ADR-old\n---\n# Later body\n\nSupersedes in part \`ADR-old\`: ${scope}`
	});
	const listing = (root: string) => ({
		items: Object.keys(files())
			.filter((path) => path.startsWith(`${root}/`))
			.map((path) => ({ path, name: path.split('/').at(-1)!, type: 'blob' }))
	});
	const source: RepositoryDataSource = {
		info: async () => ({ default_branch: 'main' }),
		tree: async (root) => listing(root),
		treeRecursive: async (root) => listing(root),
		blob: async (path) => ({
			path,
			content: files()[path as keyof ReturnType<typeof files>],
			encoding: 'utf-8'
		})
	};
	render(KnowledgeViews, { ...props(source), view: 'book', bookRequested: true });
	await screen.findAllByText('initial scope');
	scope = 'refreshed peer scope';
	const earlier = document.getElementById('doc-docs%2Fdecisions%2Fold.md')!;
	await fireEvent.click(
		earlier.querySelector('button')!.textContent === 'Reload relations'
			? earlier.querySelector('button')!
			: [...earlier.querySelectorAll('button')].find(
					(button) => button.textContent === 'Reload relations'
				)!
	);
	await waitFor(() =>
		expect(earlier.querySelector('.replacement-text')?.textContent).toBe('refreshed peer scope')
	);
	expect(
		document.getElementById('doc-docs%2Fdecisions%2Fnew.md')!.querySelector('.markdown-body')
			?.textContent
	).toContain('initial scope');
	expect(
		document.getElementById('doc-docs%2Fdecisions%2Fnew.md')!.querySelector('.replacement-text')
			?.textContent
	).toBe('initial scope');
});

it('Read relation navigation refreshes the selected target body and subject input together', async () => {
	let scope = 'original scope';
	const files = () => ({
		'docs/decisions/old.md':
			'---\nid: ADR-old\ntitle: Earlier\nstatus: accepted\n---\n# Earlier body',
		'docs/decisions/new.md': `---\nid: ADR-new\ntitle: Later\nstatus: accepted\nsupersedes: ADR-old\n---\n# Later body\n\nSupersedes in part \`ADR-old\`: ${scope}`
	});
	const listing = (root: string) => ({
		items: Object.keys(files())
			.filter((path) => path.startsWith(`${root}/`))
			.map((path) => ({ path, name: path.split('/').at(-1)!, type: 'blob' }))
	});
	const source: RepositoryDataSource = {
		info: async () => ({ default_branch: 'main' }),
		tree: async (root) => listing(root),
		treeRecursive: async (root) => listing(root),
		blob: async (path) => ({
			path,
			content: files()[path as keyof ReturnType<typeof files>],
			encoding: 'utf-8'
		})
	};
	render(KnowledgeViews, { ...props(source), view: 'book', bookRequested: true });
	await screen.findAllByText('original scope');
	const earlier = document.getElementById('doc-docs%2Fdecisions%2Fold.md')!;
	scope = 'updated scope';
	await fireEvent.click(
		[...earlier.querySelectorAll('button')].find(
			(button) => button.textContent === 'Reload relations'
		)!
	);
	await waitFor(() =>
		expect(earlier.querySelector('.replacement-text')?.textContent).toBe('updated scope')
	);
	await fireEvent.click(earlier.querySelector('.relation-row a')!);
	const later = document.getElementById('doc-docs%2Fdecisions%2Fnew.md')!;
	await waitFor(() =>
		expect(later.querySelector('.markdown-body')?.textContent).toContain('updated scope')
	);
	expect(later.querySelector('.replacement-text')?.textContent).toBe('updated scope');
});
