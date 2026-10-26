import { afterEach, describe, expect, it, vi } from 'vitest';
import {
	appliedOverlay,
	cachedOverlay,
	loadPlanningBundle,
	loadPlanningOverlay,
	type OverlayEntry
} from './planning';
import { clearRepositoryCache } from './cache';
import { httpDataSource, type PlanningProposals, type RepositoryDataSource } from './repository';

const signal = () => new AbortController().signal;
const worktree = { id: 'worktree:plan-a', kind: 'worktree', label: 'worktree plan-a', slug: 'a' };
const branch = { id: 'branch:plan-b', kind: 'branch', label: 'plan-b', slug: 'b' };
const header = (id: string, status: string) =>
	`---\nid: ${id}\ntitle: ${id} planned\nstatus: ${status}\n---\n# ${id}\n`;

function answer(extra: Partial<PlanningProposals> = {}): PlanningProposals {
	return {
		sources: [worktree, branch] as PlanningProposals['sources'],
		items: [
			{
				source: 'worktree:plan-a',
				path: 'docs/proposals/PROP-a/proposal.md',
				content: header('PROP-a', 'review'),
				encoding: 'utf-8'
			},
			// Another proposal on the same branch is a stale copy and never overlays.
			{
				source: 'worktree:plan-a',
				path: 'docs/proposals/PROP-b/proposal.md',
				content: header('PROP-b', 'review'),
				encoding: 'utf-8'
			},
			{
				source: 'remote:origin/plan-z',
				path: 'docs/proposals/PROP-z/proposal.md',
				content: header('PROP-z', 'draft'),
				encoding: 'utf-8'
			}
		],
		errors: [],
		...extra
	};
}

function host(result: () => Promise<PlanningProposals>): RepositoryDataSource {
	return {
		info: async () => ({}),
		tree: vi.fn(async () => []),
		blob: vi.fn(async () => ({ path: '', content: '', encoding: 'utf-8' })),
		planningProposals: vi.fn(result)
	};
}

afterEach(() => vi.unstubAllGlobals());

describe('Planning overlay', () => {
	it('keeps only each source’s own proposal and caches the result', async () => {
		const source = host(async () => answer());
		const overlay = await loadPlanningOverlay(source, 'main', signal());
		expect(Object.keys(overlay!.entries)).toEqual(['docs/proposals/PROP-a/proposal.md']);
		expect(overlay!.entries['docs/proposals/PROP-a/proposal.md'].source.label).toBe(
			'worktree plan-a'
		);
		expect(await loadPlanningOverlay(source, 'main', signal())).toBe(overlay);
		expect(source.planningProposals).toHaveBeenCalledTimes(1);
		expect(appliedOverlay(source, 'main')).toBe(overlay);
	});

	it('reports unreadable items without caching and keeps the readable ones applied', async () => {
		const source = host(async () =>
			answer({
				items: [
					{
						source: 'branch:plan-b',
						path: 'docs/proposals/PROP-b/proposal.md',
						content: '---\n: [\n---\n',
						encoding: 'utf-8'
					},
					answer().items[0]
				],
				errors: ['git cat-file: failed']
			})
		);
		const overlay = await loadPlanningOverlay(source, 'main', signal());
		expect(overlay!.errors).toHaveLength(2);
		expect(Object.keys(overlay!.entries)).toEqual(['docs/proposals/PROP-a/proposal.md']);
		expect(cachedOverlay(source, 'main')).toBeUndefined();
		expect(appliedOverlay(source, 'main')).toBe(overlay);
	});

	it('neither caches nor applies aborted or refreshed work', async () => {
		let release!: () => void;
		const slow = new Promise<void>((resolve) => (release = resolve));
		const source = host(async () => {
			await slow;
			return answer();
		});
		const controller = new AbortController();
		const aborted = loadPlanningOverlay(source, 'main', controller.signal);
		controller.abort();
		const refreshed = loadPlanningOverlay(source, 'other', signal());
		clearRepositoryCache(source);
		release();
		await Promise.all([aborted, refreshed]);
		expect(cachedOverlay(source, 'main')).toBeUndefined();
		expect(cachedOverlay(source, 'other')).toBeUndefined();
		expect(appliedOverlay(source, 'main')).toBeUndefined();
		expect(appliedOverlay(source, 'other')).toBeUndefined();
	});

	it('is absent for a host without the overlay', async () => {
		const source = host(async () => answer());
		delete source.planningProposals;
		expect(await loadPlanningOverlay(source, 'main', signal())).toBeUndefined();
	});

	it('reads an overlaid bundle from its own source only', async () => {
		const files: Record<string, string> = {
			'docs/proposals/PROP-a/proposal.md': header('PROP-a', 'review'),
			'docs/proposals/PROP-a/materials/notes.md': '# Notes'
		};
		const source = host(async () => answer());
		source.planningTree = vi.fn(async (_source, path) => ({
			items: Object.keys(files)
				.filter((file) => file.startsWith(`${path}/`))
				.map((file) => ({ name: file.split('/').at(-1)!, path: file, type: 'blob' }))
		}));
		source.planningBlob = vi.fn(async (_source, path) => ({
			path,
			content: files[path],
			encoding: 'utf-8'
		}));
		const overlay = await loadPlanningOverlay(source, 'main', signal());
		const entry: OverlayEntry = overlay!.entries['docs/proposals/PROP-a/proposal.md'];
		const bundle = await loadPlanningBundle(source, entry, signal());
		expect(bundle.documents.map((doc) => doc.path)).toEqual(Object.keys(files).sort());
		expect(source.planningTree).toHaveBeenCalledWith(
			'worktree:plan-a',
			'docs/proposals/PROP-a',
			expect.anything()
		);
		expect(
			vi.mocked(source.planningBlob!).mock.calls.every((c) => c[0] === 'worktree:plan-a')
		).toBe(true);
		expect(source.tree).not.toHaveBeenCalled();
		expect(source.blob).not.toHaveBeenCalled();
	});

	it('sends the source only on the Planning endpoints', async () => {
		const urls: string[] = [];
		vi.stubGlobal(
			'fetch',
			vi.fn(async (url: string) => {
				urls.push(url);
				return new Response('{"items": []}');
			})
		);
		const source = httpDataSource('/api/repos/r');
		await source.planningProposals!(signal());
		await source.planningTree!('remote:origin/plan-c', 'docs/proposals/PROP-c', signal());
		await source.planningBlob!('branch:plan-b', 'docs/proposals/PROP-b/proposal.md', signal());
		await source.blob('docs/proposals/PROP-b/proposal.md', 'plan-b', signal());
		expect(urls).toEqual([
			'/api/repos/r/planning-proposals',
			'/api/repos/r/tree?path=docs%2Fproposals%2FPROP-c&recursive=true&source=remote%3Aorigin%2Fplan-c',
			'/api/repos/r/blob?path=docs%2Fproposals%2FPROP-b%2Fproposal.md&source=branch%3Aplan-b',
			'/api/repos/r/blob?path=docs%2Fproposals%2FPROP-b%2Fproposal.md'
		]);
	});
});
