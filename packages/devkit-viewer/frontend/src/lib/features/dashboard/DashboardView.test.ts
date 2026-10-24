import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { afterEach, describe, expect, it, vi } from 'vitest';
import DashboardView from './DashboardView.svelte';
import type { RepositoryDataSource } from '../../api/repository';

describe('DashboardView', () => {
	afterEach(() => {
		cleanup();
	});

	function mockSource(): RepositoryDataSource {
		return {
			info: vi.fn(async () => ({ default_branch: 'main' })),
			tree: vi.fn(async (path: string) => {
				if (path === 'docs') {
					return {
						items: [
							{ name: 'roadmap', path: 'docs/roadmap', type: 'tree' },
							{ name: 'proposals', path: 'docs/proposals', type: 'tree' }
						]
					};
				}
				if (path === 'docs/roadmap') {
					return {
						items: [{ name: 'MS-core.md', path: 'docs/roadmap/MS-core.md', type: 'blob' }]
					};
				}
				if (path === 'docs/proposals') {
					return {
						items: [{ name: 'PROP-test', path: 'docs/proposals/PROP-test', type: 'tree' }]
					};
				}
				if (path === 'docs/proposals/PROP-test') {
					return {
						items: [
							{
								name: 'proposal.md',
								path: 'docs/proposals/PROP-test/proposal.md',
								type: 'blob'
							}
						]
					};
				}
				if (path === 'specs') {
					return {
						items: [{ name: '2026-10', path: 'specs/2026-10', type: 'tree' }]
					};
				}
				if (path === 'specs/2026-10') {
					return {
						items: [{ name: 'unit-a', path: 'specs/2026-10/unit-a', type: 'tree' }]
					};
				}
				if (path === 'specs/2026-10/unit-a') {
					return {
						items: [{ name: 'feedback', path: 'specs/2026-10/unit-a/feedback', type: 'tree' }]
					};
				}
				if (path === 'specs/2026-10/unit-a/feedback') {
					return {
						items: [
							{
								name: 'fb-issue.md',
								path: 'specs/2026-10/unit-a/feedback/fb-issue.md',
								type: 'blob'
							}
						]
					};
				}
				return { items: [] };
			}),
			blob: vi.fn(async (path: string) => {
				if (path === 'docs/roadmap/MS-core.md') {
					return {
						path,
						encoding: 'utf-8',
						content:
							'---\nid: MS-core\ntitle: Core System\nstatus: active\nsummary: Core system architecture\n---\n# MS-core\nDetailed exit conditions.'
					};
				}
				if (path === 'docs/proposals/PROP-test/proposal.md') {
					return {
						path,
						encoding: 'utf-8',
						content:
							'---\nid: PROP-test\ntitle: Test Proposal\nstatus: draft\ntask_kind: feature\nplanning_effort: medium\ndev_effort: low\n---\n# PROP-test\nSummary of test proposal.'
					};
				}
				if (path === 'specs/2026-10/unit-a/feedback/fb-issue.md') {
					return {
						path,
						encoding: 'utf-8',
						content:
							'---\nid: FB-issue\ntitle: CLI Issue\nstatus: open\nseverity: critical\ntarget: cli.py\n---\n# FB-issue\nContext: CLI argument parsing fails.'
					};
				}
				return { path, encoding: 'utf-8', content: '' };
			}),
			refs: vi.fn(async () => ({
				default_branch: 'main',
				branches: ['main', 'dev-feature-x', 'plan-proposal-y']
			}))
		};
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
		expect(source.refs).not.toHaveBeenCalled();
		expect(screen.queryByText('dev-feature-x')).toBeNull();
		expect(screen.queryByText('plan-proposal-y')).toBeNull();

		// Check AI invisible guide section
		const aiSection = document.querySelector(
			'section[aria-label="AI Assistant Instructions and SDD Dashboard Guide"]'
		);
		expect(aiSection).not.toBeNull();
		expect(aiSection?.textContent).toContain('Project SDD Dashboard');
		expect(aiSection?.textContent).toContain('uv run devkit spec list');
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
	it('publishes fast sections independently, reuses cache on remount and refreshes', async () => {
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
		expect(source.blob).toHaveBeenCalledTimes(calls);
		await fireEvent.click(screen.getByText('Refresh'));
		await waitFor(() => expect(source.blob).toHaveBeenCalledTimes(calls * 2));
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
	it('loads pages on demand, retries without losing cards and restores expanded pages', async () => {
		const entries = Array.from({ length: 15 }, (_, i) => ({
			path: `specs/month/unit/feedback/${String(i).padStart(2, '0')}.md`,
			encoding: 'utf-8',
			content: `---\nid: FB-${i}\ntitle: Issue ${i}\nstatus: open\nseverity: friction\n---\n`
		}));
		const source = mockSource();
		source.dashboardList = vi.fn(async (section) => ({
			items: section === 'feedback' ? entries : [],
			errors: []
		}));
		source.blob = vi.fn(async (path) => ({
			path,
			encoding: 'utf-8',
			content: entries.find((e) => e.path === path)!.content + 'Summary'
		}));
		const props = { source, branch: 'main' };
		const view = render(DashboardView, { props });
		const cards = () => screen.getAllByRole('heading', { level: 3, name: /^Issue / });
		await waitFor(() => expect(cards()).toHaveLength(6));
		expect(source.blob).toHaveBeenCalledTimes(6);
		vi.mocked(source.blob).mockRejectedValueOnce(new Error('page failure'));
		await fireEvent.click(screen.getByRole('button', { name: 'Load more' }));
		await waitFor(() => expect(screen.getByRole('button', { name: 'Retry' })).toBeTruthy());
		expect(cards()).toHaveLength(6);
		await fireEvent.click(screen.getByRole('button', { name: 'Retry' }));
		await waitFor(() => expect(cards()).toHaveLength(12));
		const calls = vi.mocked(source.blob).mock.calls.length;
		view.unmount();
		render(DashboardView, { props });
		await waitFor(() => expect(cards()).toHaveLength(12));
		expect(source.blob).toHaveBeenCalledTimes(calls);
		expect(source.dashboardList).toHaveBeenCalledTimes(3);
		await fireEvent.click(screen.getByRole('button', { name: 'Refresh' }));
		await waitFor(() => expect(cards()).toHaveLength(6));
		expect(source.blob).toHaveBeenCalledTimes(calls + 6);
	});
});
