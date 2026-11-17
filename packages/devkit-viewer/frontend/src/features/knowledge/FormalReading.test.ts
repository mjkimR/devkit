import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/svelte';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import KnowledgeViews from './KnowledgeViews.svelte';
import SddViewer from '../../SddViewer.svelte';
import { documentAnchor, parseBlob, bookGroup } from '../../api/documents';
import { readFileSync } from 'node:fs';
import type { RepositoryDataSource } from '../../api/repository';
import { openFile } from '../../testing/files';
import { testSource } from '../../testing/source';
const roles = [
	['DESIGN', 'designs'],
	['DOMAIN', 'domain'],
	['OPS', 'operations']
] as const;
const page = (id: string, body = '', extra = '') =>
	`---\nid: ${id}\ntitle: ${id} title\nsummary: "${id} example"\nstatus: active\n${extra}---\n# [${id}] ${id} title\n\n${body}`;
function repository(files: Record<string, string>) {
	if (Object.keys(files).some((path) => path.startsWith('docs/packages/registered/'))) {
		files['.devkit/config.toml'] =
			'[[tool.docs.namespaces]]\nname="registered"\npath="packages/registered"\n';
		files['packages/registered/README.md'] = '# Registered source package';
	}

	const listing = (path: string) => ({
		items: Object.keys(files)
			.filter((file) => file.startsWith(path + '/'))
			.map((file) => ({ name: file.split('/').at(-1), path: file, type: 'blob' }))
	});
	return testSource({
		tree: vi.fn(async (path: string, _signal: AbortSignal) => listing(path)),
		treeRecursive: vi.fn(async (path: string, _signal: AbortSignal) => listing(path)),
		blob: vi.fn(async (path: string, _signal: AbortSignal) => {
			if (!(path in files)) throw new Error('HTTP 404: Not Found');
			return {
				path,
				content: files[path],
				encoding: /\.(png|bin)$/.test(path) ? 'base64' : 'utf-8'
			};
		})
	});
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
	diagrams: () => ({ destroy() {} })
});
/** The element the reader last scrolled to: the document the book shows. */
const scrolledTo = () =>
	(vi.mocked(Element.prototype.scrollIntoView).mock.contexts.at(-1) as Element | undefined)?.id;
beforeEach(() => {
	Element.prototype.scrollIntoView = vi.fn();
	vi.stubGlobal(
		'IntersectionObserver',
		class {
			observe() {}
			disconnect() {}
		}
	);
	URL.createObjectURL = vi.fn(() => `blob:test-${Math.random()}`);
	URL.revokeObjectURL = vi.fn();
});
afterEach(() => {
	cleanup();
	vi.unstubAllGlobals();
});
describe.each(roles)('%s real reading surfaces', (prefix, dir) => {
	it('searches aliases/body and exposes retired only explicitly or as a direct target', async () => {
		const files = {
			[`docs/${dir}/${prefix}-active.md`]: page(
				`${prefix}-active`,
				'unique needle',
				`aliases: [${prefix}-old_name]\n`
			),
			[`docs/packages/registered/${dir}/${prefix}-retired.md`]: page(
				`${prefix}-retired`,
				'historical evidence',
				''
			).replace('status: active', 'status: retired'),
			[`docs/${dir}/${prefix}-other-retired.md`]: page(`${prefix}-other-retired`).replace(
				'status: active',
				'status: retired'
			)
		};
		const view = render(KnowledgeViews, props(repository(files)));
		await waitFor(() => expect(document.querySelectorAll('.chapter')).toHaveLength(1));
		await fireEvent.input(screen.getByRole('textbox', { name: 'Search documents' }), {
			target: { value: `${prefix}-old_name` }
		});
		expect(document.querySelectorAll('.chapter')).toHaveLength(1);
		await fireEvent.input(screen.getByRole('textbox', { name: 'Search documents' }), {
			target: { value: 'unique needle' }
		});
		expect(document.querySelectorAll('.chapter')).toHaveLength(1);
		await fireEvent.input(screen.getByRole('textbox', { name: 'Search documents' }), {
			target: { value: '' }
		});
		await fireEvent.click(screen.getByRole('checkbox', { name: 'Include retired' }));
		await waitFor(() => expect(document.querySelectorAll('.chapter')).toHaveLength(3));
		await fireEvent.click(screen.getByRole('checkbox', { name: 'Include retired' }));
		await view.rerender({ ...props(repository(files)), requestedPath: `${prefix}-retired` });
		await waitFor(() =>
			expect(
				document.getElementById(
					documentAnchor(`docs/packages/registered/${dir}/${prefix}-retired.md`)
				)
			).not.toBeNull()
		);
		expect(document.querySelectorAll('.chapter')).toHaveLength(2);
		expect(
			(screen.getByRole('checkbox', { name: 'Include retired' }) as HTMLInputElement).checked
		).toBe(false);
	});
	it('reads a moved parent by alias, independent detail, supporting formats, missing old artifact and raw/Back', async () => {
		const path = `docs/packages/registered/${dir}/${prefix}-new.md`,
			artifact = `docs/packages/registered/${dir}/${prefix}-new/artifacts/data sheet.csv`;
		const files = {
			[path]: page(
				`${prefix}-new`,
				`![Chart](${prefix}-new/artifacts/chart.png)\n\n[Example](${prefix}-new/artifacts/example.md)\n\n[Binary](${prefix}-new/artifacts/data.bin)\n\n[Data sheet](${prefix}-new/artifacts/data%20sheet.csv#row%202)\n\n[Gone](${prefix}-old/artifacts/data%20sheet.csv)\n\n[${prefix}-detail]`,
				`aliases: [${prefix}-old]\n`
			),
			[`docs/packages/registered/${dir}/${prefix}-detail.md`]: page(
				`${prefix}-detail`,
				'Independent detail.'
			),
			[artifact]: 'name,value\nalpha,42',
			[`docs/packages/registered/${dir}/${prefix}-new/artifacts/example.md`]: `# Parent-owned example\n\nSupport owned by ${prefix}-new.\n\n\`\`\`mermaid\ngraph TD\nA-->B\n\`\`\``,
			[`docs/packages/registered/${dir}/${prefix}-new/artifacts/chart.png`]:
				'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGP4z8DwHwAFAAH/iZk9HQAAAABJRU5ErkJggg==',
			[`docs/packages/registered/${dir}/${prefix}-new/artifacts/data.bin`]: btoa(
				String.fromCharCode(255, 254)
			)
		};
		const source = repository(files);
		render(KnowledgeViews, props(source, `${prefix}-old`));
		await waitFor(() => expect(document.querySelectorAll('.chapter')).toHaveLength(2));
		const chapter = document.getElementById(documentAnchor(path))!;
		await waitFor(() =>
			expect(within(chapter).getByRole('img', { name: 'Chart' }).getAttribute('src')).toMatch(
				/^blob:/
			)
		);
		await fireEvent.click(within(chapter).getByRole('button', { name: 'View raw' }));
		expect(chapter.textContent).toContain('aliases:');
		await fireEvent.click(within(chapter).getByRole('button', { name: 'Rendered' }));
		await fireEvent.click(within(chapter).getByRole('link', { name: 'Data sheet' }));
		await screen.findByText(/name,value\s+alpha,42/);
		expect(source.blob).toHaveBeenCalledWith(artifact, expect.anything());
		await fireEvent.click(screen.getByRole('button', { name: `Back to ${prefix}-new` }));
		await fireEvent.click(within(chapter).getByRole('link', { name: 'Example' }));
		await screen.findByRole('heading', { name: 'Parent-owned example' });
		expect(document.querySelector('.supporting-artifact .language-mermaid')?.textContent).toContain(
			'A-->B'
		);
		await fireEvent.click(screen.getByRole('button', { name: `Back to ${prefix}-new` }));
		await fireEvent.click(within(chapter).getByRole('link', { name: 'Binary' }));
		await screen.findByText(/Unsupported preview format/);
		expect(screen.getByRole('link', { name: 'Download file' })).toBeTruthy();
		await fireEvent.click(screen.getByRole('button', { name: `Back to ${prefix}-new` }));
		await fireEvent.click(within(chapter).getByRole('link', { name: 'Gone' }));
		await screen.findByText(/File unavailable:.*old\/artifacts/);
		await fireEvent.click(screen.getByRole('button', { name: `Back to ${prefix}-new` }));
		await fireEvent.click(within(chapter).getByRole('link', { name: `[${prefix}-detail]` }));
		await screen.findByRole('button', { name: 'Back to previous document' });
		await fireEvent.click(screen.getByRole('button', { name: 'Back to previous document' }));
		expect(source.treeRecursive).toHaveBeenCalledTimes(2);
	});
	it('cold Files shares canonical/alias links and current incoming/outgoing context before book', async () => {
		const path = `docs/${dir}/${prefix}-node.md`;
		const source = repository({
			[path]: page(`${prefix}-node`, 'See [CAP-A-owner].', 'related_capabilities: [CAP-A-owner]\n'),
			'docs/capabilities/a/CAP-A-owner.md': page('CAP-A-owner', `See [${prefix}-alias].`)
		});
		// Current node gains an identity alias; no alias graph edge is created.
		const original = source.blob;
		source.blob = vi.fn(async (path: string, signal: AbortSignal) => {
			const blob = await original(path, signal);
			return path.endsWith(`${prefix}-node.md`)
				? {
						...blob,
						content: blob.content.replace(
							'status: active',
							'status: active\naliases: [' + prefix + '-alias]'
						)
					}
				: blob;
		});
		render(SddViewer, { dataSource: source });
		await openFile(path);
		const panel = await screen.findByRole('complementary', {
			name: `References for ${prefix}-node`
		});
		await waitFor(() =>
			expect(within(panel).getAllByRole('button', { name: /CAP-A-owner/ }).length).toBe(3)
		);
		const link = document.querySelector<HTMLAnchorElement>(
			'.content-viewport article a[data-doc-path]'
		)!;
		expect(link.textContent).toBe('[CAP-A-owner]');
		await fireEvent.click(link);
		await screen.findAllByRole('heading', { name: 'CAP-A-owner title' });
	});
	it('keeps missing and ambiguous written direct IDs explicit', async () => {
		const files = {
			[`docs/${dir}/${prefix}-one.md`]: page(
				`${prefix}-one`,
				'',
				`aliases: [${prefix}-ambiguous]\n`
			),
			[`docs/${dir}/${prefix}-two.md`]: page(
				`${prefix}-two`,
				'',
				`aliases: [${prefix}-ambiguous]\n`
			)
		};
		render(KnowledgeViews, props(repository(files), `${prefix}-ambiguous`));
		await screen.findByText(`${prefix}-ambiguous — unavailable (ambiguous)`);
	});
});
it('keeps raw, supporting-file and handbook reads outside the identity-index budget', async () => {
	const files = {
		'docs/plain.md': '---\nrelated_designs: [DESIGN-x]\n---\n# Plain',
		'docs/designs/DESIGN-x.md': page('DESIGN-x'),
		'docs/designs/DESIGN-x/artifacts/table.csv': 'a,b\n1,2'
	};
	const source = repository(files);
	render(SddViewer, { dataSource: source });
	await openFile('docs/plain.md');
	await screen.findByRole('heading', { name: 'Plain' });
	await fireEvent.click(screen.getByRole('button', { name: '📝 Raw' }));
	await openFile('docs/designs/DESIGN-x.md');
	await waitFor(() =>
		expect(
			document.querySelector('.raw-viewer')?.textContent ??
				document.querySelector('pre')?.textContent
		).toContain('DESIGN-x')
	);
	expect(source.treeRecursive).not.toHaveBeenCalled();
	await openFile('docs/designs/DESIGN-x/artifacts/table.csv');
	await screen.findByText(/a,b\s+1,2/);
	expect(source.treeRecursive).not.toHaveBeenCalled();
});
it.each(roles)(
	'%s cold Files exposes incomplete index/retry and replaces stale source responses',
	async (prefix, dir) => {
		const path = `docs/${dir}/${prefix}-node.md`,
			files = {
				[path]: page(`${prefix}-node`, '', 'related_capabilities: [CAP-A-owner]\n'),
				'docs/capabilities/a/CAP-A-owner.md': page('CAP-A-owner', `[${prefix}-node]`)
			};
		const source = repository(files);
		let failed = true;
		const list = source.treeRecursive;
		source.treeRecursive = vi.fn(async (root: string, signal: AbortSignal) => {
			if (root === 'docs' && failed) throw new Error('Read denied');
			return list(root, signal);
		});
		render(SddViewer, { dataSource: source });
		await openFile(path);
		await screen.findByText('Incomplete reference information');
		expect(screen.getByText(/Read denied/)).toBeTruthy();
		failed = false;
		await fireEvent.click(screen.getByRole('button', { name: 'Reload references' }));
		await waitFor(() => expect(screen.queryByText('Incomplete reference information')).toBeNull());
		await waitFor(() =>
			expect(document.querySelectorAll('.formal-references button').length).toBe(2)
		);
	}
);
it.each(
	roles.flatMap(([prefix, dir]) => [
		[prefix, dir, 'CAP-A-owner', 'docs/capabilities/a/CAP-A-owner.md'],
		[prefix, dir, 'UC-owner', 'docs/usecases/a/UC-owner.md'],
		[prefix, dir, 'MAT-owner', 'docs/materials/MAT-owner.md']
	])
)(
	'an indexed %s role relation on %s/%s has a usable shared Files route',
	async (prefix, dir, owner, path) => {
		const field: Record<string, string> = {
			DESIGN: 'related_designs',
			DOMAIN: 'related_domains',
			OPS: 'related_operations'
		};
		const files = {
			[path]: page(owner, '', `${field[prefix]}: [${prefix}-node]\n`),
			[`docs/${dir}/${prefix}-node.md`]: page(`${prefix}-node`)
		};
		render(SddViewer, { dataSource: repository(files) });
		await openFile(path);
		const panel = await screen.findByRole('complementary', { name: `References for ${owner}` });
		const target = await within(panel).findByRole('button', {
			name: `${prefix}-node — ${prefix}-node title`
		});
		await fireEvent.click(target);
		await screen.findByRole('complementary', { name: `References for ${prefix}-node` });
	}
);
it('never indexes a no-ID typed declaration, ID-bearing artifact or handbook file', async () => {
	const files = {
		'docs/no-id.md': '---\nrelated_designs: [DESIGN-x]\n---\n# No ID',
		'docs/designs/DESIGN-x/artifacts/invalid.md': page('ADR-not-a-canonical-decision'),
		'handbook/en/README.md': page('DESIGN-not-a-handbook-identity')
	};
	const source = repository(files);
	const listing = source.tree;
	// The root listing names the handbook page, which lies outside `docs`.
	source.tree = vi.fn(async (path: string, signal: AbortSignal) =>
		path
			? listing(path, signal)
			: { items: [{ name: 'README.md', path: 'handbook/en/README.md', type: 'blob' }] }
	);
	render(SddViewer, { dataSource: source });
	await openFile('docs/no-id.md');
	await screen.findByRole('heading', { name: 'No ID' });
	expect(source.treeRecursive).not.toHaveBeenCalled();
	await openFile('docs/designs/DESIGN-x/artifacts/invalid.md');
	await screen.findByText('Format: text/markdown');
	expect(source.treeRecursive).not.toHaveBeenCalled();
	// The handbook lies outside `docs`: open it from the root listing.
	await fireEvent.click(screen.getByRole('button', { name: 'root' }));
	await fireEvent.click(
		await waitFor(() => {
			const node = [...document.querySelectorAll<HTMLButtonElement>('.tree-node')].find(
				(button) => button.querySelector('.node-name')?.textContent === 'README.md'
			);
			if (!node) throw new Error('no handbook entry');
			return node;
		})
	);
	await screen.findAllByRole('heading', { name: 'DESIGN-not-a-handbook-identity title' });
	expect(source.treeRecursive).not.toHaveBeenCalled();
});

it('reads the four retained formal documents and their real capability ingress through shared book routes', async () => {
	const capability = 'docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md';
	const detail =
		'docs/designs/distribution/DESIGN-distribution-file-directory-replacement/design.md';
	const bundleDomain = 'docs/domain/distribution/DOMAIN-bundle-selection-and-installation.md';
	const deliveryDomain = 'docs/domain/delivery/DOMAIN-delivery-relationships.md';
	const operations = 'docs/operations/OPS-distribution-sync.md';
	const paths = [capability, detail, bundleDomain, deliveryDomain, operations];
	const files = Object.fromEntries(
		paths.map((path) => [
			path,
			readFileSync(new URL('../../../../../../' + path, import.meta.url), 'utf-8')
		])
	);
	const documents = paths.map((path) => parseBlob(path, files[path], 'utf-8'));
	expect(documents.slice(1).map((doc) => [doc.meta.id, bookGroup(doc)])).toEqual([
		['DESIGN-distribution-file-directory-replacement', 'Designs'],
		['DOMAIN-bundle-selection-and-installation', 'Domain'],
		['DOMAIN-delivery-relationships', 'Domain'],
		['OPS-distribution-sync', 'Operations']
	]);
	render(KnowledgeViews, props(repository(files), 'CAP-DIST-sync-and-transactions'));
	await waitFor(() => expect(document.querySelectorAll('.chapter')).toHaveLength(5));
	await waitFor(() => expect(scrolledTo()).toBe(documentAnchor(capability)));
	const chapter = (path: string) => document.getElementById(documentAnchor(path))!;
	const follow = async (origin: string, destination: string) => {
		const link = chapter(origin).querySelector<HTMLAnchorElement>(
			`article a[data-doc-path="${destination}"]`
		);
		expect(link).toBeTruthy();
		await fireEvent.click(link!);
		await waitFor(() => expect(scrolledTo()).toBe(documentAnchor(destination)));
	};
	await follow(capability, detail);
	expect(chapter(detail).textContent).toContain('apply_changes');
	await follow(detail, capability);
	await follow(capability, bundleDomain);
	expect(chapter(bundleDomain).textContent).toContain('Installation receipt');
	const outline = screen.getByRole('complementary', { name: 'Table of contents' });
	await fireEvent.click(
		within(outline).getByRole('button', { name: /DOMAIN-delivery-relationships/ })
	);
	await waitFor(() => expect(scrolledTo()).toBe(documentAnchor(deliveryDomain)));
	expect(chapter(deliveryDomain).textContent).toContain('Milestone membership');
	await fireEvent.click(within(outline).getByRole('button', { name: /OPS-distribution-sync/ }));
	await waitFor(() => expect(scrolledTo()).toBe(documentAnchor(operations)));
	expect(chapter(operations).textContent).toContain('TRANSACTION_PENDING');
	await follow(operations, capability);
});

it('lists current bundle support at every depth without creating identities or rereading its tree', async () => {
	const parent = 'docs/designs/alpha/DESIGN-parent/design.md';
	const support = 'docs/designs/alpha/DESIGN-parent/examples/deep/table.csv';
	const stray = 'docs/designs/alpha/DESIGN-parent/examples/stray.md';
	const source = repository({
		[parent]: page('DESIGN-parent', '[DESIGN-peer]', 'area: alpha\n'),
		'docs/designs/beta/DESIGN-peer/design.md': page('DESIGN-peer', '', 'area: beta\n'),
		[support]: 'a,b\n1,2',
		[stray]: page('CAP-X-fake'),
		'docs/designs/alpha/DESIGN-parent/README.md': '# Support readme',
		'docs/designs/alpha/DESIGN-parent/nested/DESIGN-child/design.md': page('DESIGN-child'),
		'docs/designs/alpha/DESIGN-orphan/note.md': page('DOMAIN-fake'),
		'docs/domain/alpha/DOMAIN-real.md': page('DOMAIN-real', '', 'area: alpha\n'),
		'docs/domain/alpha/DOMAIN-real/artifacts/example.md': page('ADR-fake'),
		'docs/operations/OPS-real.md': page('OPS-real'),
		'docs/operations/OPS-real/artifacts/example.csv': 'x,y'
	});
	render(KnowledgeViews, props(source, 'DESIGN-parent'));
	await waitFor(() => expect(document.querySelectorAll('.chapter')).toHaveLength(4));
	const chapter = document.getElementById(documentAnchor(parent))!;
	const panel = within(chapter).getByRole('complementary', {
		name: 'References for DESIGN-parent'
	});
	expect(within(panel).getByRole('button', { name: 'examples/stray.md' })).toBeTruthy();
	expect(within(panel).getByRole('button', { name: 'README.md' })).toBeTruthy();
	expect(within(panel).getByRole('button', { name: 'nested/DESIGN-child/design.md' })).toBeTruthy();
	expect(screen.getAllByRole('heading', { name: 'alpha' }).length).toBeGreaterThan(0);
	expect(screen.getAllByRole('heading', { name: 'beta' }).length).toBeGreaterThan(0);
	expect(source.blob).not.toHaveBeenCalledWith(stray, expect.anything());
	const reads = vi.mocked(source.treeRecursive).mock.calls.length;
	await fireEvent.click(within(panel).getByRole('button', { name: 'examples/deep/table.csv' }));
	await screen.findByText(/a,b\s+1,2/);
	await fireEvent.click(screen.getByRole('button', { name: 'Back to DESIGN-parent' }));
	expect(vi.mocked(source.treeRecursive).mock.calls.length).toBe(reads);
});

const currentPath = (prefix: string, dir: string, id: string, root = 'docs', area = 'alpha') =>
	prefix === 'DESIGN'
		? `${root}/${dir}/${area}/${id}/design.md`
		: prefix === 'DOMAIN'
			? `${root}/${dir}/${area}/${id}.md`
			: `${root}/${dir}/${id}.md`;
const currentSupport = (prefix: string, path: string, id: string) =>
	prefix === 'DESIGN'
		? path.slice(0, -9)
		: path.slice(0, path.lastIndexOf('/') + 1) + id + '/artifacts/';

it.each(
	roles.flatMap(([prefix, dir]) =>
		['docs', 'docs/packages/registered'].map((root) => [prefix, dir, root])
	)
)(
	'%s current grammar in %s/%s preserves cold Files, support, graph, alias and source budgets',
	async (prefix, dir, root) => {
		const id = prefix + '-current',
			path = currentPath(prefix, dir, id, root);
		const support = currentSupport(prefix, path, id) + 'examples/deep/data sheet.csv';
		const source = repository({
			[path]: page(
				id,
				'[CAP-A-owner]',
				`aliases: [${prefix}-previous]\n${prefix === 'OPS' ? '' : 'area: alpha\n'}related_capabilities: [CAP-A-owner]\n`
			),
			[support]: 'name,value\nalpha,42',
			'docs/capabilities/a/CAP-A-owner.md': page('CAP-A-owner', `[${prefix}-previous]`)
		});
		const view = render(SddViewer, { dataSource: source, branch: 'release' });
		await openFile(path);
		const panel = await screen.findByRole('complementary', { name: `References for ${id}` });
		await within(panel).findByRole('button', { name: 'examples/deep/data sheet.csv' });
		await waitFor(() =>
			expect(within(panel).getAllByRole('button', { name: /CAP-A-owner/ })).toHaveLength(3)
		);
		const reads = vi.mocked(source.treeRecursive).mock.calls.length;
		await fireEvent.click(
			within(panel).getByRole('button', { name: 'examples/deep/data sheet.csv' })
		);
		await screen.findByText(/name,value\s+alpha,42/);
		expect(source.blob).toHaveBeenCalledWith(support, expect.anything());
		await fireEvent.click(screen.getByRole('button', { name: `Back to ${id}` }));
		await screen.findByRole('complementary', { name: `References for ${id}` });
		expect(vi.mocked(source.treeRecursive).mock.calls.length).toBe(reads);
		view.unmount();
		const bookProps = props(source, prefix + '-previous');
		bookProps.branch = 'release';
		render(KnowledgeViews, bookProps);
		await waitFor(() => expect(scrolledTo()).toBe(documentAnchor(path)));
		expect(vi.mocked(source.treeRecursive).mock.calls.length).toBe(reads);
	}
);

it.each(['DESIGN', 'DOMAIN'])(
	'%s area moves keep identity while bundle rename/root moves retain aliases and reject stale paths',
	async (prefix) => {
		const dir = prefix === 'DESIGN' ? 'designs' : 'domain';
		const oldPath = currentPath(prefix, dir, prefix + '-before');
		const moved = currentPath(prefix, dir, prefix + '-after', 'docs/packages/registered', 'beta');
		const areaMoved = currentPath(prefix, dir, prefix + '-stable', 'docs', 'beta');
		const support = currentSupport(prefix, moved, prefix + '-after') + 'table.csv';
		const source = repository({
			[moved]: page(
				prefix + '-after',
				`[${prefix}-stable]`,
				`aliases: [${prefix}-before]\narea: beta\n`
			),
			[areaMoved]: page(prefix + '-stable', '', 'area: beta\n'),
			[support]: 'moved,data',
			'docs/capabilities/a/CAP-A-owner.md': page(
				'CAP-A-owner',
				`[${prefix}-before] [${prefix}-stable]`
			)
		});
		const view = render(KnowledgeViews, props(source, prefix + '-before'));
		await waitFor(() => expect(document.getElementById(documentAnchor(moved))).toBeTruthy());
		expect(document.getElementById(documentAnchor(areaMoved))).toBeTruthy();
		expect(screen.getByRole('option', { name: 'registered + Global' })).toBeTruthy();
		const panel = screen.getByRole('complementary', { name: `References for ${prefix}-after` });
		await fireEvent.click(within(panel).getByRole('button', { name: 'table.csv' }));
		await screen.findByText('moved,data');
		await fireEvent.click(screen.getByRole('button', { name: `Back to ${prefix}-after` }));
		await view.rerender({ ...props(source, oldPath) });
		await screen.findByText(`${oldPath} — unavailable (missing)`);
	}
);

it('cold Files reads an identified bundle support file without scanning identities', async () => {
	const path = 'docs/packages/registered/designs/alpha/DESIGN-parent/examples/stray.md';
	const source = repository({ [path]: page('CAP-X-stray') });
	render(SddViewer, { dataSource: source });
	await openFile(path);
	await screen.findByText('Format: text/markdown');
	expect(source.treeRecursive).not.toHaveBeenCalled();
	expect(screen.queryByRole('complementary', { name: 'References for CAP-X-stray' })).toBeNull();
});
