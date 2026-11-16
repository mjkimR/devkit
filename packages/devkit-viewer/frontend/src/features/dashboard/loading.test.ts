import { afterEach, describe, expect, it, vi } from 'vitest';
import { loadDashboardSection, type DashboardSection } from './loading';
import { indexDocuments, scanDocuments } from '../../api/documents';
import { cachedResult, cacheGeneration, cacheResult, clearRepositoryCache } from '../../api/cache';
import { loadRoadmapDocuments } from '../../api/roadmap';
import { testSource } from '../../testing/source';

const signal = () => new AbortController().signal;
type Entry = { path: string; content: string; encoding: string };
const entry = (path: string, header: string): Entry => ({
	path,
	content: `---\n${header}\n---\n`,
	encoding: 'utf-8'
});

/** A source whose `dashboardList` returns the headers and whose `blob` adds a body to them. */
function listed(entries: Entry[]) {
	return testSource({
		dashboardList: vi.fn(async (_section: string, _signal: AbortSignal) => ({
			items: entries,
			errors: [] as string[]
		})),
		blob: vi.fn(async (path: string, _signal: AbortSignal) => {
			const found = entries.find((e) => e.path === path);
			if (!found) throw new Error(`HTTP 404: ${path}`);
			return { path, content: `${found.content}# Body\nsummary of ${path}`, encoding: 'utf-8' };
		})
	});
}
const ids = (documents: { meta: Record<string, any> }[]) => documents.map((d) => d.meta.id);

afterEach(() => vi.useRealTimers());

describe('dashboard sections', () => {
	it('lists each section once and reads every eligible body beyond the former page sizes', async () => {
		const sizes: Record<DashboardSection, Entry[]> = {
			milestones: Array.from({ length: 7 }, (_, i) =>
				entry(`docs/roadmap/MS-${i}.md`, `id: MS-${i}\nstatus: active`)
			),
			proposals: Array.from({ length: 10 }, (_, i) =>
				entry(`docs/proposals/PROP-${i}/proposal.md`, `id: PROP-${i}\nstatus: draft`)
			),
			feedback: Array.from({ length: 7 }, (_, i) =>
				entry(`specs/m/u/feedback/${i}.md`, `id: FB-${i}\nstatus: open\nseverity: friction`)
			)
		};
		for (const section of ['milestones', 'proposals', 'feedback'] as const) {
			const source = listed(sizes[section]);
			const result = await loadDashboardSection(source, section, signal());
			expect(source.dashboardList).toHaveBeenCalledTimes(1);
			expect(source.dashboardList).toHaveBeenCalledWith(section, expect.anything());
			expect(source.blob).toHaveBeenCalledTimes(sizes[section].length);
			expect(result.documents).toHaveLength(sizes[section].length);
			expect(result.errors).toEqual([]);
		}
	});

	it('keeps the status, severity, ID and path order and reads only eligible entries', async () => {
		const source = listed([
			entry('docs/roadmap/MS-b.md', 'id: MS-b\nstatus: planned'),
			entry('docs/roadmap/MS-c.md', 'id: MS-c\nstatus: active'),
			entry('docs/roadmap/_archive/MS-d.md', 'id: MS-d\nstatus: done'),
			entry('docs/roadmap/MS-a.md', 'id: MS-a\nstatus: active'),
			entry('specs/a/feedback/z.md', 'id: FB-same\nstatus: open\nseverity: friction'),
			entry('specs/a/feedback/a.md', 'id: FB-same\nstatus: open\nseverity: friction'),
			entry('specs/a/feedback/c.md', 'id: FB-c\nstatus: open\nseverity: critical'),
			entry('specs/a/feedback/r.md', 'id: FB-r\nstatus: resolved\nseverity: critical'),
			entry('docs/proposals/PROP-a/proposal.md', 'id: PROP-a\nstatus: accepted'),
			entry('docs/proposals/PROP-b/proposal.md', 'id: PROP-b\nstatus: review'),
			entry('docs/proposals/PROP-c/proposal.md', 'id: PROP-c\nstatus: draft')
		]);
		const milestones = await loadDashboardSection(source, 'milestones', signal());
		expect(ids(milestones.documents)).toEqual(['MS-a', 'MS-c', 'MS-b']);
		// The archived done milestone counts in the listing but is never read.
		expect(ids(milestones.metadata)).toContain('MS-d');
		const feedback = await loadDashboardSection(source, 'feedback', signal());
		expect(feedback.documents.map((d) => d.path)).toEqual([
			'specs/a/feedback/c.md',
			'specs/a/feedback/a.md',
			'specs/a/feedback/z.md'
		]);
		const proposals = await loadDashboardSection(source, 'proposals', signal());
		expect(ids(proposals.documents)).toEqual(['PROP-b', 'PROP-c', 'PROP-a']);
		const read = vi.mocked(source.blob).mock.calls.map(([path]) => path);
		expect(read).not.toContain('docs/roadmap/_archive/MS-d.md');
		expect(read).not.toContain('specs/a/feedback/r.md');
	});

	it('ignores hostile and out-of-section entries of the listing', async () => {
		const source = listed([
			entry('specs/../feedback/private.md', 'id: FB-x\nstatus: open'),
			entry('docs/roadmap/sub/MS-nested.md', 'id: MS-nested\nstatus: active'),
			entry('specs/a/feedback/README.md', 'id: FB-readme\nstatus: open'),
			entry('specs/a/feedback/a.md', 'id: FB-a\nstatus: open')
		]);
		expect(ids((await loadDashboardSection(source, 'feedback', signal())).documents)).toEqual([
			'FB-a'
		]);
		expect((await loadDashboardSection(source, 'milestones', signal())).documents).toEqual([]);
	});

	it('shows the readable cards and counts a failed body read with its path', async () => {
		const source = listed(
			['a', 'b', 'c'].map((slug) =>
				entry(`docs/proposals/PROP-${slug}/proposal.md`, `id: PROP-${slug}\nstatus: draft`)
			)
		);
		const blob = source.blob.getMockImplementation()!;
		source.blob.mockImplementation(async (path, s) => {
			if (path.includes('PROP-b')) throw new Error('unreadable');
			return blob(path, s);
		});
		const result = await loadDashboardSection(source, 'proposals', signal());
		expect(ids(result.documents)).toEqual(['PROP-a', 'PROP-c']);
		expect(result.errors).toEqual(['docs/proposals/PROP-b/proposal.md: unreadable']);
		expect(result.listErrors).toEqual([]);
		expect(ids(result.metadata)).toEqual(['PROP-a', 'PROP-b', 'PROP-c']);
	});

	it('keeps listing failures and malformed headers apart from body reads', async () => {
		const source = listed([
			entry('docs/proposals/PROP-a/proposal.md', 'id: PROP-a\nstatus: draft'),
			{ path: 'docs/proposals/PROP-x/proposal.md', content: '---\n: [\n---\n', encoding: 'utf-8' }
		]);
		const items = (await source.dashboardList('proposals', signal())).items;
		source.dashboardList.mockResolvedValueOnce({
			items,
			errors: ['docs/proposals/PROP-y: unreadable directory']
		});
		const result = await loadDashboardSection(source, 'proposals', signal());
		expect(result.listErrors).toHaveLength(2);
		expect(result.listErrors[0]).toBe('docs/proposals/PROP-y: unreadable directory');
		expect(result.errors).toEqual(result.listErrors);
		expect(ids(result.documents)).toEqual(['PROP-a']);
	});

	it('keeps order with delayed bodies, at most six requests in flight, and stops on abort', async () => {
		const entries = Array.from({ length: 12 }, (_, i) =>
			entry(
				`docs/proposals/PROP-${String(i).padStart(2, '0')}/proposal.md`,
				`id: PROP-${String(i).padStart(2, '0')}\nstatus: draft`
			)
		);
		const source = listed(entries);
		const blob = source.blob.getMockImplementation()!;
		let release!: () => void;
		const slow = new Promise<void>((resolve) => (release = resolve));
		let active = 0,
			maximum = 0;
		source.blob.mockImplementation(async (path, s) => {
			maximum = Math.max(maximum, ++active);
			if (path === entries[0].path) await slow;
			active--;
			return blob(path, s);
		});
		const work = loadDashboardSection(source, 'proposals', signal());
		await vi.waitFor(() => expect(source.blob).toHaveBeenCalledTimes(12));
		expect(maximum).toBeLessThanOrEqual(6);
		release();
		expect((await work).documents.map((d) => d.path)).toEqual(entries.map((e) => e.path));

		const controller = new AbortController();
		source.blob.mockClear();
		source.blob.mockImplementation(async (path) => {
			controller.abort();
			throw new Error(`late ${path}`);
		});
		const aborted = await loadDashboardSection(source, 'proposals', controller.signal);
		// No worker starts another read once the signal is aborted, and nothing is reported.
		expect(source.blob).toHaveBeenCalledTimes(1);
		expect(aborted.errors).toEqual([]);
	});

	it('caches nothing: a second open lists and reads again', async () => {
		const source = listed([entry('docs/roadmap/MS-a.md', 'id: MS-a\nstatus: active')]);
		await loadDashboardSection(source, 'milestones', signal());
		await loadDashboardSection(source, 'milestones', signal());
		expect(source.dashboardList).toHaveBeenCalledTimes(2);
		expect(source.blob).toHaveBeenCalledTimes(2);
	});
});

describe('tab caches', () => {
	const files: Record<string, string> = {
		'docs/roadmap/MS-a.md': '---\nid: MS-a\nstatus: active\n---\n# Milestone',
		'docs/a.md': '# A',
		'specs/m/u/spec.md': '# Spec'
	};
	function tree() {
		return testSource({
			tree: vi.fn(async (root: string, _signal: AbortSignal) => {
				const prefix = root ? `${root}/` : '';
				const names = new Map<string, string>();
				for (const file of Object.keys(files))
					if (file.startsWith(prefix)) {
						const [name, ...rest] = file.slice(prefix.length).split('/');
						names.set(name, rest.length ? 'tree' : 'blob');
					}
				return [...names].map(([name, type]) => ({ name, path: prefix + name, type }));
			}),
			treeRecursive: vi.fn(async (root: string, _signal: AbortSignal) => ({
				items: Object.keys(files)
					.filter((path) => path.startsWith(`${root}/`))
					.map((path) => ({ path, name: path.split('/').at(-1)!, type: 'blob' }))
			})),
			blob: vi.fn(async (path: string, _signal: AbortSignal) => ({
				path,
				content: files[path],
				encoding: 'utf-8'
			}))
		});
	}

	it('bounds cache entries and rejects writes from before refresh', () => {
		const source = tree();
		const generation = cacheGeneration(source);
		for (let i = 0; i < 9; i++) cacheResult(source, String(i), 'test', i, generation);
		expect(cachedResult(source, '0', 'test')).toBeUndefined();
		expect(cachedResult(source, '1', 'test')).toBe(1);
		clearRepositoryCache(source);
		cacheResult(source, 'main', 'test', 'old', generation);
		expect(cachedResult(source, 'main', 'test')).toBeUndefined();
	});

	it('reuses the document index and roadmap for 30 seconds, per branch, until refresh', async () => {
		vi.useFakeTimers();
		const source = tree();
		const first = await indexDocuments(source, 'main', signal());
		expect(await indexDocuments(source, 'main', signal())).toBe(first);
		expect(await indexDocuments(source, 'other', signal())).not.toBe(first);
		const roadmap = await loadRoadmapDocuments(source, 'main', signal());
		expect(await loadRoadmapDocuments(source, 'main', signal())).toBe(roadmap);
		vi.advanceTimersByTime(30_000);
		expect(await indexDocuments(source, 'main', signal())).not.toBe(first);
		const fresh = await loadRoadmapDocuments(source, 'main', signal());
		expect(fresh).not.toBe(roadmap);
		clearRepositoryCache(source);
		expect(await loadRoadmapDocuments(source, 'main', signal())).not.toBe(fresh);
	});

	it('lists each index root with one recursive request and ignores out-of-scope paths', async () => {
		const source = tree();
		source.treeRecursive.mockImplementation(async (root: string) => ({
			items: [
				...Object.keys(files)
					.filter((path) => path.startsWith(`${root}/`))
					.map((path) => ({ path, name: path.split('/').at(-1)!, type: 'blob' })),
				{ path: `${root}/../secret.md`, name: 'secret.md', type: 'blob' },
				{ path: 'elsewhere/a.md', name: 'a.md', type: 'blob' }
			]
		}));
		const result = await scanDocuments(source, signal(), ['docs', 'specs']);
		expect(result.documents.map((d) => d.path)).toEqual([
			'docs/a.md',
			'docs/roadmap/MS-a.md',
			'specs/m/u/spec.md'
		]);
		expect(source.treeRecursive).toHaveBeenCalledTimes(2);
		expect(source.tree).not.toHaveBeenCalled();
	});
});
