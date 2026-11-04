import { afterEach, describe, expect, it, vi } from 'vitest';
import { discoverMilestonePaths, isMilestonePath } from './milestones';
import { buildRoadmap, loadRoadmapDocuments } from './roadmap';
import {
	loadDashboardSection,
	openDashboardPage,
	nextDashboardPage
} from '../features/dashboard/loading';
import { clearRepositoryCache } from './cache';
import { parseBlob } from './documents';
import type { RepositoryDataSource } from './repository';

const signal = () => new AbortController().signal;
const header = (id: string, status = 'planned', extra = '') =>
	`---\nid: ${id}\nstatus: ${status}\n${extra}---\n# Body\n`;
const files: Record<string, string> = {
	'docs/roadmap/MS-global.md': header('MS-global', 'planned', 'depends_on: [MS-api]\n'),
	'docs/roadmap/_archive/MS-base.md': header('MS-base', 'done'),
	'docs/packages/api/roadmap/_archive/MS-api.md': header('MS-api', 'dropped'),
	'docs/packages/web/roadmap/MS-web.md': header(
		'MS-web',
		'planned',
		'depends_on: [MS-base, MS-api]\n'
	),
	'docs/proposals/PROP-api/proposal.md': header('PROP-api', 'draft', 'milestone: MS-web\n'),
	'docs/packages/api/roadmap/_archive/deep/MS-ignore.md': '# ignored',
	'docs/packages/api/roadmap/deep/MS-ignore.md': '# ignored',
	'docs/packages/api/roadmap/README.md': '# ignored',
	'docs/packages/api/ux/MS-ignore.md': '# ignored'
};
const expected = Object.keys(files).filter(isMilestonePath).sort();
function fixture(values = files): RepositoryDataSource {
	return {
		info: async () => ({}),
		tree: vi.fn(async (path: string) => {
			const prefix = path ? `${path}/` : '';
			const children = new Map<string, string>();
			for (const file of Object.keys(values))
				if (file.startsWith(prefix)) {
					const [name, ...rest] = file.slice(prefix.length).split('/');
					children.set(name, rest.length ? 'tree' : 'blob');
				}
			if (!children.size && path) throw new Error('HTTP 404: Not Found');
			return [...children].map(([name, type]) => ({ name, path: prefix + name, type }));
		}),
		blob: vi.fn(async (path: string) => {
			if (!(path in values)) throw new Error('HTTP 404: Not Found');
			return { path, content: values[path], encoding: 'utf-8' };
		})
	};
}
afterEach(() => vi.useRealTimers());
describe('namespace milestone discovery', () => {
	it.each([undefined, '', 'invalid [toml', '[[tool.docs.namespaces]]\nname="api"\npath="api"'])(
		'ignores config %s and shares candidates in generic routes',
		async (config) => {
			const source = fixture(
				config === undefined ? files : { ...files, '.devkit/config.toml': config }
			);
			source.treeRecursive = vi.fn(async () => {
				throw new Error('must stay shallow');
			});
			expect((await discoverMilestonePaths(source, 'main', signal())).paths).toEqual(expected);
			const dashboard = await loadDashboardSection(source, 'main', 'milestones', signal());
			const roadmap = await loadRoadmapDocuments(source, 'main', signal());
			expect(dashboard.documents.map((d) => d.path).sort()).toEqual(expected);
			expect(
				roadmap.documents
					.filter((d) => isMilestonePath(d.path))
					.map((d) => d.path)
					.sort()
			).toEqual(expected);
			expect([dashboard.errors, roadmap.errors]).toEqual([[], []]);
			expect(source.treeRecursive).not.toHaveBeenCalled();
			expect(
				vi
					.mocked(source.blob)
					.mock.calls.every(([p]) => isMilestonePath(p) || /\/proposal.md$/.test(p))
			).toBe(true);
			expect(vi.mocked(source.tree).mock.calls.some(([p]) => p === 'docs/packages/api/ux')).toBe(
				false
			);
		}
	);
	it.each([
		'docs/packages/../roadmap/MS-x.md',
		'docs/packages/.git/roadmap/MS-x.md',
		'docs//roadmap/MS-x.md',
		'docs/packages/api/roadmap/_archive/deep/MS-x.md',
		'docs/packages/api/roadmap/MS-x.md/extra',
		'docs/packages/api/roadmap/MS-x\\.md'
	])('rejects noncanonical path %s', (path) => {
		expect(isMilestonePath(path)).toBe(false);
	});
	it('ignores hostile non-child entries without reading their bodies', async () => {
		const source = fixture();
		const tree = source.tree;
		source.tree = vi.fn(async (...args: Parameters<RepositoryDataSource['tree']>) => [
			...(await tree(...args)),
			{ path: `${args[0]}/../secret`, name: 'secret', type: 'tree' },
			{ path: `${args[0]}/deep/roadmap`, name: 'roadmap', type: 'tree' },
			{ path: 'docs/roadmap/MS-secret.md', name: 'secret', type: 'symlink' }
		]);
		expect((await discoverMilestonePaths(source, 'main', signal())).paths).toEqual(expected);
	});
	it('keeps successful roots and retries errors instead of caching them', async () => {
		const source = fixture();
		const tree = source.tree;
		let fail = true;
		source.tree = vi.fn(async (...args: Parameters<RepositoryDataSource['tree']>) => {
			if (fail && args[0] === 'docs/packages/api/roadmap') throw new Error('HTTP 403: Forbidden');
			return tree(...args);
		});
		const first = await loadDashboardSection(source, 'main', 'milestones', signal());
		expect(first.documents).toHaveLength(3);
		expect(first.errors).toEqual(['docs/packages/api/roadmap: HTTP 403: Forbidden']);
		fail = false;
		expect(
			(await loadDashboardSection(source, 'main', 'milestones', signal())).documents
		).toHaveLength(4);
		clearRepositoryCache(source);
		fail = true;
		expect((await loadRoadmapDocuments(source, 'main', signal())).errors).toHaveLength(1);
		fail = false;
		expect(
			(await loadRoadmapDocuments(source, 'main', signal())).documents.filter((d) =>
				isMilestonePath(d.path)
			)
		).toHaveLength(4);
	});
	it('does not hide a listed 404 and treats absent docs as empty', async () => {
		const source = fixture();
		const tree = source.tree;
		source.tree = vi.fn(async (...args: Parameters<RepositoryDataSource['tree']>) => {
			if (args[0] === 'docs/packages/api') throw new Error('HTTP 404: removed');
			return tree(...args);
		});
		expect((await discoverMilestonePaths(source, 'main', signal())).errors).toEqual([
			'docs/packages/api: HTTP 404: removed'
		]);
		expect(await discoverMilestonePaths(fixture({}), 'main', signal())).toMatchObject({
			paths: [],
			errors: []
		});
	});
	it('does not cache aborted namespace reads and preserves expiry/refresh', async () => {
		vi.useFakeTimers();
		const source = fixture();
		const blob = source.blob;
		const controller = new AbortController();
		source.blob = vi.fn(async (...args: Parameters<RepositoryDataSource['blob']>) => {
			controller.abort();
			return blob(...args);
		});
		await loadDashboardSection(source, 'main', 'milestones', controller.signal);
		source.blob = vi.fn(async (...args: Parameters<RepositoryDataSource['blob']>) => blob(...args));
		await loadDashboardSection(source, 'main', 'milestones', signal());
		expect(source.blob).toHaveBeenCalledTimes(4);
		await loadDashboardSection(source, 'main', 'milestones', signal());
		expect(source.blob).toHaveBeenCalledTimes(4);
		vi.advanceTimersByTime(30000);
		await loadDashboardSection(source, 'main', 'milestones', signal());
		expect(source.blob).toHaveBeenCalledTimes(8);
		clearRepositoryCache(source);
		await loadDashboardSection(source, 'main', 'milestones', signal());
		expect(source.blob).toHaveBeenCalledTimes(12);
	});
	it('resolves all cross-root directions before hiding archives and attaches direct proposals once', async () => {
		const source = fixture({
			...files,
			'docs/packages/api/roadmap/MS-api-live.md': header(
				'MS-api-live',
				'planned',
				'depends_on: [MS-base, MS-api]\n'
			),
			'docs/packages/web/roadmap/MS-wait.md': header(
				'MS-wait',
				'planned',
				'depends_on: [MS-web, MS-missing]\n'
			),
			'docs/proposals/PROP-reject/proposal.md': header(
				'PROP-reject',
				'rejected',
				'milestone: MS-web\n'
			),
			'specs/month/unit/spec.md': header('SPEC-unit', 'in-progress', 'milestone: MS-web\n')
		});
		const result = await loadRoadmapDocuments(source, 'main', signal());
		const graph = buildRoadmap(result.documents, [], { history: false });
		expect(
			graph
				.filter((m) => m.ready)
				.map((m) => m.id)
				.sort()
		).toEqual(['MS-api-live', 'MS-global', 'MS-web']);
		expect(graph.find((m) => m.id === 'MS-wait')).toMatchObject({
			ready: false,
			waitingFor: ['MS-web'],
			unknown: ['MS-missing']
		});
		expect(graph.find((m) => m.id === 'MS-web')?.members.map((m) => m.id)).toEqual(['PROP-api']);
		expect(graph.some((m) => ['MS-base', 'MS-api'].includes(m.id))).toBe(false);
	});
	it('keeps optimized namespace metadata counts and pages without scanning trees', async () => {
		const values = Object.fromEntries(
			Array.from({ length: 10 }, (_, i) => [
				`docs/packages/api/roadmap/MS-${i}.md`,
				header(`MS-${i}`)
			])
		);
		const source = fixture(values);
		source.dashboardList = vi.fn(async () => ({
			items: Object.entries(values)
				.reverse()
				.map(([path, content]) => ({ path, content, encoding: 'utf-8' })),
			errors: []
		}));
		const first = await openDashboardPage(source, 'main', 'milestones', signal());
		expect(first.metadata).toHaveLength(10);
		expect(first.documents).toHaveLength(6);
		expect(first.documents.map((d) => d.meta.id)).toEqual([
			'MS-0',
			'MS-1',
			'MS-2',
			'MS-3',
			'MS-4',
			'MS-5'
		]);
		const next = await nextDashboardPage(source, 'main', 'milestones', first, signal());
		expect(next.documents).toHaveLength(10);
		expect(next.expires).toBe(first.expires);
		expect(source.tree).not.toHaveBeenCalled();
		expect(source.blob).toHaveBeenCalledTimes(10);
	});
	it('bounds generic namespace body reads to six and refills before a slow request completes', async () => {
		const values = Object.fromEntries(
			Array.from({ length: 12 }, (_, i) => [
				`docs/packages/api/roadmap/MS-${String(i).padStart(2, '0')}.md`,
				header(`MS-${i}`)
			])
		);
		const source = fixture(values);
		const blob = source.blob;
		let release!: () => void;
		const slow = new Promise<void>((resolve) => {
			release = resolve;
		});
		let active = 0,
			maximum = 0;
		source.blob = vi.fn(async (...args: Parameters<RepositoryDataSource['blob']>) => {
			maximum = Math.max(maximum, ++active);
			try {
				if (args[0].endsWith('MS-00.md')) await slow;
				return await blob(...args);
			} finally {
				active--;
			}
		});
		const loading = loadDashboardSection(source, 'main', 'milestones', signal());
		await vi.waitFor(() => expect(source.blob).toHaveBeenCalledTimes(12));
		expect(maximum).toBeLessThanOrEqual(6);
		release();
		expect((await loading).documents).toHaveLength(12);
	});
	it('rejects stale namespace writes after refresh and aborted roadmap caching', async () => {
		const source = fixture();
		const blob = source.blob;
		let refresh = true;
		source.blob = vi.fn(async (...args: Parameters<RepositoryDataSource['blob']>) => {
			if (refresh) {
				clearRepositoryCache(source);
				refresh = false;
			}
			return blob(...args);
		});
		await loadDashboardSection(source, 'main', 'milestones', signal());
		await loadDashboardSection(source, 'main', 'milestones', signal());
		expect(source.blob).toHaveBeenCalledTimes(8);
		clearRepositoryCache(source);
		const controller = new AbortController();
		source.blob = vi.fn(async (...args: Parameters<RepositoryDataSource['blob']>) => {
			controller.abort();
			return blob(...args);
		});
		await loadRoadmapDocuments(source, 'main', controller.signal);
		source.blob = vi.fn(async (...args: Parameters<RepositoryDataSource['blob']>) => blob(...args));
		await loadRoadmapDocuments(source, 'main', signal());
		await loadRoadmapDocuments(source, 'main', signal());
		expect(source.blob).toHaveBeenCalledTimes(5);
	});
	it('reports a proposal root listed by metadata that disappears before its read', async () => {
		const source = fixture();
		const tree = source.tree;
		source.tree = vi.fn(async (...args: Parameters<RepositoryDataSource['tree']>) => {
			if (args[0] === 'docs/proposals') throw new Error('HTTP 404: disappeared');
			return tree(...args);
		});
		expect((await loadRoadmapDocuments(source, 'main', signal())).errors).toEqual([
			'docs/proposals: HTTP 404: disappeared'
		]);
	});
	it('discovers an absent docs root from parent metadata without requiring tree error text', async () => {
		const source = fixture({});
		source.tree = vi.fn(async (path: string) => {
			if (path === '') return [];
			throw new Error('ENOENT');
		});
		expect((await discoverMilestonePaths(source, 'main', signal())).errors).toEqual([]);
		expect(vi.mocked(source.tree).mock.calls.map(([path]) => path)).toEqual(['']);
	});
	it('preserves a read failure of docs advertised by root metadata', async () => {
		const source = fixture({});
		source.tree = vi.fn(async (path: string) => {
			if (path === '') return [{ name: 'docs', path: 'docs', type: 'tree' }];
			throw new Error('HTTP 404: removed');
		});
		expect((await discoverMilestonePaths(source, 'main', signal())).errors).toEqual([
			'docs: HTTP 404: removed'
		]);
	});
});
