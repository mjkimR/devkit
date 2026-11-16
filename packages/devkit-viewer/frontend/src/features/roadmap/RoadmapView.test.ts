import { cleanup, fireEvent, render, screen } from '@testing-library/svelte';
import { afterEach, describe, expect, it, vi } from 'vitest';
import RoadmapView from './RoadmapView.svelte';
import { testSource } from '../../testing/source';

const main: Record<string, string> = {
	'docs/roadmap/_archive/MS-old.md':
		'---\nid: MS-old\ntitle: Archived milestone\nstatus: done\n---\n# Historical detail\n',
	'docs/roadmap/MS-b.md': '---\nid: MS-b\ntitle: Main milestone\nstatus: active\n---\n# B\n',
	'specs/2026-10/20261019-s/spec.md':
		'---\nid: SPEC-s\ntitle: Done on main\nstatus: completed\nmilestone: MS-b\n---\n# S\n'
};
const planX: Record<string, string> = {
	'docs/roadmap/MS-b.md': '---\nid: MS-b\ntitle: Stale copy\nstatus: planned\n---\n# B\n',
	'docs/proposals/PROP-x/proposal.md':
		'---\nid: PROP-x\ntitle: In planning\nstatus: reviewing\nmilestone: MS-b\n---\n# X\n'
};

/** The checked out branch's files: the server reads only the checkout. */
function source(files: Record<string, string>, reads: string[]) {
	const listing = (path: string) => {
		const prefix = path ? `${path}/` : '';
		const names = new Map<string, string>();
		for (const file of Object.keys(files))
			if (file.startsWith(prefix)) {
				const [name, ...rest] = file.slice(prefix.length).split('/');
				names.set(name, rest.length ? 'tree' : 'blob');
			}
		return { items: [...names].map(([name, type]) => ({ name, path: prefix + name, type })) };
	};
	return testSource({
		tree: async (path: string) => {
			reads.push(path);
			return listing(path);
		},
		blob: async (path: string) => {
			reads.push(path);
			const content = files[path];
			if (content === undefined) throw new Error('HTTP 404');
			return { path, content, encoding: 'utf-8' };
		},
		planningProposals: vi.fn(async () => ({ sources: [], items: [], errors: [] }))
	});
}

afterEach(cleanup);

describe('RoadmapView', () => {
	it('reads the checked out branch without the Planning overlay', async () => {
		const onOpen = vi.fn();
		const repository = source(planX, []);
		render(RoadmapView, { source: repository, branch: 'plan-x', onOpen });
		await screen.findByText('Stale copy');
		expect(repository.planningProposals).not.toHaveBeenCalled();
		expect(screen.getByText('In planning')).toBeTruthy();
		await fireEvent.click(screen.getByRole('button', { name: 'In planning' }));
		expect(onOpen).toHaveBeenCalledWith('docs/proposals/PROP-x/proposal.md');
	});
	it('reuses roadmap results when the tab is reopened', async () => {
		const reads: string[] = [];
		const repository = source(planX, reads);
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
	render(RoadmapView, { source: source(main, []), branch: 'main', onOpen });
	await screen.findByText('Main milestone');
	expect(screen.queryByText('Archived milestone')).toBeNull();
	await fireEvent.click(screen.getByRole('checkbox'));
	await screen.findByText('Archived milestone');
	await fireEvent.click(
		screen.getByText('Archived milestone').closest('li')!.querySelector('button')!
	);
	expect(onOpen).toHaveBeenCalledWith('docs/roadmap/_archive/MS-old.md');
});
