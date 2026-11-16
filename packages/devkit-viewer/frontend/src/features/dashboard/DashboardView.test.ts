import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { afterEach, describe, expect, it, vi } from 'vitest';
import DashboardView from './DashboardView.svelte';
import type { RepositoryDataSource } from '../../api/repository';
import { testSource } from '../../testing/source';
import { cachedResult, cacheGeneration, cacheResult } from '../../api/cache';

describe('DashboardView', () => {
	afterEach(() => {
		cleanup();
	});

	const bodies: Record<string, string> = {
		'docs/roadmap/MS-core.md':
			'---\nid: MS-core\ntitle: Core System\nstatus: active\nsummary: Core system architecture\n---\n# MS-core\nDetailed exit conditions.',
		'docs/proposals/PROP-test/proposal.md':
			'---\nid: PROP-test\ntitle: Test Proposal\nstatus: draft\ntask_kind: feature\nplanning_effort: medium\ndev_effort: low\n---\n# PROP-test\nSummary of test proposal.',
		'specs/2026-10/unit-a/feedback/fb-issue.md':
			'---\nid: FB-issue\ntitle: CLI Issue\nstatus: open\nseverity: critical\ntarget: cli.py\n---\n# FB-issue\nContext: CLI argument parsing fails.'
	};
	const sectionOf = (path: string) =>
		path.includes('/roadmap/')
			? 'milestones'
			: path.includes('/proposals/')
				? 'proposals'
				: 'feedback';
	function mockSource() {
		return testSource({
			dashboardList: vi.fn(async (section: string, _signal: AbortSignal) => ({
				items: Object.entries(bodies)
					.filter(([path]) => sectionOf(path) === section)
					.map(([path, content]) => ({
						path,
						encoding: 'utf-8',
						content: content.slice(0, content.indexOf('\n---\n') + 5)
					})),
				errors: [] as string[]
			})),
			blob: vi.fn(async (path: string, _signal: AbortSignal) => ({
				path,
				encoding: 'utf-8',
				content: bodies[path] ?? ''
			}))
		});
	}

	it('renders overview stats and cards from indexed repository data', async () => {
		const source = mockSource();
		render(DashboardView, { props: { source, repoId: 'test-repo', branch: 'main' } });

		await waitFor(() => {
			expect(screen.getByText('Core System')).toBeTruthy();
		});

		expect(screen.getByText('Test Proposal')).toBeTruthy();
		await waitFor(() => expect(screen.getByText('CLI Issue')).toBeTruthy());
		expect(screen.getByText('Active Worktree Session')).toBeTruthy();

		// Check AI invisible guide section
		const aiSection = document.querySelector(
			'section[aria-label="AI Assistant Instructions and SDD Dashboard Guide"]'
		);
		expect(aiSection).not.toBeNull();
		expect(aiSection?.textContent).toContain('Project SDD Dashboard');
		expect(aiSection?.textContent).toContain('uv run devkit docs list');
	});

	it('calls onNavigate callback when clicking a card or action button', async () => {
		const source = mockSource();
		const onNavigate = vi.fn();
		render(DashboardView, {
			props: { source, repoId: 'test-repo', branch: 'main', onNavigate }
		});

		await waitFor(() => {
			expect(screen.getByText('Core System')).toBeTruthy();
		});

		await fireEvent.click(screen.getByText('Core System'));
		expect(onNavigate).toHaveBeenCalledWith('roadmap', undefined);

		await fireEvent.click(screen.getByText('Test Proposal'));
		expect(onNavigate).toHaveBeenCalledWith('proposals', 'docs/proposals/PROP-test/proposal.md');
	});
	it('publishes fast sections independently, reloads on remount and on Refresh', async () => {
		const source = mockSource();
		const original = source.blob;
		let release!: () => void;
		const slow = new Promise<void>((resolve) => {
			release = resolve;
		});
		source.blob = vi.fn(async (...args: Parameters<RepositoryDataSource['blob']>) => {
			if (args[0].includes('/feedback/')) await slow;
			return original(...args);
		});
		const props = { source, repoId: 'test', branch: 'main' };
		const view = render(DashboardView, { props });
		await waitFor(() => expect(screen.getByText('Core System')).toBeTruthy());
		expect(screen.getByText('Loading feedback…')).toBeTruthy();
		expect(screen.queryByText('No open feedback items found.')).toBeNull();
		release();
		await waitFor(() => expect(screen.getByText('CLI Issue')).toBeTruthy());
		const calls = vi.mocked(source.blob).mock.calls.length;
		view.unmount();
		render(DashboardView, { props });
		await waitFor(() => expect(screen.getByText('CLI Issue')).toBeTruthy());
		// The dashboard caches nothing: a new view lists and reads again.
		expect(source.blob).toHaveBeenCalledTimes(calls * 2);
		await fireEvent.click(screen.getByText('Refresh'));
		await waitFor(() => expect(source.blob).toHaveBeenCalledTimes(calls * 3));
		expect(source.dashboardList).toHaveBeenCalledTimes(9);
	});
	it('clears the source caches on Refresh', async () => {
		const source = mockSource();
		render(DashboardView, { props: { source, repoId: 'test', branch: 'main' } });
		await waitFor(() => expect(screen.getByText('CLI Issue')).toBeTruthy());
		cacheResult(
			source,
			'main',
			'documents',
			{ documents: [], errors: [] },
			cacheGeneration(source)
		);
		expect(cachedResult(source, 'main', 'documents')).toBeDefined();
		await fireEvent.click(screen.getByText('Refresh'));
		expect(cachedResult(source, 'main', 'documents')).toBeUndefined();
	});
	it('keeps errors local and ignores the old source after switching', async () => {
		const source = mockSource();
		const original = source.blob;
		let release!: () => void;
		const slow = new Promise<void>((resolve) => {
			release = resolve;
		});
		source.blob = vi.fn(async (...args: Parameters<RepositoryDataSource['blob']>) => {
			if (args[0].includes('/feedback/')) {
				await slow;
				throw new Error('old feedback failure');
			}
			return original(...args);
		});
		const view = render(DashboardView, { props: { source, branch: 'main' } });
		await waitFor(() => expect(screen.getByText('Core System')).toBeTruthy());
		const replacement = mockSource();
		replacement.blob = vi.fn(async () => {
			throw new Error('new source failure');
		});
		await view.rerender({ source: replacement, branch: 'other' });
		await waitFor(() => expect(screen.getAllByRole('alert').length).toBe(3));
		expect(screen.queryByText('Core System')).toBeNull();
		expect(screen.queryByText('No open milestones found.')).toBeNull();
		release();
		await waitFor(() =>
			expect(vi.mocked(source.blob).mock.settledResults.every((r) => r.type !== 'incomplete')).toBe(
				true
			)
		);
		expect(screen.queryByText(/old feedback failure/)).toBeNull();
	});
	it('shows every eligible card without paging and counts a failed read with its path', async () => {
		const entries = Array.from({ length: 15 }, (_, i) => ({
			path: `specs/month/unit/feedback/${String(i).padStart(2, '0')}.md`,
			encoding: 'utf-8',
			content: `---\nid: FB-${String(i).padStart(2, '0')}\ntitle: Issue ${i}\nstatus: open\nseverity: friction\n---\n`
		}));
		const source = mockSource();
		source.dashboardList.mockImplementation(async (section) => ({
			items: section === 'feedback' ? entries : [],
			errors: []
		}));
		source.blob.mockImplementation(async (path) => {
			if (path.endsWith('/07.md')) throw new Error('moved');
			return {
				path,
				encoding: 'utf-8',
				content: entries.find((e) => e.path === path)!.content + 'Summary'
			};
		});
		render(DashboardView, { props: { source, branch: 'main' } });
		const cards = () => screen.getAllByRole('heading', { level: 3, name: /^Issue / });
		await waitFor(() => expect(cards()).toHaveLength(14));
		expect(cards().map((card) => card.textContent)).toEqual(
			Array.from({ length: 15 }, (_, i) => `Issue ${i}`).filter((title) => title !== 'Issue 7')
		);
		expect(source.blob).toHaveBeenCalledTimes(15);
		expect(screen.queryByRole('button', { name: 'Load more' })).toBeNull();
		expect(screen.queryByRole('button', { name: 'Retry' })).toBeNull();
		expect(screen.getByRole('alert').textContent).toContain(
			'specs/month/unit/feedback/07.md: moved'
		);
		expect(document.querySelector('.count-badge-amber')?.textContent).toBe('15');
		await fireEvent.click(screen.getByRole('button', { name: 'Refresh' }));
		await waitFor(() => expect(source.blob).toHaveBeenCalledTimes(30));
		await waitFor(() => expect(cards()).toHaveLength(14));
	});
});

describe('DashboardView Planning overlay', () => {
	afterEach(() => cleanup());
	const checkout = ['a', 'b', 'c'].map((slug) => ({
		path: `docs/proposals/PROP-${slug}/proposal.md`,
		encoding: 'utf-8',
		content: `---\nid: PROP-${slug}\ntitle: Checkout ${slug}\nstatus: draft\n---\n`
	}));
	const planned = (slug: string, status: string) => ({
		source: `branch:plan-${slug}`,
		path: `docs/proposals/PROP-${slug}/proposal.md`,
		encoding: 'utf-8',
		content: `---\nid: PROP-${slug}\ntitle: Planned ${slug}\nstatus: ${status}\nsummary: From ${slug}\n---\n`
	});
	const answer = () => ({
		sources: ['c', 'new'].map((slug) => ({
			id: `branch:plan-${slug}`,
			kind: 'branch' as const,
			label: `plan-${slug}`,
			slug
		})),
		items: [planned('c', 'review'), planned('new', 'draft')],
		errors: []
	});
	function overlaySource(planning: () => Promise<ReturnType<typeof answer>>) {
		return testSource({
			dashboardList: vi.fn(async (section: string, _signal: AbortSignal) => ({
				items: section === 'proposals' ? checkout : [],
				errors: [] as string[]
			})),
			blob: vi.fn(async (path: string, _signal: AbortSignal) =>
				checkout.find((e) => e.path === path)!
			),
			planningProposals: vi.fn(planning)
		});
	}
	const titles = () =>
		[...document.querySelectorAll('h3.card-heading')]
			.map((h) => h.textContent)
			.filter((t) => t !== 'Active Worktree Session');

	it('renders checkout cards first and updates them in place without reordering', async () => {
		let release!: () => void;
		const pending = new Promise<void>((resolve) => (release = resolve));
		const source = overlaySource(async () => {
			await pending;
			return answer();
		});
		render(DashboardView, { props: { source, branch: 'main' } });
		await waitFor(() => expect(titles()).toEqual(['Checkout a', 'Checkout b', 'Checkout c']));
		expect(screen.getByText('Checking Planning sources…')).toBeTruthy();
		expect(screen.getByText(/3 active\/draft out of 3 total/)).toBeTruthy();
		release();
		await waitFor(() =>
			expect(titles()).toEqual(['Checkout a', 'Checkout b', 'Planned c', 'Planned new'])
		);
		expect(screen.getByText('plan-c')).toBeTruthy();
		expect(screen.getByText('plan-new')).toBeTruthy();
		expect(screen.getByText(/4 active\/draft out of 4 total/)).toBeTruthy();
		expect(screen.queryByText('Checking Planning sources…')).toBeNull();
		expect(source.blob).toHaveBeenCalledTimes(3);

		// Refresh asks for the overlay again; the order stays the checkout's.
		await fireEvent.click(screen.getByText('Refresh'));
		await waitFor(() => expect(source.planningProposals).toHaveBeenCalledTimes(2));
		await waitFor(() => expect(source.blob).toHaveBeenCalledTimes(6));
		await waitFor(() =>
			expect(titles()).toEqual(['Checkout a', 'Checkout b', 'Planned c', 'Planned new'])
		);
	});

	it('keeps the checkout view when the overlay fails', async () => {
		const source = overlaySource(async () => {
			throw new Error('HTTP 500: boom');
		});
		render(DashboardView, { props: { source, branch: 'main' } });
		await waitFor(() =>
			expect(screen.getByText(/Planning overlay unavailable: HTTP 500: boom/)).toBeTruthy()
		);
		await waitFor(() => expect(titles()).toEqual(['Checkout a', 'Checkout b', 'Checkout c']));
		expect(screen.queryAllByRole('alert')).toHaveLength(0);
		expect(screen.getByText(/3 active\/draft out of 3 total/)).toBeTruthy();
	});

	it('appends Planning-only cards after every checkout card', async () => {
		const many = Array.from({ length: 10 }, (_, i) => ({
			path: `docs/proposals/PROP-${String(i).padStart(2, '0')}/proposal.md`,
			encoding: 'utf-8',
			content: `---\nid: PROP-${String(i).padStart(2, '0')}\ntitle: Checkout ${i}\nstatus: draft\n---\n`
		}));
		let release!: () => void;
		const pending = new Promise<void>((resolve) => (release = resolve));
		const source = overlaySource(async () => {
			await pending;
			return answer();
		});
		source.dashboardList.mockImplementation(async (section: string) => ({
			items: section === 'proposals' ? many : [],
			errors: []
		}));
		source.blob.mockImplementation(async (path: string) => many.find((e) => e.path === path)!);
		render(DashboardView, { props: { source, branch: 'main' } });
		await waitFor(() => expect(titles()).toHaveLength(10));
		release();
		await waitFor(() => expect(screen.queryByText('Checking Planning sources…')).toBeNull());
		await waitFor(() =>
			expect(titles().slice(-3)).toEqual(['Checkout 9', 'Planned c', 'Planned new'])
		);
		expect(titles()).toHaveLength(12);
		expect(screen.getByText(/12 active\/draft out of 12 total/)).toBeTruthy();
	});
});

describe('DashboardView overlay without cache', () => {
	afterEach(() => cleanup());
	it('asks for the overlay again when the view opens again', async () => {
		const checkout = [
			{
				path: 'docs/proposals/PROP-a/proposal.md',
				encoding: 'utf-8',
				content: '---\nid: PROP-a\ntitle: Checkout a\nstatus: draft\n---\n'
			}
		];
		const source = testSource({
			dashboardList: vi.fn(async (section: string, _signal: AbortSignal) => ({
				items: section === 'proposals' ? checkout : [],
				errors: [] as string[]
			})),
			blob: vi.fn(async (path: string, _signal: AbortSignal) =>
				checkout.find((e) => e.path === path)!
			),
			planningProposals: vi.fn(async () => ({ sources: [], items: [], errors: [] }))
		});
		const view = render(DashboardView, { props: { source, branch: 'main' } });
		await waitFor(() => expect(screen.getByText('Checkout a')).toBeTruthy());
		view.unmount();
		render(DashboardView, { props: { source, branch: 'main' } });
		await waitFor(() => expect(screen.getByText('Checkout a')).toBeTruthy());
		expect(source.planningProposals).toHaveBeenCalledTimes(2);
	});
});
