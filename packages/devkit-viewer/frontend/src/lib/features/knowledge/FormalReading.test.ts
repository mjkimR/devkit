import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/svelte';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import KnowledgeViews from './KnowledgeViews.svelte';
import SddViewer from '../../SddViewer.svelte';
import { documentAnchor, parseBlob, bookGroup } from '../../api/documents';
import { readFileSync } from 'node:fs';
import type { RepositoryDataSource } from '../../api/repository';
const roles = [
	['DESIGN', 'designs'],
	['DOMAIN', 'domain'],
	['OPS', 'operations']
] as const;
const page = (id: string, body = '', extra = '') =>
	`---\nid: ${id}\ntitle: ${id} title\nsummary: "${id} example"\nstatus: active\n${extra}---\n# [${id}] ${id} title\n\n${body}`;
function repository(files: Record<string, string>): RepositoryDataSource {
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
	return {
		info: async () => ({ default_branch: 'main' }),
		tree: vi.fn(async (path) => listing(path)),
		treeRecursive: vi.fn(async (path) => listing(path)),
		blob: vi.fn(async (path) => {
			if (!(path in files)) throw new Error('HTTP 404: Not Found');
			return {
				path,
				content: files[path],
				encoding: /\.(png|bin)$/.test(path) ? 'base64' : 'utf-8'
			};
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
		expect(source.blob).toHaveBeenCalledWith(artifact, 'main', expect.anything());
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
		source.blob = vi.fn(async (path, ref, signal) => {
			const blob = await original(path, ref, signal);
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
		render(SddViewer, { dataSource: source, initialView: 'files', initialPath: path });
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
	const view = render(SddViewer, {
		dataSource: source,
		initialView: 'files',
		initialPath: 'docs/plain.md'
	});
	await screen.findByRole('heading', { name: 'Plain' });
	await fireEvent.click(screen.getByRole('button', { name: '📝 Raw' }));
	await view.rerender({
		dataSource: source,
		initialView: 'files',
		initialPath: 'docs/designs/DESIGN-x.md'
	});
	await waitFor(() =>
		expect(
			document.querySelector('.raw-viewer')?.textContent ??
				document.querySelector('pre')?.textContent
		).toContain('DESIGN-x')
	);
	expect(source.treeRecursive).not.toHaveBeenCalled();
	await view.rerender({
		dataSource: source,
		initialView: 'files',
		initialPath: 'docs/designs/DESIGN-x/artifacts/table.csv'
	});
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
		const list = source.treeRecursive!;
		source.treeRecursive = vi.fn(async (root, ref, signal) => {
			if (root === 'docs' && failed) throw new Error('Read denied');
			return list(root, ref, signal);
		});
		render(SddViewer, { dataSource: source, initialView: 'files', initialPath: path });
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
		render(SddViewer, { dataSource: repository(files), initialView: 'files', initialPath: path });
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
	const view = render(SddViewer, {
		dataSource: source,
		initialView: 'files',
		initialPath: 'docs/no-id.md'
	});
	await screen.findByRole('heading', { name: 'No ID' });
	expect(source.treeRecursive).not.toHaveBeenCalled();
	await view.rerender({
		dataSource: source,
		initialView: 'files',
		initialPath: 'docs/designs/DESIGN-x/artifacts/invalid.md'
	});
	await screen.findByText('Format: text/markdown');
	expect(source.treeRecursive).not.toHaveBeenCalled();
	await view.rerender({
		dataSource: source,
		initialView: 'files',
		initialPath: 'handbook/en/README.md'
	});
	await screen.findAllByRole('heading', { name: 'DESIGN-not-a-handbook-identity title' });
	expect(source.treeRecursive).not.toHaveBeenCalled();
});

it('reads the five retained formal documents and their real capability ingress through shared book routes', async () => {
	const capability = 'docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md';
	const design = 'docs/designs/DESIGN-distribution-transactions.md';
	const detail = 'docs/designs/DESIGN-distribution-file-directory-replacement.md';
	const bundleDomain = 'docs/domain/DOMAIN-bundle-selection-and-installation.md';
	const deliveryDomain = 'docs/domain/DOMAIN-delivery-relationships.md';
	const operations = 'docs/operations/OPS-distribution-sync.md';
	const paths = [capability, design, detail, bundleDomain, deliveryDomain, operations];
	const files = Object.fromEntries(
		paths.map((path) => [
			path,
			readFileSync(new URL('../../../../../../../' + path, import.meta.url), 'utf-8')
		])
	);
	const documents = paths.map((path) => parseBlob(path, files[path], 'utf-8'));
	expect(documents.slice(1).map((doc) => [doc.meta.id, bookGroup(doc)])).toEqual([
		['DESIGN-distribution-transactions', 'Designs'],
		['DESIGN-distribution-file-directory-replacement', 'Designs'],
		['DOMAIN-bundle-selection-and-installation', 'Domain'],
		['DOMAIN-delivery-relationships', 'Domain'],
		['OPS-distribution-sync', 'Operations']
	]);
	const view = props(repository(files), 'CAP-DIST-sync-and-transactions');
	render(KnowledgeViews, view);
	await waitFor(() => expect(document.querySelectorAll('.chapter')).toHaveLength(6));
	await waitFor(() =>
		expect(view.onLocation).toHaveBeenCalledWith(
			capability,
			expect.any(String),
			'book',
			expect.objectContaining({ id: 'CAP-DIST-sync-and-transactions' })
		)
	);
	const chapter = (path: string) => document.getElementById(documentAnchor(path))!;
	const follow = async (origin: string, destination: string, id: string) => {
		const link = chapter(origin).querySelector<HTMLAnchorElement>(
			`article a[data-doc-path="${destination}"]`
		);
		expect(link).toBeTruthy();
		await fireEvent.click(link!);
		await waitFor(() =>
			expect(view.onLocation).toHaveBeenLastCalledWith(
				destination,
				expect.any(String),
				'book',
				expect.objectContaining({ id })
			)
		);
	};
	await follow(capability, design, 'DESIGN-distribution-transactions');
	await follow(design, detail, 'DESIGN-distribution-file-directory-replacement');
	expect(chapter(detail).textContent).toContain('apply_changes');
	await follow(detail, capability, 'CAP-DIST-sync-and-transactions');
	await follow(capability, bundleDomain, 'DOMAIN-bundle-selection-and-installation');
	expect(chapter(bundleDomain).textContent).toContain('Installation receipt');
	const outline = screen.getByRole('complementary', { name: 'Table of contents' });
	await fireEvent.click(
		within(outline).getByRole('button', { name: /DOMAIN-delivery-relationships/ })
	);
	await waitFor(() =>
		expect(view.onLocation).toHaveBeenLastCalledWith(
			deliveryDomain,
			expect.any(String),
			'book',
			expect.objectContaining({ id: 'DOMAIN-delivery-relationships' })
		)
	);
	expect(chapter(deliveryDomain).textContent).toContain('Milestone membership');
	await fireEvent.click(within(outline).getByRole('button', { name: /OPS-distribution-sync/ }));
	await waitFor(() =>
		expect(view.onLocation).toHaveBeenLastCalledWith(
			operations,
			expect.any(String),
			'book',
			expect.objectContaining({ id: 'OPS-distribution-sync' })
		)
	);
	expect(chapter(operations).textContent).toContain('TRANSACTION_PENDING');
	await follow(operations, capability, 'CAP-DIST-sync-and-transactions');
});
