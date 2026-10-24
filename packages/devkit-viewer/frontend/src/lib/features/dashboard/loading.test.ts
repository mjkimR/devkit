import { afterEach, describe, expect, it, vi } from 'vitest';
import { loadDashboardSection } from './loading';
import { indexDocuments, scanDocuments } from '../../api/documents';
import { cachedResult, cacheGeneration, cacheResult, clearRepositoryCache } from '../../api/cache';
import type { RepositoryDataSource } from '../../api/repository';
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
