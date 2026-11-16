import type { RepositoryDocument } from './documents';

export const ID_SOURCE =
	'(?:CAP|UC|UX|ARCH|ADR|PROP|PADR|SPEC|PLAN|TASKS|REC|FB|MAT|MS|DESIGN|DOMAIN|OPS)-[A-Za-z0-9][A-Za-z0-9_-]*';
export const ID_PATTERN = new RegExp(`^${ID_SOURCE}$`);
export const documentId = (doc: RepositoryDocument | null | undefined): string =>
	typeof doc?.meta.id === 'string' && doc.meta.id
		? doc.meta.id
		: typeof doc?.meta.reconcile_id === 'string'
			? doc.meta.reconcile_id
			: '';
export const isArtifactPath = (path: string) =>
	/^docs\/(?:designs|domain|operations)\/[^/]+\/artifacts\//.test(
		path.replace(/^docs\/packages\/[^/]+\//, 'docs/')
	);
export const isFormal = (doc: RepositoryDocument | null | undefined) =>
	Boolean(doc && !isArtifactPath(doc.path) && /^(?:DESIGN|DOMAIN|OPS)-/.test(documentId(doc)));

export const hasFormalContext = (doc: RepositoryDocument | null | undefined) =>
	Boolean(
		doc &&
		!isArtifactPath(doc.path) &&
		ID_PATTERN.test(documentId(doc)) &&
		(isFormal(doc) ||
			['related_designs', 'related_domains', 'related_operations'].some(
				(field) => field in doc.meta
			))
	);

export function identityResolver(documents: RepositoryDocument[]) {
	const declared = new Map<string, RepositoryDocument[]>();
	const aliases = new Map<string, RepositoryDocument[]>();
	for (const doc of documents) {
		const id = documentId(doc);
		if (!id || isArtifactPath(doc.path)) continue;
		declared.set(id, [...(declared.get(id) ?? []), doc]);
		if (Array.isArray(doc.meta.aliases))
			for (const alias of new Set(doc.meta.aliases)) {
				if (
					typeof alias !== 'string' ||
					!ID_PATTERN.test(alias) ||
					alias.split('-')[0] !== id.split('-')[0]
				)
					continue;
				aliases.set(alias, [...(aliases.get(alias) ?? []), doc]);
			}
	}
	const candidates = (id: string) => declared.get(id) ?? aliases.get(id) ?? [];
	const resolve = (id: string) => {
		const found = candidates(id);
		return {
			document: found.length === 1 ? found[0] : null,
			unavailable: found.length > 1 ? 'ambiguous' : found.length ? null : 'missing'
		} as const;
	};
	return { resolve, candidates, keys: new Set([...declared.keys(), ...aliases.keys()]) };
}
