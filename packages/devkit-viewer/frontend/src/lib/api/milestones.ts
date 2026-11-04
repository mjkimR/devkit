import { normalizeTree, type RepositoryDataSource, type TreeItem } from './repository';
import { parseBlob, type DocumentIndex } from './documents';

const safePath = (path: string) =>
	!path.includes('\\') &&
	!path.includes('\0') &&
	!path
		.split('/')
		.some((part) => !part || part === '.' || part === '..' || part.toLowerCase() === '.git');
export const isMilestonePath = (path: string) =>
	safePath(path) && /^docs\/(?:packages\/[^/]+\/)?roadmap\/(?:_archive\/)?MS-[^/]+\.md$/.test(path);

/** Shallow structural discovery shared by the dashboard fallback and roadmap tab. */
export async function discoverMilestonePaths(
	source: RepositoryDataSource,
	ref: string,
	signal: AbortSignal
): Promise<{ paths: string[]; errors: string[]; docsEntries: TreeItem[] }> {
	const errors: string[] = [];
	const list = async (path: string, optional = false): Promise<TreeItem[]> => {
		if (signal.aborted) return [];
		try {
			return normalizeTree(await source.tree(path, ref, signal)).filter(
				(item) =>
					safePath(item.path) &&
					item.path.startsWith(`${path}/`) &&
					item.path.slice(path.length + 1).indexOf('/') < 0
			);
		} catch (error) {
			const message = error instanceof Error ? error.message : String(error);
			if (!signal.aborted && !(optional && /^HTTP 404(?:\b|:)/.test(message)))
				errors.push(`${path}: ${message}`);
			return [];
		}
	};
	const docs = await list('docs', true);
	const roots = docs
		.filter((item) => item.type === 'tree' && item.path === 'docs/roadmap')
		.map((item) => item.path);
	if (docs.some((item) => item.type === 'tree' && item.path === 'docs/packages'))
		for (const pkg of await list('docs/packages'))
			if (pkg.type === 'tree')
				for (const item of await list(pkg.path))
					if (item.type === 'tree' && item.path === `${pkg.path}/roadmap`) roots.push(item.path);
	const paths: string[] = [];
	for (const root of roots) {
		const entries = await list(root);
		if (entries.some((item) => item.type === 'tree' && item.path === `${root}/_archive`))
			entries.push(...(await list(`${root}/_archive`)));
		for (const item of entries)
			if (item.type === 'blob' && isMilestonePath(item.path)) paths.push(item.path);
	}
	return { paths: [...new Set(paths)].sort(), errors, docsEntries: docs };
}

/** Generic sources read only discovered milestone bodies, with six continuous workers. */
export async function loadMilestoneDocuments(
	source: RepositoryDataSource,
	ref: string,
	signal: AbortSignal
): Promise<DocumentIndex & { docsEntries: TreeItem[] }> {
	const { paths, errors, docsEntries } = await discoverMilestonePaths(source, ref, signal);
	const documents: DocumentIndex['documents'] = [];
	let cursor = 0;
	await Promise.all(
		Array.from({ length: Math.min(6, paths.length) }, async () => {
			while (!signal.aborted && cursor < paths.length) {
				const path = paths[cursor++];
				try {
					const blob = await source.blob(path, ref, signal);
					documents.push(parseBlob(path, blob.content, blob.encoding));
				} catch (error) {
					if (!signal.aborted)
						errors.push(`${path}: ${error instanceof Error ? error.message : String(error)}`);
				}
			}
		})
	);
	return { documents: documents.sort((a, b) => a.path.localeCompare(b.path)), errors, docsEntries };
}
