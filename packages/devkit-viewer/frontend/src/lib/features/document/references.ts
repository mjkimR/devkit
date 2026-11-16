import { visibleReferences, type RepositoryDocument } from '../../api/documents';
import {
	documentId,
	ID_PATTERN,
	identityResolver,
	isArtifactPath,
	isFormal
} from '../../api/identity';

export function metadataText(value: unknown): string {
	if (typeof value === 'string') return value;
	try {
		return JSON.stringify(value) ?? String(value);
	} catch {
		return '[Recursive metadata; inspect raw source]';
	}
}
const lists = [
	'usecases',
	'capabilities',
	'related_usecases',
	'related_capabilities',
	'depends_on',
	'related_designs',
	'related_domains',
	'related_operations'
];
const scalars = ['spec', 'plan', 'milestone'];
const provenance = ['proposal', 'decomposed_from', 'supersedes'];
const typed: Record<string, string> = {
	related_designs: 'DESIGN-',
	related_domains: 'DOMAIN-',
	related_operations: 'OPS-',
	related_capabilities: 'CAP-',
	related_usecases: 'UC-'
};
export interface ReferenceRow {
	written: string;
	id: string;
	field: string;
	path: string | null;
	title: string | null;
	status: string | null;
	unavailable: string | null;
	referencedAs?: string;
}
function facts(doc: RepositoryDocument) {
	const current: { written: string; field: string }[] = visibleReferences(doc).map((written) => ({
		written,
		field: 'body'
	}));
	const origins: typeof current = [];
	const issues: string[] = [];
	if (isFormal(doc)) {
		for (const field of ['id', 'title', 'status', 'summary'])
			if (typeof doc.meta[field] !== 'string' || !doc.meta[field].trim())
				issues.push(`${field}: expected a nonempty string`);
		if (
			'aliases' in doc.meta &&
			(!Array.isArray(doc.meta.aliases) ||
				doc.meta.aliases.some(
					(value: unknown) =>
						typeof value !== 'string' ||
						!ID_PATTERN.test(value) ||
						value.split('-')[0] !== documentId(doc).split('-')[0]
				))
		)
			issues.push('aliases: expected same-prefix identity IDs');
		if (
			'entrypoints' in doc.meta &&
			(!documentId(doc).startsWith('DESIGN-') ||
				!Array.isArray(doc.meta.entrypoints) ||
				doc.meta.entrypoints.some((value: unknown) => typeof value !== 'string'))
		)
			issues.push('entrypoints: not applicable or malformed');
	}
	for (const field of [...lists, ...scalars, ...provenance]) {
		if (!(field in doc.meta)) continue;
		const anchor = /(?:\/proposal\.md|\/spec\.md)$/.test(doc.path);
		if (['supersedes', 'decomposed_from'].includes(field) && !anchor) continue;
		if (field === 'milestone' && (!anchor || documentId(doc).startsWith('SPEC-'))) continue;
		const value: unknown = doc.meta[field];
		const list = lists.includes(field);
		if (list ? !Array.isArray(value) : typeof value !== 'string') {
			issues.push(`${field}: expected ${list ? 'a list of IDs' : 'one ID'}`);
			continue;
		}
		for (const written of list ? (value as unknown[]) : [value]) {
			if (
				typeof written !== 'string' ||
				!ID_PATTERN.test(written) ||
				(typed[field] && !written.startsWith(typed[field]))
			) {
				issues.push(`${field}: invalid target ${metadataText(written)}`);
				continue;
			}
			(provenance.includes(field) ? origins : current).push({ written, field });
		}
	}
	return { current, origins, issues };
}
export function deriveReferences(subject: RepositoryDocument, indexed: RepositoryDocument[]) {
	const documents = [
		...indexed.filter((doc) => doc.path !== subject.path && !isArtifactPath(doc.path)),
		subject
	];
	const resolver = identityResolver(documents);
	const row = (written: string, field: string): ReferenceRow => {
		const result = resolver.resolve(written),
			doc = result.document;
		return {
			written,
			field,
			id: doc ? documentId(doc) : written,
			path: doc?.path ?? null,
			title: doc?.title ?? null,
			status: typeof doc?.meta.status === 'string' ? doc.meta.status : null,
			unavailable: result.unavailable
		};
	};
	const own = facts(subject);
	const sort = (a: ReferenceRow, b: ReferenceRow) =>
		a.id.localeCompare(b.id) ||
		a.field.localeCompare(b.field) ||
		a.written.localeCompare(b.written);
	const outgoing = own.current.map((ref) => row(ref.written, ref.field)).sort(sort);
	const incoming: ReferenceRow[] = [];
	const issues = [...own.issues];
	for (const doc of documents) {
		if (!ID_PATTERN.test(documentId(doc)) || doc.path === subject.path) continue;
		const references = facts(doc);
		for (const ref of references.current)
			if (resolver.resolve(ref.written).document?.path === subject.path)
				incoming.push({ ...row(documentId(doc), ref.field), referencedAs: ref.written });
		issues.push(...references.issues.map((issue) => `${documentId(doc)}: ${issue}`));
	}
	return {
		outgoing,
		incoming: incoming.sort(sort),
		provenance: own.origins.map((ref) => row(ref.written, ref.field)).sort(sort),
		issues
	};
}
