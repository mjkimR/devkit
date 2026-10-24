import { parseDocument } from 'yaml';

export interface Frontmatter {
	id?: string;
	title?: string;
	status?: string;
	target_area?: string;
	milestone?: string;
	priority?: string;
	size?: string;
	[key: string]: any;
}

export function parseFrontmatterAndMarkdown(text: string): {
	frontmatter: Frontmatter | null;
	content: string;
} {
	const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
	if (!match) return { frontmatter: null, content: text };
	const document = parseDocument(match[1]);
	if (document.errors.length) throw new Error(document.errors[0].message);
	const parsed = document.toJS({ maxAliasCount: 100 });
	return {
		frontmatter: parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : null,
		content: text.slice(match[0].length)
	};
}
