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
			})),
			sharedList: vi.fn(async () => ({
				artifacts: [
					{
						generation_id: 'gen-12345',
						kind: 'proposal-review',
						slug: 'test',
						source_sha: 'abcdef123456',
						language: 'ko',
						content_sha256: 'sha-hash',
						content_type: 'text/markdown',
						byte_count: 120,
						created_at: '2026-10-24T12:00:00Z',
						expires_at: '2026-10-31T12:00:00Z',
						revision: 'rev-1'
					}
				]
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
		expect(screen.getByText('CLI Issue')).toBeTruthy();
		expect(screen.getByText('Active Worktree Session')).toBeTruthy();

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
});

