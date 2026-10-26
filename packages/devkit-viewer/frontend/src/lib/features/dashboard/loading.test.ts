import { afterEach, describe, expect, it, vi } from 'vitest';
import {
	loadDashboardSection,
	openDashboardPage,
	nextDashboardPage,
	cachedDashboardPage
} from './loading';
import { indexDocuments, scanDocuments } from '../../api/documents';
import { cachedResult, cacheGeneration, cacheResult, clearRepositoryCache } from '../../api/cache';
import type { RepositoryDataSource } from '../../api/repository';
import { loadPlanningOverlay } from '../../api/planning';
const signal = () => new AbortController().signal;
function fixture(files: Record<string, string>): RepositoryDataSource {
	return {
		info: async () => ({}),
		tree: vi.fn(async (path: string) => {
			const names = new Map<string, string>();
			for (const file of Object.keys(files))
				if (file.startsWith(`${path}/`)) {
					const [name, ...rest] = file.slice(path.length + 1).split('/');
					names.set(name, rest.length ? 'tree' : 'blob');
				}
			return [...names].map(([name, type]) => ({ name, path: `${path}/${name}`, type }));
		}),
		blob: vi.fn(async (path: string) => ({ path, content: files[path], encoding: 'utf-8' }))
	};
}
const files = {
	'docs/roadmap/MS-a.md': '# Milestone',
	'docs/roadmap/README.md': '# Ignore',
	'docs/roadmap/sub/MS-b.md': '# Ignore nested milestone',
	'docs/proposals/PROP-a/proposal.md': '# Proposal',
	'docs/proposals/PROP-a/padrs/a.md': '# Ignore decision',
	'docs/proposals/PROP-a/feedback/a.md': '# Proposal feedback',
	'docs/materials/x/feedback/nested/a.md': '# Nested feedback',
	'docs/architecture/a.md': '# Ignore architecture',
	'specs/month/unit/spec.md': '# Ignore spec',
	'specs/month/unit/feedback/a.md': '# Unit feedback',
	'specs/month/unit/feedback/README.md': '# Ignore README'
};
afterEach(() => vi.useRealTimers());
describe('dashboard loading', () => {
	it('reads only matching blobs and preserves nested feedback', async () => {
		const source = fixture(files);
		const results = await Promise.all(
			(['milestones', 'proposals', 'feedback'] as const).map((s) =>
				loadDashboardSection(source, 'main', s, signal())
			)
		);
		expect(results.map((r) => r.documents.length)).toEqual([1, 1, 3]);
		expect(
			vi
				.mocked(source.blob)
				.mock.calls.map(([path]) => path)
				.sort()
		).toEqual(
			[
				'docs/roadmap/MS-a.md',
				'docs/proposals/PROP-a/proposal.md',
				'docs/proposals/PROP-a/feedback/a.md',
				'docs/materials/x/feedback/nested/a.md',
				'specs/month/unit/feedback/a.md'
			].sort()
		);
	});
	it('treats only missing optional roots as empty', async () => {
		const source = fixture({});
		source.tree = vi.fn(async () => {
			throw new Error('HTTP 404: Not Found');
		});
		expect((await loadDashboardSection(source, 'main', 'milestones', signal())).errors).toEqual([]);
		source.tree = vi.fn(async () => {
			throw new Error('HTTP 403: Forbidden');
		});
		expect(
			(await loadDashboardSection(source, 'other', 'milestones', signal())).errors
		).toHaveLength(1);
	});
	it('reuses results and retries on expiry, refresh, failure and abort', async () => {
		vi.useFakeTimers();
		const source = fixture(files);
		const load = (ref = 'main') => loadDashboardSection(source, ref, 'milestones', signal());
		await load();
		await load();
		expect(source.blob).toHaveBeenCalledTimes(1);
		await load('other');
		expect(source.blob).toHaveBeenCalledTimes(2);
		const other = fixture(files);
		await loadDashboardSection(other, 'main', 'milestones', signal());
		expect(other.blob).toHaveBeenCalledTimes(1);
		vi.advanceTimersByTime(30_000);
		await load();
		expect(source.blob).toHaveBeenCalledTimes(3);
		clearRepositoryCache(source);
		await load();
		expect(source.blob).toHaveBeenCalledTimes(4);
		clearRepositoryCache(source);
		vi.mocked(source.blob).mockRejectedValueOnce(new Error('unreadable'));
		expect((await load()).errors).toHaveLength(1);
		await load();
		expect(source.blob).toHaveBeenCalledTimes(6);
		clearRepositoryCache(source);
		const controller = new AbortController();
		const original = source.blob;
		source.blob = vi.fn(async (...args: Parameters<RepositoryDataSource['blob']>) => {
			controller.abort();
			return original(...args);
		});
		await loadDashboardSection(source, 'main', 'milestones', controller.signal);
		source.blob = original;
		await load();
		expect(original).toHaveBeenCalledTimes(8);
	});
	it('bounds cache entries and rejects writes from before refresh', () => {
		const source = fixture({});
		const generation = cacheGeneration(source);
		for (let i = 0; i < 9; i++) cacheResult(source, String(i), 'test', i, generation);
		expect(cachedResult(source, '0', 'test')).toBeUndefined();
		expect(cachedResult(source, '1', 'test')).toBe(1);
		clearRepositoryCache(source);
		cacheResult(source, 'main', 'test', 'old', generation);
		expect(cachedResult(source, 'main', 'test')).toBeUndefined();
	});
	it('reuses full indices for knowledge tab visits', async () => {
		const source = fixture(files);
		const first = await indexDocuments(source, 'main', signal());
		const count = vi.mocked(source.blob).mock.calls.length;
		expect(await indexDocuments(source, 'main', signal())).toBe(first);
		expect(source.blob).toHaveBeenCalledTimes(count);
	});
	it('refills workers before a slow request ends with at most six active requests', async () => {
		const source = fixture(
			Object.fromEntries(Array.from({ length: 12 }, (_, i) => [`docs/${i}.md`, '# A']))
		);
		const original = source.blob;
		let release!: () => void;
		const slow = new Promise<void>((resolve) => {
			release = resolve;
		});
		let active = 0,
			maximum = 0;
		source.blob = vi.fn(async (...args: Parameters<RepositoryDataSource['blob']>) => {
			maximum = Math.max(maximum, ++active);
			if (args[0] === 'docs/0.md') await slow;
			try {
				return await original(...args);
			} finally {
				active--;
			}
		});
		const work = scanDocuments(source, 'main', signal(), ['docs']);
		await vi.waitFor(() => expect(source.blob).toHaveBeenCalledTimes(12));
		expect(maximum).toBeLessThanOrEqual(6);
		release();
		expect((await work).documents).toHaveLength(12);
	});
	it('rejects cycles and out-of-scope paths', async () => {
		const source = fixture({});
		source.tree = vi.fn(async () => [
			{ path: 'docs/../secret.md', name: 'secret.md', type: 'blob' },
			{ path: 'elsewhere/a.md', name: 'a.md', type: 'blob' },
			{ path: 'docs', name: 'docs', type: 'tree' }
		]);
		expect((await scanDocuments(source, 'main', signal(), ['docs'])).documents).toEqual([]);
		expect(source.blob).not.toHaveBeenCalled();
	});
	it('uses two recursive metadata requests for local feedback and ignores hostile paths', async () => {
		const source = fixture(files);
		source.treeRecursive = vi.fn(async (root) => ({
			items: [
				...Object.keys(files)
					.filter((path) => path.startsWith(`${root}/`))
					.map((path) => ({ path, name: path.split('/').at(-1)!, type: 'blob' })),
				{ path: `${root}/../outside/feedback/secret.md`, name: 'secret.md', type: 'blob' }
			]
		}));
		const result = await loadDashboardSection(source, 'main', 'feedback', signal());
		expect(result.documents).toHaveLength(3);
		expect(source.treeRecursive).toHaveBeenCalledTimes(2);
		expect(source.tree).not.toHaveBeenCalled();
		expect(source.blob).toHaveBeenCalledTimes(3);
	});
});

describe('dashboard pages', () => {
	function pagedSource(count = 20) {
		const entries = Array.from({ length: count }, (_, i) => {
			const path = `specs/month/unit/feedback/${String(i).padStart(2, '0')}.md`;
			const header = `---\nid: FB-${String(i).padStart(2, '0')}\nstatus: ${i === 19 ? 'resolved' : 'open'}\nseverity: ${i === 12 ? 'critical' : 'friction'}\n---\n`;
			return { path, content: header, encoding: 'utf-8' };
		});
		const source = fixture(
			Object.fromEntries(entries.map((e) => [e.path, e.content + '# Body\nsummary']))
		);
		source.dashboardList = vi.fn(async () => ({ items: [...entries].reverse(), errors: [] }));
		return source;
	}
	it('fetches only each visible page in global severity/ID order and reuses all loaded pages', async () => {
		const source = pagedSource();
		const first = await openDashboardPage(source, 'main', 'feedback', signal());
		expect(first.paths).toHaveLength(19);
		expect(first.paths[0]).toContain('/12.md');
		expect(first.documents.map((d) => d.path)).toEqual(first.paths.slice(0, 6));
		expect(source.blob).toHaveBeenCalledTimes(6);
		expect(source.tree).not.toHaveBeenCalled();
		const next = await nextDashboardPage(source, 'main', 'feedback', first, signal());
		expect(next.documents.map((d) => d.path)).toEqual(first.paths.slice(0, 12));
		expect(source.blob).toHaveBeenCalledTimes(12);
		expect(await openDashboardPage(source, 'main', 'feedback', signal())).toBe(next);
		expect(source.dashboardList).toHaveBeenCalledTimes(1);
		expect(source.blob).toHaveBeenCalledTimes(12);
	});
	it('does not extend snapshot expiry on more pages and refresh rejects stale cache writes', async () => {
		vi.useFakeTimers();
		const source = pagedSource();
		const first = await openDashboardPage(source, 'main', 'feedback', signal());
		vi.advanceTimersByTime(20_000);
		const next = await nextDashboardPage(source, 'main', 'feedback', first, signal());
		expect(next.expires).toBe(first.expires);
		vi.advanceTimersByTime(10_000);
		await openDashboardPage(source, 'main', 'feedback', signal());
		expect(source.dashboardList).toHaveBeenCalledTimes(2);
		clearRepositoryCache(source);
		await nextDashboardPage(source, 'main', 'feedback', first, signal());
		expect(cachedDashboardPage(source, 'main', 'feedback')).toBeUndefined();
	});
	it('keeps existing cards and cursor on a failed page, permits retry and rejects aborted publication', async () => {
		const source = pagedSource();
		const first = await openDashboardPage(source, 'main', 'feedback', signal());
		vi.mocked(source.blob).mockRejectedValueOnce(new Error('unreadable'));
		const failed = await nextDashboardPage(source, 'main', 'feedback', first, signal());
		expect(failed.documents).toBe(first.documents);
		expect(failed.errors).toHaveLength(1);
		const retry = await nextDashboardPage(source, 'main', 'feedback', failed, signal());
		expect(retry.documents.map((d) => d.path)).toEqual(first.paths.slice(0, 12));
		expect(retry.errors).toEqual([]);
		clearRepositoryCache(source);
		const abort = new AbortController();
		abort.abort();
		const cancelled = await nextDashboardPage(source, 'main', 'feedback', retry, abort.signal);
		expect(cancelled.documents).toBe(retry.documents);
		expect(cachedDashboardPage(source, 'main', 'feedback')).toBeUndefined();
	});
	it('uses path tie-breakers, ignores hostile entries, and retains legacy hosts', async () => {
		const source = pagedSource(2);
		source.dashboardList = vi.fn(async () => ({
			items: [
				{ path: 'specs/a/feedback/z.md', content: '---\nid: FB-same\n---\n', encoding: 'utf-8' },
				{ path: 'specs/a/feedback/a.md', content: '---\nid: FB-same\n---\n', encoding: 'utf-8' },
				{ path: 'specs/../feedback/private.md', content: '', encoding: 'utf-8' }
			],
			errors: []
		}));
		source.blob = vi.fn(async (path) => ({ path, content: '# Body', encoding: 'utf-8' }));
		const result = await openDashboardPage(source, 'main', 'feedback', signal());
		expect(result.errors).toEqual([]);
		expect(result.paths).toEqual(['specs/a/feedback/a.md', 'specs/a/feedback/z.md']);
		const legacy = fixture(files);
		expect(
			(await openDashboardPage(legacy, 'main', 'milestones', signal())).documents
		).toHaveLength(1);
	});
});

describe('page worker ordering', () => {
	it('keeps snapshot order with delayed bodies and at most six requests in flight', async () => {
		const entries = Array.from({ length: 12 }, (_, i) => ({
			path: `docs/proposals/PROP-${String(i).padStart(2, '0')}/proposal.md`,
			encoding: 'utf-8',
			content: `---\nid: PROP-${String(i).padStart(2, '0')}\nstatus: draft\n---\n`
		}));
		let release!: () => void;
		const slow = new Promise<void>((resolve) => {
			release = resolve;
		});
		let active = 0,
			maximum = 0;
		const source: RepositoryDataSource = {
			info: async () => ({}),
			tree: async () => [],
			dashboardList: async () => ({ items: entries, errors: [] }),
			blob: vi.fn(async (path) => {
				maximum = Math.max(maximum, ++active);
				if (path === entries[0].path) await slow;
				active--;
				return entries.find((e) => e.path === path)!;
			})
		};
		const work = openDashboardPage(source, 'main', 'proposals', signal());
		await vi.waitFor(() => expect(source.blob).toHaveBeenCalledTimes(9));
		expect(maximum).toBeLessThanOrEqual(6);
		release();
		const first = await work;
		expect(first.documents.map((d) => d.path)).toEqual(entries.slice(0, 9).map((e) => e.path));
		const last = await nextDashboardPage(source, 'main', 'proposals', first, signal());
		expect(last.documents.map((d) => d.path)).toEqual(entries.map((e) => e.path));
		expect(source.blob).toHaveBeenCalledTimes(12);
		clearRepositoryCache(source);
		const controller = new AbortController();
		source.blob = vi.fn(async (path) => {
			controller.abort();
			return entries.find((e) => e.path === path)!;
		});
		await openDashboardPage(source, 'main', 'proposals', controller.signal);
		expect(cachedDashboardPage(source, 'main', 'proposals')).toBeUndefined();
	});
});

describe('Planning overlay seed', () => {
	it('orders a rebuilt proposal list with the last applied overlay and skips seeded bodies', async () => {
		const entries = ['a', 'b', 'c'].map((slug) => ({
			path: `docs/proposals/PROP-${slug}/proposal.md`,
			encoding: 'utf-8',
			content: `---\nid: PROP-${slug}\nstatus: draft\n---\n`
		}));
		const planned = (slug: string, status: string) => ({
			source: `branch:plan-${slug}`,
			path: `docs/proposals/PROP-${slug}/proposal.md`,
			encoding: 'utf-8',
			content: `---\nid: PROP-${slug}\ntitle: planned ${slug}\nstatus: ${status}\n---\n`
		});
		const source: RepositoryDataSource = {
			info: async () => ({}),
			tree: async () => [],
			dashboardList: vi.fn(async () => ({ items: entries, errors: [] })),
			blob: vi.fn(async (path) => entries.find((e) => e.path === path)!),
			planningProposals: vi.fn(async () => ({
				sources: ['c', 'n'].map((slug) => ({
					id: `branch:plan-${slug}`,
					kind: 'branch' as const,
					label: `plan-${slug}`,
					slug
				})),
				items: [planned('c', 'review'), planned('n', 'draft')],
				errors: []
			}))
		};
		const first = await openDashboardPage(source, 'main', 'proposals', signal());
		expect(first.paths.map((p) => p.split('/')[2])).toEqual(['PROP-a', 'PROP-b', 'PROP-c']);
		expect(first.overlay).toBeUndefined();
		await loadPlanningOverlay(source, 'main', signal());
		clearRepositoryCache(source);
		const rebuilt = await openDashboardPage(source, 'main', 'proposals', signal());
		expect(rebuilt.paths.map((p) => p.split('/')[2])).toEqual([
			'PROP-c',
			'PROP-a',
			'PROP-b',
			'PROP-n'
		]);
		expect(rebuilt.documents.find((d) => d.path.includes('PROP-c'))!.title).toBe('planned c');
		expect(vi.mocked(source.blob).mock.calls.map((c) => c[0].split('/')[2])).toEqual([
			'PROP-a',
			'PROP-b',
			'PROP-c',
			'PROP-a',
			'PROP-b'
		]);
		const milestones = await openDashboardPage(source, 'main', 'milestones', signal());
		expect(milestones.overlay).toBeUndefined();
	});
});
