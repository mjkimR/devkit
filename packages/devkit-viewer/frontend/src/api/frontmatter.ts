import { parseDocument } from 'yaml';

/** The delimiter grammar of devkit_core.core.frontmatter, shared by blobs and previews. */
export function parseFrontmatter(text: string): {
	meta: Record<string, any> | null;
	body: string;
} {
	const source = text.startsWith('\uFEFF') ? text.slice(1) : text;
	const lines = source.split('\n');
	if (lines[0].trimEnd() !== '---') return { meta: null, body: source };
	let start = lines[0].length + 1;
	for (let index = 1; index < lines.length; index++) {
		const line = lines[index];
		const end = start + line.length + (index < lines.length - 1 ? 1 : 0);
		if (['---', '...'].includes(line.trimEnd())) {
			const document = parseDocument(source.slice(lines[0].length + 1, start));
			if (document.errors.length) throw new Error(document.errors[0].message);
			const value = document.toJS({ maxAliasCount: 100 }) ?? {};
			return {
				meta: typeof value === 'object' && !Array.isArray(value) ? value : null,
				body: source.slice(end)
			};
		}
		start = end;
	}
	throw new Error("frontmatter opened with '---' is never closed by a '---' or '...' line");
}
