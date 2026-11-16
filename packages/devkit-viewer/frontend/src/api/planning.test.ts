import { afterEach, describe, expect, it, vi } from 'vitest';
import { loadPlanningBundle, loadPlanningOverlay, type OverlayEntry } from './planning';
import { httpDataSource, type PlanningProposals } from './repository';
import { testSource } from '../testing/source';

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
			// An item of no reported source never overlays.
			{
				source: 'branch:plan-z',
				path: 'docs/proposals/PROP-z/proposal.md',
				content: header('PROP-z', 'draft'),
				encoding: 'utf-8'
			}
		],
		errors: [],
		...extra
	};
}

function host(result: () => Promise<PlanningProposals>) {
	return testSource({
		tree: vi.fn(async () => []),
		blob: vi.fn(async () => ({ path: '', content: '', encoding: 'utf-8' })),
		planningProposals: vi.fn(result),
		planningTree: vi.fn(async (_source: string, _path: string) => ({ items: [] as any[] })),
		planningBlob: vi.fn(async (_source: string, path: string) => ({
			path,
			content: '',
			encoding: 'utf-8'
		}))
	});
}

afterEach(() => vi.unstubAllGlobals());

describe('Planning overlay', () => {
	it('keeps only each source’s own proposal and asks again on every load', async () => {
		const source = host(async () => answer());
		const overlay = await loadPlanningOverlay(source, signal());
		expect(Object.keys(overlay.entries)).toEqual(['docs/proposals/PROP-a/proposal.md']);
		expect(overlay.entries['docs/proposals/PROP-a/proposal.md'].source.label).toBe(
			'worktree plan-a'
		);
		expect(await loadPlanningOverlay(source, signal())).not.toBe(overlay);
		expect(source.planningProposals).toHaveBeenCalledTimes(2);
	});

	it('reports unreadable items and keeps the readable ones', async () => {
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
		const overlay = await loadPlanningOverlay(source, signal());
		expect(overlay.errors).toHaveLength(2);
		expect(Object.keys(overlay.entries)).toEqual(['docs/proposals/PROP-a/proposal.md']);
	});

	it('reads an overlaid bundle from its own source only', async () => {
		const files: Record<string, string> = {
			'docs/proposals/PROP-a/proposal.md': header('PROP-a', 'review'),
			'docs/proposals/PROP-a/materials/notes.md': '# Notes'
		};
		const source = host(async () => answer());
		source.planningTree.mockImplementation(async (_source, path) => ({
			items: Object.keys(files)
				.filter((file) => file.startsWith(`${path}/`))
				.map((file) => ({ name: file.split('/').at(-1)!, path: file, type: 'blob' }))
		}));
		source.planningBlob.mockImplementation(async (_source, path) => ({
			path,
			content: files[path],
			encoding: 'utf-8'
		}));
		const overlay = await loadPlanningOverlay(source, signal());
		const entry: OverlayEntry = overlay.entries['docs/proposals/PROP-a/proposal.md'];
		const bundle = await loadPlanningBundle(source, entry, signal());
		expect(bundle.documents.map((doc) => doc.path)).toEqual(Object.keys(files).sort());
		expect(source.planningTree).toHaveBeenCalledWith(
			'worktree:plan-a',
			'docs/proposals/PROP-a',
			expect.anything()
		);
		expect(source.planningBlob.mock.calls.every((c) => c[0] === 'worktree:plan-a')).toBe(true);
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
		await source.planningProposals(signal());
		await source.planningTree('branch:plan-c', 'docs/proposals/PROP-c', signal());
		await source.planningBlob('branch:plan-b', 'docs/proposals/PROP-b/proposal.md', signal());
		await source.blob('docs/proposals/PROP-b/proposal.md', signal());
		expect(urls).toEqual([
			'/api/repos/r/planning-proposals',
			'/api/repos/r/tree?path=docs%2Fproposals%2FPROP-c&recursive=true&source=branch%3Aplan-c',
			'/api/repos/r/blob?path=docs%2Fproposals%2FPROP-b%2Fproposal.md&source=branch%3Aplan-b',
			'/api/repos/r/blob?path=docs%2Fproposals%2FPROP-b%2Fproposal.md'
		]);
	});
});
