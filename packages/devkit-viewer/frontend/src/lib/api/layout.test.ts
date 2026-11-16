import { describe, expect, it, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { parseBlob, indexDocuments, namespaceOf } from './documents';
import { isArtifactPath, identityResolver, formalArea, supportRoot } from './identity';
import type { RepositoryDataSource } from './repository';

it('pins delivered Kind rows and preserves the immutable Planning pin', () => {
	const root = '../../../../../../';
	const rows = readFileSync(
		new URL(
			root + 'packages/devkit-docs/src/devkit_docs/features/documents/models/kinds.py',
			import.meta.url
		),
		'utf-8'
	);
	for (const [kind, layout, anchor] of [
		['DESIGN', 'AREA_BUNDLE', 'design.md'],
		['DOMAIN', 'AREA', ''],
		['OPERATIONS', 'FLAT', '']
	]) {
		const row = rows.split(`Kind.${kind},`)[1].split('KindDefinition(')[0];
		expect(row).toContain(`layout=Layout.${layout},`);
		expect(row).toContain(`layout_anchor="${anchor}"`);
		expect(row).toContain('living_spec=True');
	}
	const historical = readFileSync(
		new URL(
			root + 'docs/materials/2026-11/20261116-design-document-viewer/core-contract.md',
			import.meta.url
		)
	);
	expect(createHash('sha256').update(historical).digest('hex')).toBe(
		'1d724834426991e04904fd9f1677f60235de49764d9a1863ad9c8d112c55f413'
	);
});

describe.each(['docs', 'docs/packages/registered'])('%s bundle projection', (root) => {
	const parent = `${root}/designs/alpha/DESIGN-parent/design.md`;
	const support = [
		'notes.md',
		'README.md',
		'examples/deep/table.csv',
		'image.png',
		'DESIGN-nested/design.md'
	].map((p) => `${root}/designs/alpha/DESIGN-parent/${p}`);
	it('keeps every non-anchor file outside the identity registry, including stray IDs, nested anchors and orphans', () => {
		for (const path of support) expect(isArtifactPath(path)).toBe(true);
		expect(isArtifactPath(parent)).toBe(false);
		const documents = [parent, ...support, `${root}/designs/beta/DESIGN-orphan/stray.md`].map(
			(path, i) =>
				parseBlob(path, `---\nid: ${i ? 'CAP-X-fake' : 'DESIGN-parent'}\n---\n# Example`, 'utf-8')
		);
		expect(identityResolver(documents).resolve('CAP-X-fake').document).toBeNull();
		expect(identityResolver(documents).resolve('DESIGN-parent').document?.path).toBe(parent);
		expect(formalArea(documents[0])).toBe('alpha');
		expect(supportRoot(documents[0])).toBe(parent.slice(0, -9));
		expect(namespaceOf(documents[0])).toBe(root === 'docs' ? 'global' : 'registered');
	});
	it('collects all tree files once without reading supporting blobs, also with only the generic tree callback', async () => {
		const files = [parent, ...support];
		const source: RepositoryDataSource = {
			info: vi.fn(),
			tree: vi.fn(async () => ({
				items: files.map((path) => ({ path, name: path.split('/').at(-1)!, type: 'blob' }))
			})),
			blob: vi.fn(async (path) => ({
				path,
				content: '---\nid: DESIGN-parent\n---\n# Parent',
				encoding: 'utf-8'
			}))
		};
		const result = await indexDocuments(source, 'main', new AbortController().signal);
		expect(result.documents.map((d) => d.path)).toEqual([parent]);
		expect(result.files?.map((f) => f.path)).toEqual([...files].sort((a, b) => a.localeCompare(b)));
		expect(source.blob).toHaveBeenCalledTimes(1);
		await indexDocuments(source, 'main', new AbortController().signal);
		expect(source.tree).toHaveBeenCalledTimes(2);
	});
});
