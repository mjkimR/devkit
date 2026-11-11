import { parseFrontmatter } from '../../api/frontmatter';

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
	const parsed = parseFrontmatter(text);
	return { frontmatter: parsed.meta, content: parsed.body };
}
