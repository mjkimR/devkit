import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { afterEach, describe, expect, it, vi } from 'vitest';
import RoadmapView from './RoadmapView.svelte';
import type { RepositoryDataSource } from './repository';

const files: Record<string, Record<string, string>> = {
	main: {
		'docs/roadmap/_archive/MS-old.md':
			'---\nid: MS-old\ntitle: Archived milestone\nstatus: done\n---\n# Historical detail\n',
		'docs/roadmap/MS-b.md': '---\nid: MS-b\ntitle: Main milestone\nstatus: active\n---\n# B\n',
		'specs/2026-10/20261019-s/spec.md':
			'---\nid: SPEC-s\ntitle: Done on main\nstatus: completed\nmilestone: MS-b\n---\n# S\n'
	},
	'plan-x': {
		'docs/roadmap/MS-b.md': '---\nid: MS-b\ntitle: Stale copy\nstatus: planned\n---\n# B\n',
		'docs/proposals/PROP-x/proposal.md':
			'---\nid: PROP-x\ntitle: In planning\nstatus: reviewing\nmilestone: MS-b\n---\n# X\n'
	},
	other: {
		'docs/proposals/PROP-o/proposal.md':
			'---\nid: PROP-o\ntitle: Not an activity branch\nstatus: draft\nmilestone: MS-b\n---\n# O\n'
	}
};

function source(withRefs: boolean, reads: string[]): RepositoryDataSource {
	const listing = (ref: string, path: string) => {
		const prefix = path ? `${path}/` : '';
		const names = new Map<string, string>();
		for (const file of Object.keys(files[ref] ?? {}))
			if (file.startsWith(prefix)) {
				const [name, ...rest] = file.slice(prefix.length).split('/');
				names.set(name, rest.length ? 'tree' : 'blob');
			}
		return { items: [...names].map(([name, type]) => ({ name, path: prefix + name, type })) };
	};
	return {
		info: async () => ({ default_branch: 'main' }),
		tree: async (path, ref) => {
			reads.push(ref);
			return listing(ref, path);
		},
		blob: async (path, ref) => {
			reads.push(ref);
			const content = files[ref]?.[path];
			if (content === undefined) throw new Error('HTTP 404');
			return { path, content, encoding: 'utf-8' };
		},
		planningProposals: vi.fn(async () => ({ sources: [], items: [], errors: [] })),
		...(withRefs
			? {
					refs: vi.fn(async () => ({
						default_branch: 'main',
						branches: ['main', 'other', 'plan-x']
					}))
				}
			: {})
	};
}

afterEach(cleanup);

describe('RoadmapView', () => {
	it('reads only the checked out branch and does not enumerate branches', async () => {
		const reads: string[] = [];
		const onOpen = vi.fn();
		const repository = source(true, reads);
		render(RoadmapView, { source: repository, branch: 'plan-x', onOpen });
		await screen.findByText('Stale copy');
		expect(new Set(reads)).toEqual(new Set(['plan-x']));
		expect(repository.refs).not.toHaveBeenCalled();
		expect(repository.planningProposals).not.toHaveBeenCalled();
		expect(screen.queryByText('Done on main')).toBeNull();
		expect(screen.getByText('In planning')).toBeTruthy();
		await fireEvent.click(screen.getByRole('button', { name: 'In planning' }));
		expect(onOpen).toHaveBeenCalledWith('docs/proposals/PROP-x/proposal.md');
		expect(screen.queryByText('Not an activity branch')).toBeNull();
	});

	it('reads the checked out branch when the source does not enumerate refs', async () => {
		const reads: string[] = [];
		render(RoadmapView, { source: source(false, reads), branch: 'plan-x', onOpen: () => {} });
		await screen.findByText('Stale copy');
		await waitFor(() => expect(new Set(reads)).toEqual(new Set(['plan-x'])));
		expect(screen.getByText('In planning')).toBeTruthy();
	});
	it('reuses roadmap results when the tab is reopened', async () => {
		const reads: string[] = [];
		const repository = source(false, reads);
		const props = { source: repository, branch: 'plan-x', onOpen: vi.fn() };
		const view = render(RoadmapView, props);
		await screen.findByText('In planning');
		const count = reads.length;
		view.unmount();
		render(RoadmapView, props);
		await screen.findByText('In planning');
		expect(reads).toHaveLength(count);
	});
});

it('opens an archived milestone from the history control using its retained path', async () => {
	const onOpen = vi.fn();
	render(RoadmapView, { source: source(false, []), branch: 'main', onOpen });
	await screen.findByText('Main milestone');
	expect(screen.queryByText('Archived milestone')).toBeNull();
	await fireEvent.click(screen.getByRole('checkbox'));
	await screen.findByText('Archived milestone');
	await fireEvent.click(
		screen.getByText('Archived milestone').closest('li')!.querySelector('button')!
	);
	expect(onOpen).toHaveBeenCalledWith('docs/roadmap/_archive/MS-old.md');
});
