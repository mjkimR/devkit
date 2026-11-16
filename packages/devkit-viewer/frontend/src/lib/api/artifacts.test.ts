import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
	blobBytes,
	classifyFile,
	fileUrl,
	readSupportingFile,
	repositoryImages,
	ARTIFACT_MAX_BYTES
} from './artifacts';
import { parseBlob, renderDocument, resolvePath } from './documents';
import type { RepositoryDataSource } from './repository';
const source = (content: string, encoding = 'utf-8') =>
	({
		info: async () => ({}),
		tree: async () => [],
		blob: vi.fn(async () => ({ content, encoding }))
	}) satisfies RepositoryDataSource;
beforeEach(() => {
	URL.createObjectURL = vi.fn(() => `blob:test-${Math.random()}`);
	URL.revokeObjectURL = vi.fn();
});
afterEach(() => vi.restoreAllMocks());
describe('repository supporting files', () => {
	it('preserves raster and unsupported binary bytes without UTF-8 coercion', async () => {
		const bytes = Uint8Array.of(137, 80, 78, 71, 255, 0);
		const encoded = btoa(String.fromCharCode(...bytes));
		const image = await readSupportingFile(
			source(encoded, 'base64'),
			'docs/designs/DESIGN-x/artifacts/chart.png',
			'branch',
			new AbortController().signal
		);
		expect(image.bytes).toEqual(bytes);
		expect(image.kind).toBe('image');
		expect(image.text).toBeNull();
		expect(classifyFile('docs/data.bin', bytes).kind).toBe('unsupported');
		expect(blobBytes('한글', 'utf-8')).toEqual(new TextEncoder().encode('한글'));
	});
	it('reads Markdown, CSV and diagrams as source and refuses malformed encodings/oversize', () => {
		for (const [path, kind] of [
			['example.md', 'markdown'],
			['data.csv', 'text'],
			['graph.mmd', 'text']
		])
			expect(classifyFile(path, new TextEncoder().encode('a,b\n1,2')).kind).toBe(kind);
		expect(() => blobBytes('bad', 'rot13')).toThrow('Unsupported encoding');
		expect(() => blobBytes('x'.repeat(ARTIFACT_MAX_BYTES + 1), 'utf-8')).toThrow('limit');
		expect(() => classifyFile('bad.md', Uint8Array.of(255))).toThrow('UTF-8');
	});
	it('never reads escape/git paths and preserves encoded relative fragments', async () => {
		const repository = source('text');
		for (const path of ['../escape', '/absolute', '.git/config', 'docs/../secret', 'docs\\secret'])
			await expect(
				readSupportingFile(repository, path, 'main', new AbortController().signal)
			).rejects.toThrow('path');
		expect(repository.blob).not.toHaveBeenCalled();
		expect(
			resolvePath('docs/designs/DESIGN-x.md', 'DESIGN-x/artifacts/data%20sheet.csv#row%202')
		).toEqual({ path: 'docs/designs/DESIGN-x/artifacts/data sheet.csv', fragment: 'row 2' });
		expect(resolvePath('docs/a.md', '../.git/config')).toBeNull();
	});
	it('clears relative img/src and srcset before assigning HTML in the live document', () => {
		const descriptor = Object.getOwnPropertyDescriptor(Element.prototype, 'innerHTML')!;
		const setter = vi.spyOn(Element.prototype, 'innerHTML', 'set').mockImplementation(function (
			this: Element,
			value: string
		) {
			if (this.ownerDocument === document && this.tagName === 'DIV')
				expect(value).not.toMatch(/<img[^>]+(?:src|srcset)=["'](?:\.\.?\/|artifacts\/)/);
			descriptor.set!.call(this, value);
		});
		const html = renderDocument(
			parseBlob(
				'docs/designs/DESIGN-x.md',
				'![chart](artifacts/chart.png) <img src="artifacts/other.png" srcset="artifacts/leak.png 2x">',
				'utf-8'
			),
			[]
		).html;
		setter.mockRestore();
		expect(html).not.toContain('src=');
		expect(html).not.toContain('srcset');
		expect(html).toContain('data-repo-image="docs/designs/artifacts/chart.png"');
	});
	it('hydrates only source blobs, aborts late results and revokes created object URLs', async () => {
		const root = document.createElement('div');
		root.innerHTML = '<img data-repo-image="docs/p.png">';
		const repository = source(btoa('PNG'), 'base64');
		const action = repositoryImages(root, { source: repository, branch: 'feature' });
		await vi.waitFor(() => expect(root.querySelector('img')?.src).toContain('blob:test'));
		expect(repository.blob).toHaveBeenCalledWith('docs/p.png', 'feature', expect.anything());
		action.destroy();
		expect(URL.revokeObjectURL).toHaveBeenCalledTimes(1);
		let release!: (blob: any) => void;
		const pending = { ...repository, blob: vi.fn(() => new Promise<any>((r) => (release = r))) };
		const other = document.createElement('div');
		other.innerHTML = '<img data-repo-image="docs/late.png">';
		const cancelled = repositoryImages(other, { source: pending, branch: 'old' });
		cancelled.destroy();
		release({ content: btoa('PNG'), encoding: 'base64' });
		await new Promise((r) => setTimeout(r, 0));
		expect(other.querySelector('img')?.hasAttribute('src')).toBe(false);
	});
	it('sanitizes SVG scripts, external resources and CSS before preview', async () => {
		let blob!: Blob;
		vi.mocked(URL.createObjectURL).mockImplementation((value) => {
			blob = value as Blob;
			return 'blob:safe';
		});
		fileUrl(
			classifyFile(
				'docs/x.svg',
				new TextEncoder().encode(
					'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script><image href="https://evil/x"/><path style="fill:url(https://evil)" d="M0 0"/></svg>'
				)
			),
			true
		);
		const text = await new Promise<string>((resolve) => {
			const reader = new FileReader();
			reader.onload = () => resolve(String(reader.result));
			reader.readAsText(blob);
		});
		expect(text).not.toMatch(/script|https:\/\/evil|style=/);
		expect(text).toContain('<path');
	});
});
it('does not trust authored renderer markers or picture srcset', () => {
	const html = renderDocument(
		parseBlob(
			'docs/a.md',
			'<a data-doc-path=".git/config" href="../.git/config">Secret</a><picture><source srcset="relative.png"><img src="relative.png" data-repo-image=".git/config"></picture>',
			'utf-8'
		),
		[]
	).html;
	expect(html).not.toContain('data-doc-path=".git/config"');
	expect(html).not.toContain('data-repo-image=".git/config"');
	expect(html).not.toContain('srcset');
	expect(html).not.toContain('<source');
	expect(html).toContain('data-repo-image="docs/relative.png"');
});
it('preserves the encoded SVG view fragment on preview URLs while reading only its source path', async () => {
	vi.mocked(URL.createObjectURL).mockReturnValue('blob:svg-view');
	const root = document.createElement('div');
	root.innerHTML = renderDocument(
		parseBlob(
			'docs/designs/DESIGN-x.md',
			'![diagram](DESIGN-x/artifacts/figure.svg#named%20view)',
			'utf-8'
		),
		[]
	).html;
	expect(root.querySelector('img')?.hasAttribute('src')).toBe(false);
	const repository = source(
		'<svg xmlns="http://www.w3.org/2000/svg"><view id="named view" viewBox="0 0 10 10"/></svg>'
	);
	const action = repositoryImages(root, { source: repository, branch: 'planning-ref' });
	await vi.waitFor(() => expect(root.querySelector('img')?.src).toBe('blob:svg-view#named%20view'));
	expect(repository.blob).toHaveBeenCalledWith(
		'docs/designs/DESIGN-x/artifacts/figure.svg',
		'planning-ref',
		expect.anything()
	);
	action.destroy();
	expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:svg-view');
});
