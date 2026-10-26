import { describe, expect, it } from 'vitest';
import { indexDocuments, parseBlob, renderDocument } from './documents';
import type { RepositoryDataSource } from './repository';

const base64 = (text: string) => btoa(String.fromCharCode(...new TextEncoder().encode(text)));

describe('parseBlob', () => {
	it('keeps fields and kinds it does not know', () => {
		const doc = parseBlob(
			'docs/other/THING-x.md',
			base64('---\nid: THING-x\nkind: gadget\nnested: {a: [1, 2]}\n---\n# Thing\n\nBody 한글\n'),
			'base64'
		);
		expect(doc.meta).toEqual({ id: 'THING-x', kind: 'gadget', nested: { a: [1, 2] } });
		expect(doc.title).toBe('Thing');
		expect(renderDocument(doc, [doc]).html).toContain('Body 한글');
	});

	it('refuses frontmatter that is not YAML', () => {
		expect(() => parseBlob('docs/a.md', '---\nid: [broken\n---\n# A\n', 'utf-8')).toThrow();
	});
});

describe('renderDocument ID references', () => {
	const doc = (path: string, id: string, body = '') =>
		parseBlob(path, `---\nid: ${id}\n---\n# ${id}\n\n${body}\n`, 'utf-8');

	it('links prose references with every current ID prefix', () => {
		const targets = [
			doc('docs/usecases/a/UC-a.md', 'UC-a'),
			doc('specs/feedback/b.md', 'FB-b'),
			doc('docs/roadmap/MS-c.md', 'MS-c'),
			doc('docs/ux/a/UX-d.md', 'UX-d')
		];
		const page = doc('docs/page.md', 'CAP-P-page', 'See [UC-a], [FB-b], [MS-c] and [UX-d].');
		const wrapper = document.createElement('div');
		wrapper.innerHTML = renderDocument(page, [page, ...targets]).html;
		const anchors = [...wrapper.querySelectorAll('a')];
		expect(anchors.map((a) => [a.textContent, a.dataset.docPath])).toEqual([
			['[UC-a]', 'docs/usecases/a/UC-a.md'],
			['[FB-b]', 'specs/feedback/b.md'],
			['[MS-c]', 'docs/roadmap/MS-c.md'],
			['[UX-d]', 'docs/ux/a/UX-d.md']
		]);
	});

	it('leaves retired and unresolved references as text', () => {
		const retired = doc('docs/old/US-a.md', 'US-a');
		const page = doc('docs/page.md', 'CAP-P-page', 'See [US-a] and [UC-missing].');
		const wrapper = document.createElement('div');
		wrapper.innerHTML = renderDocument(page, [page, retired]).html;
		expect(wrapper.querySelectorAll('a')).toHaveLength(0);
		expect(wrapper.textContent).toContain('See [US-a] and [UC-missing].');
	});
});

describe('indexDocuments', () => {
	it('indexes every readable document and lists the unreadable ones', async () => {
		const files: Record<string, string> = {
			'docs/a.md': '---\nid: CAP-A-a\nunknown_field: 1\n---\n# A\n',
			'docs/b.md': '---\nid: [broken\n---\n# B\n',
			'docs/sub/c.md': '# C\n',
			'specs/2026-10/x/spec.md': '---\nid: SPEC-x\n---\n# X\n'
		};
		const source: RepositoryDataSource = {
			info: async () => ({ default_branch: 'main' }),
			tree: async (path) => {
				const names = new Map<string, string>();
				for (const file of Object.keys(files))
					if (file.startsWith(`${path}/`)) {
						const [name, ...rest] = file.slice(path.length + 1).split('/');
						names.set(name, rest.length ? 'tree' : 'blob');
					}
				return [...names].map(([name, type]) => ({ name, path: `${path}/${name}`, type }));
			},
			blob: async (path) => ({ path, content: base64(files[path]), encoding: 'base64' })
		};
		const { documents, errors } = await indexDocuments(
			source,
			'main',
			new AbortController().signal
		);
		expect(documents.map((d) => d.path)).toEqual([
			'docs/a.md',
			'docs/sub/c.md',
			'specs/2026-10/x/spec.md'
		]);
		expect(errors).toHaveLength(1);
		expect(errors[0]).toMatch(/^docs\/b\.md: /);
	});
});
