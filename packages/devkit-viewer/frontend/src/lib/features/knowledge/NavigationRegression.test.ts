import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/svelte';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import SddViewer from '../../SddViewer.svelte';
import KnowledgeViews from './KnowledgeViews.svelte';
import { documentAnchor } from '../../api/documents';
import type { RepositoryDataSource } from '../../api/repository';
const page = (id: string, body = '', extra = '') =>
	`---\nid: ${id}\ntitle: ${id}\nsummary: "Navigation."\nstatus: active\n${extra}---\n# [${id}] ${id}\n\n${body}`;
function repository(files: Record<string, string>): RepositoryDataSource {
	const list = (root: string) => ({
		items: Object.keys(files)
			.filter((path) => path.startsWith(root + '/'))
			.map((path) => ({ path, name: path.split('/').at(-1), type: 'blob' }))
	});
	return {
		info: async () => ({ default_branch: 'main' }),
		tree: vi.fn(async (root) => list(root)),
		treeRecursive: vi.fn(async (root) => list(root)),
		blob: vi.fn(async (path) => {
			if (!(path in files)) throw new Error('HTTP 404');
			return { path, content: files[path], encoding: 'utf-8' };
		})
	};
}
const props = (source: RepositoryDataSource, requestedPath = '') => ({
	source,
	view: 'book' as const,
	bookRequested: true,
	branch: 'main',
	theme: 'dark',
	requestedPath,
	requestedAnchor: '',
	onOpen: vi.fn(),
	onLocation: vi.fn(),
	diagrams: () => ({ destroy() {} })
});
let scrolled: string[] = [];
beforeEach(() => {
	scrolled = [];
	Element.prototype.scrollIntoView = vi.fn(function (this: Element) {
		scrolled.push(this.id);
	});
	vi.stubGlobal(
		'IntersectionObserver',
		class {
			observe() {}
			disconnect() {}
		}
	);
	URL.createObjectURL = vi.fn(() => 'blob:navigation');
	URL.revokeObjectURL = vi.fn();
});
afterEach(() => {
	cleanup();
	vi.unstubAllGlobals();
});
it('Files preserves same/peer encoded fragments and raw anchors without reloading same-path content', async () => {
	const a = 'docs/designs/DESIGN-a.md',
		b = 'docs/designs/DESIGN-b.md';
	const source = repository({
		[a]: page('DESIGN-a', '[Within](#details)\n\n[Peer](DESIGN-b.md#peer%20details)\n\n## Details'),
		[b]: page(
			'DESIGN-b',
			'<h2 id="peer details">Peer details</h2>\n\n[Raw anchor](#raw%20anchor)\n\n<a id="raw anchor"></a>'
		)
	});
	render(SddViewer, { dataSource: source, initialView: 'files', initialPath: a });
	await screen.findByRole('complementary', { name: 'References for DESIGN-a' });
	await waitFor(() => expect(screen.queryByText('Loading references…')).toBeNull());
	const reads = vi.mocked(source.blob).mock.calls.filter(([path]) => path === a).length;
	await fireEvent.click(screen.getByRole('link', { name: 'Within' }));
	await waitFor(() => expect(scrolled).toContain(documentAnchor(a) + '--details'));
	await fireEvent.click(screen.getByRole('link', { name: 'Within' }));
	expect(vi.mocked(source.blob).mock.calls.filter(([path]) => path === a)).toHaveLength(reads);
	await fireEvent.click(screen.getByRole('link', { name: 'Peer' }));
	await waitFor(() => expect(scrolled).toContain(documentAnchor(b) + '--peer details'));
	await fireEvent.click(screen.getByRole('link', { name: 'Raw anchor' }));
	await waitFor(() => expect(scrolled).toContain(documentAnchor(b) + '--raw anchor'));
});
it.each(['body', 'panel'])(
	'first Read %s reference restores actual origin, filters and position through Back',
	async (route) => {
		const a = 'docs/designs/DESIGN-a.md',
			b = 'docs/designs/DESIGN-b.md';
		const view = props(
			repository({
				[a]: page('DESIGN-a', '[DESIGN-b]', 'related_designs: [DESIGN-b]\n'),
				[b]: page('DESIGN-b')
			})
		);
		render(KnowledgeViews, view);
		await waitFor(() => expect(document.querySelectorAll('.chapter')).toHaveLength(2));
		const content = document.querySelector('.reading-content')!;
		content.scrollTop = 123;
		const chapter = document.getElementById(documentAnchor(a))!;
		await fireEvent.click(
			route === 'body'
				? within(chapter).getByRole('link', { name: '[DESIGN-b]' })
				: within(
						[...chapter.querySelectorAll('.formal-references li')].find((row) =>
							row.textContent?.includes('related_designs')
						)! as HTMLElement
					).getByRole('button')
		);
		await fireEvent.click(await screen.findByRole('button', { name: 'Back to previous document' }));
		await waitFor(() => expect(view.onLocation.mock.calls.at(-1)?.[0]).toBe(a));
		expect(content.scrollTop).toBe(123);
	}
);
it('explicit search and namespace changes expire the prior pin, while a new hidden request still materializes', async () => {
	const a = 'docs/packages/first/designs/DESIGN-a.md',
		b = 'docs/packages/second/designs/DESIGN-b.md';
	const source = repository({ [a]: page('DESIGN-a'), [b]: page('DESIGN-b') });
	const view = render(KnowledgeViews, props(source));
	await waitFor(() => expect(document.querySelectorAll('.chapter')).toHaveLength(2));
	await fireEvent.change(screen.getByRole('combobox', { name: 'Scope' }), {
		target: { value: 'first' }
	});
	await fireEvent.click(screen.getByRole('button', { name: 'DESIGN-a DESIGN-a' }));
	await fireEvent.input(screen.getByRole('textbox', { name: 'Search documents' }), {
		target: { value: 'absent-query' }
	});
	await waitFor(() => expect(document.querySelectorAll('.chapter')).toHaveLength(0));
	await fireEvent.input(screen.getByRole('textbox', { name: 'Search documents' }), {
		target: { value: '' }
	});
	await fireEvent.click(screen.getByRole('button', { name: 'DESIGN-a DESIGN-a' }));
	await fireEvent.change(screen.getByRole('combobox', { name: 'Scope' }), {
		target: { value: 'second' }
	});
	await waitFor(() =>
		expect([...document.querySelectorAll('.chapter')].map((node) => node.id)).toEqual([
			documentAnchor(b)
		])
	);
	await view.rerender({ ...props(source), requestedPath: 'DESIGN-a' });
	await waitFor(() => expect(document.getElementById(documentAnchor(a))).not.toBeNull());
});
it.each([false, true])(
	'an empty completed index retains written identity and retry after errors=%s',
	async (failed) => {
		const files: Record<string, string> = {};
		const source = repository(files),
			listing = source.treeRecursive!;
		let bad = failed;
		source.treeRecursive = vi.fn(async (path, ref, signal) => {
			if (bad) throw new Error('HTTP 403');
			return listing(path, ref, signal);
		});
		render(KnowledgeViews, props(source, 'DESIGN-missing'));
		await screen.findByText(
			`DESIGN-missing — unavailable (${failed ? 'index incomplete' : 'missing'})`
		);
		expect(screen.getByRole('button', { name: 'Back to documents' })).toBeTruthy();
		bad = false;
		files['docs/designs/DESIGN-missing.md'] = page('DESIGN-missing');
		await fireEvent.click(screen.getByRole('button', { name: 'Reload documents' }));
		await waitFor(() => expect(document.querySelectorAll('.chapter')).toHaveLength(1));
		expect(screen.queryByText(/DESIGN-missing — unavailable/)).toBeNull();
	}
);
it('same-artifact fragments scroll without a second blob read or new document history', async () => {
	const path = 'docs/designs/DESIGN-a/artifacts/example.md';
	const source = repository({ [path]: '# Example\n\n[Second](#second)\n\n## Second' });
	render(SddViewer, { dataSource: source, initialView: 'files', initialPath: path });
	await screen.findByRole('link', { name: 'Second' });
	const reads = vi.mocked(source.blob).mock.calls.length;
	await fireEvent.click(screen.getByRole('link', { name: 'Second' }));
	await waitFor(() => expect(scrolled).toContain(documentAnchor(path) + '--second'));
	expect(source.blob).toHaveBeenCalledTimes(reads);
	expect(screen.queryByRole('button', { name: 'Back to previous document' })).toBeNull();
	expect(source.treeRecursive).not.toHaveBeenCalled();
});
it('direct Files artifact host anchors scroll initially and on same-path prop changes without another read', async () => {
	const path = 'docs/designs/DESIGN-a/artifacts/sample.md';
	const source = repository({
		[path]: '# Artifact\n\n<h2 id="first section">First</h2>\n\n<a id="raw anchor"></a>'
	});
	const view = render(SddViewer, {
		dataSource: source,
		initialView: 'files',
		initialPath: path,
		initialAnchor: 'first%20section'
	});
	await screen.findByRole('heading', { name: 'First' });
	await waitFor(() => expect(scrolled).toContain(documentAnchor(path) + '--first section'));
	const reads = vi
		.mocked(source.blob)
		.mock.calls.filter(([candidate]) => candidate === path).length;
	await view.rerender({ initialAnchor: 'raw%20anchor' });
	await waitFor(() => expect(scrolled).toContain(documentAnchor(path) + '--raw anchor'));
	expect(
		vi.mocked(source.blob).mock.calls.filter(([candidate]) => candidate === path)
	).toHaveLength(reads);
});
