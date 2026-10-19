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
	doc(`docs/roadmap/${id}.md`, dependsOn ? { id, status, depends_on: dependsOn } : { id, status });
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

	it('reads activity branches, prefers specs and leaves rejected proposals out', () => {
		const b = buildRoadmap(base, branches, { history: false }).find((m) => m.id === 'MS-b')!;
		expect(b.members.map((m) => [m.id, m.settled, m.branch])).toEqual([
			['PROP-p', false, null],
			['SPEC-h', false, 'dev-h'],
			['SPEC-s', true, null]
		]);
	});

	it('shows only the selected branch without activity branches', () => {
		const b = buildRoadmap(base, [], { history: false }).find((m) => m.id === 'MS-b')!;
		expect(b.members.map((m) => m.id)).toEqual(['PROP-h', 'PROP-p', 'SPEC-s']);
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
		'docs/proposals/PROP-p/proposal.md': '---\nid: PROP-p\nmilestone: MS-b\n---\n# P\n',
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

	it('reads milestones, proposal anchors and spec anchors only', async () => {
		const { documents, errors } = await loadRoadmapDocuments(
			source,
			'main',
			new AbortController().signal
		);
		expect(documents.map((d) => d.path)).toEqual([
			'docs/proposals/PROP-p/proposal.md',
			'docs/roadmap/MS-b.md'
		]);
		expect(errors).toHaveLength(1);
		expect(errors[0]).toMatch(/^specs\/2026-10\/20261019-s\/spec\.md: /);
	});
});
