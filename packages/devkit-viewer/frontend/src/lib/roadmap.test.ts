import { describe, expect, it } from 'vitest';
import { parseBlob } from './documents';
import { buildRoadmap, loadRoadmapDocuments } from './roadmap';
import type { RepositoryDataSource } from './repository';

const doc = (path: string, meta: Record<string, string | string[]>, title = path) => {
	const lines = Object.entries(meta).map(([key, value]) =>
		Array.isArray(value) ? `${key}: [${value.join(', ')}]` : `${key}: ${value}`
	);
	return parseBlob(path, `---\n${lines.join('\n')}\ntitle: ${title}\n---\n\n# ${title}\n`, 'utf-8');
};
const milestone = (id: string, status: string, dependsOn?: string[]) =>
	doc(
		`docs/roadmap/${['done', 'dropped'].includes(status) ? '_archive/' : ''}${id}.md`,
		dependsOn ? { id, status, depends_on: dependsOn } : { id, status }
	);
const proposal = (slug: string, status: string, milestone: string) =>
	doc(`docs/proposals/PROP-${slug}/proposal.md`, { id: `PROP-${slug}`, status, milestone });
const spec = (slug: string, status: string, milestone: string) =>
	doc(`specs/2026-10/20261019-${slug}/spec.md`, { id: `SPEC-${slug}`, status, milestone });

const milestones = [
	milestone('MS-a', 'done'),
	milestone('MS-b', 'active', ['MS-a']),
	milestone('MS-c', 'planned', ['MS-b']),
	milestone('MS-d', 'dropped'),
	milestone('MS-e', 'planned', ['MS-missing', 'MS-d'])
];

describe('buildRoadmap order and readiness', () => {
	it('lists active then planned, history hidden', () => {
		const roadmap = buildRoadmap(milestones, [], { history: false });
		expect(roadmap.map((m) => m.id)).toEqual(['MS-b', 'MS-c', 'MS-e']);
		const [b, c] = roadmap;
		expect([b.ready, b.waitingFor]).toEqual([true, []]);
		expect([c.ready, c.waitingFor]).toEqual([false, ['MS-b']]);
	});

	it('adds done and dropped milestones with history', () => {
		const roadmap = buildRoadmap(milestones, [], { history: true });
		expect(roadmap.map((m) => m.id)).toEqual(['MS-b', 'MS-c', 'MS-e', 'MS-a', 'MS-d']);
	});

	it('never counts an unknown prerequisite as satisfied', () => {
		const e = buildRoadmap(milestones, [], { history: false }).find((m) => m.id === 'MS-e')!;
		expect([e.ready, e.unknown, e.waitingFor]).toEqual([false, ['MS-missing'], []]);
	});
});

describe('buildRoadmap members', () => {
	const base = [
		...milestones,
		proposal('p', 'draft', 'MS-b'),
		proposal('r', 'rejected', 'MS-b'),
		spec('s', 'completed', 'MS-b'),
		proposal('h', 'accepted', 'MS-b'),
		proposal('other', 'draft', 'MS-c')
	];
	const branches = [{ name: 'dev-h', documents: [spec('h', 'in-progress', 'MS-b')] }];

	it('ignores SPEC metadata and leaves direct PROP members and rejected filtering intact', () => {
		const b = buildRoadmap(base, branches, { history: false }).find((m) => m.id === 'MS-b')!;
		expect(b.members.map((m) => [m.id, m.settled, m.branch])).toEqual([
			['PROP-h', false, null],
			['PROP-p', false, null]
		]);
	});

	it('shows only the selected branch without activity branches', () => {
		const b = buildRoadmap(base, [], { history: false }).find((m) => m.id === 'MS-b')!;
		expect(b.members.map((m) => m.id)).toEqual(['PROP-h', 'PROP-p']);
	});

	it('does not replace PROP membership with a same-slug completed SPEC on any branch', () => {
		const documents = [...base, spec('p', 'completed', 'MS-c')];
		const activity = [{ name: 'dev-p', documents: [spec('p', 'completed', 'MS-c')] }];
		const b = buildRoadmap(documents, activity, { history: true }).find((m) => m.id === 'MS-b')!;
		expect(b.members.map((m) => m.id)).toEqual(['PROP-h', 'PROP-p']);
		expect(b.members.every((m) => m.kind === 'proposal' && !m.settled)).toBe(true);
	});

	it('retains proposal members when showing milestone history', () => {
		const history = buildRoadmap([...base, proposal('old', 'draft', 'MS-a')], [], {
			history: true
		});
		expect(history.find((m) => m.id === 'MS-a')!.members.map((m) => m.id)).toEqual(['PROP-old']);
	});

	it('follows a member that moved to another milestone on its branch', () => {
		const moved = [{ name: 'plan-p', documents: [proposal('p', 'reviewing', 'MS-c')] }];
		const roadmap = buildRoadmap(base, moved, { history: false });
		expect(roadmap.find((m) => m.id === 'MS-b')!.members.map((m) => m.id)).not.toContain('PROP-p');
		expect(roadmap.find((m) => m.id === 'MS-c')!.members.map((m) => [m.id, m.branch])).toEqual([
			['PROP-other', null],
			['PROP-p', 'plan-p']
		]);
	});
});

describe('loadRoadmapDocuments', () => {
	const files: Record<string, string> = {
		'docs/roadmap/MS-b.md': '---\nid: MS-b\nstatus: active\n---\n# B\n',
		'docs/roadmap/README.md': '# Roadmap\n',
		'docs/roadmap/_archive/MS-old.md': '---\nid: MS-old\nstatus: done\n---\n# Old\n',
		'docs/roadmap/_archive/MS-dropped.md': '---\nid: MS-dropped\nstatus: dropped\n---\n# Dropped\n',
		'docs/roadmap/_archive/year/MS-ignore.md': '# Ignore\n',
		'docs/proposals/PROP-p/proposal.md': '---\nid: PROP-p\nmilestone: MS-b\n---\n# P\n',
		'docs/proposals/PROP-broken/proposal.md': '---\nid: PROP-broken\nmilestone: [broken\n---\n',
		'docs/proposals/PROP-q/notes.md': '# not a bundle anchor\n',
		'specs/2026-10/20261019-s/spec.md': '---\nid: SPEC-s\nmilestone: [broken\n---\n# S\n',
		'docs/capabilities/a/CAP-A-x.md': '# unrelated\n'
	};
	const source: RepositoryDataSource = {
		info: async () => ({ default_branch: 'main' }),
		tree: async (path) => {
			const prefix = path ? `${path}/` : '';
			const names = new Map<string, string>();
			for (const file of Object.keys(files))
				if (file.startsWith(prefix)) {
					const [name, ...rest] = file.slice(prefix.length).split('/');
					names.set(name, rest.length ? 'tree' : 'blob');
				}
			if (!names.size) throw new Error(`HTTP 404: ${path}`);
			return {
				items: [...names].map(([name, type]) => ({ name, path: prefix + name, type }))
			};
		},
		blob: async (path) => {
			if (!(path in files)) throw new Error(`HTTP 404: ${path}`);
			return { path, content: files[path], encoding: 'utf-8' };
		}
	};

	it('loads only milestone and proposal anchors and preserves their error reporting', async () => {
		const { documents, errors } = await loadRoadmapDocuments(
			source,
			'main',
			new AbortController().signal
		);
		expect(documents.map((d) => d.path)).toEqual([
			'docs/proposals/PROP-p/proposal.md',
			'docs/roadmap/_archive/MS-dropped.md',
			'docs/roadmap/_archive/MS-old.md',
			'docs/roadmap/MS-b.md'
		]);
		expect(errors).toHaveLength(1);
		expect(errors[0]).toMatch(/^docs\/proposals\/PROP-broken\/proposal\.md: /);
	});
});

it('keeps done and dropped archived prerequisites satisfied before history filtering', () => {
	const base = [
		milestone('MS-done', 'done'),
		milestone('MS-drop', 'dropped'),
		milestone('MS-live', 'active', ['MS-done', 'MS-drop'])
	];
	for (const history of [false, true]) {
		const live = buildRoadmap(base, [], { history }).find((m) => m.id === 'MS-live')!;
		expect([live.ready, live.unknown, live.waitingFor]).toEqual([true, [], []]);
	}
	const reopened = milestone('MS-done', 'active');
	expect(reopened.path).toBe('docs/roadmap/MS-done.md');
	expect(buildRoadmap([reopened], [], { history: false })[0].status).toBe('active');
});
