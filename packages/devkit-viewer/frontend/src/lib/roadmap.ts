import { parseBlob, type RepositoryDocument } from './documents';
import { normalizeTree, type RepositoryDataSource } from './repository';

export interface Member {
	id: string;
	title: string;
	kind: 'proposal' | 'spec';
	status: string;
	/** A completed spec; everything else still needs work before the milestone can close. */
	settled: boolean;
	/** The activity branch the member was read from; `null` for the default branch. */
	branch: string | null;
	path: string;
}
export interface Milestone {
	id: string;
	title: string;
	status: string;
	path: string;
	dependsOn: string[];
	/** Every `depends_on` names a known milestone that is `done` or `dropped`. */
	ready: boolean;
	/** Known prerequisites not finished yet. */
	waitingFor: string[];
	/** Prerequisites that name no milestone: never counted as satisfied. */
	unknown: string[];
	members: Member[];
}
export interface BranchDocuments {
	name: string;
	documents: RepositoryDocument[];
}

const FINISHED = new Set(['done', 'dropped']);
const ORDER = ['active', 'planned', 'done', 'dropped'];
const MILESTONE = /^docs\/roadmap\/MS-[^/]+\.md$/;
const PROPOSAL = /^docs\/proposals\/PROP-[^/]+\/proposal\.md$/;
const SPEC = /^specs\/\d{4}-\d{2}\/[^/]+\/spec\.md$/;

/** Local branches whose Units the roadmap reads besides the selected branch. */
export const isActivityBranch = (name: string) => /^(plan|dev)-./.test(name);

const text = (value: unknown) => (typeof value === 'string' ? value : '');
const rank = (status: string) => {
	const index = ORDER.indexOf(status);
	return index < 0 ? ORDER.length : index;
};

function memberOf(doc: RepositoryDocument, branch: string | null) {
	const kind = PROPOSAL.test(doc.path) ? 'proposal' : SPEC.test(doc.path) ? 'spec' : null;
	const id = text(doc.meta.id);
	if (!kind || !id) return null;
	const status = text(doc.meta.status) || 'unknown';
	const member: Member = {
		id,
		title: doc.title,
		kind,
		status,
		settled: kind === 'spec' && status === 'completed',
		branch,
		path: doc.path
	};
	return { member, milestone: text(doc.meta.milestone), slug: id.replace(/^(PROP|SPEC)-/, '') };
}

/**
 * Milestones of the default branch (`base`) with their readiness and members. One member per slug: a spec replaces the
 * proposal it was handed off from, and an activity branch replaces the default branch's copy; rejected proposals
 * are not members.
 */
export function buildRoadmap(
	base: RepositoryDocument[],
	branches: BranchDocuments[],
	options: { history: boolean }
): Milestone[] {
	const winners = new Map<string, { member: Member; milestone: string }>();
	const sources = [
		{ branch: null, documents: base },
		...branches.map((b) => ({ branch: b.name, documents: b.documents }))
	];
	const weight = (m: Member) => (m.kind === 'spec' ? 2 : 0) + (m.branch ? 1 : 0);
	for (const source of sources)
		for (const doc of source.documents) {
			const candidate = memberOf(doc, source.branch);
			if (!candidate) continue;
			const current = winners.get(candidate.slug);
			if (!current || weight(candidate.member) > weight(current.member))
				winners.set(candidate.slug, candidate);
		}
	const milestones = base
		.filter((doc) => MILESTONE.test(doc.path) && text(doc.meta.id))
		.map((doc) => ({
			id: text(doc.meta.id),
			title: doc.title,
			status: text(doc.meta.status) || 'unknown',
			path: doc.path,
			dependsOn: Array.isArray(doc.meta.depends_on)
				? doc.meta.depends_on.filter((d: unknown) => typeof d === 'string')
				: []
		}));
	const statusOf = new Map(milestones.map((m) => [m.id, m.status]));
	return milestones
		.filter((m) => options.history || !FINISHED.has(m.status))
		.map((m) => {
			const unknown = m.dependsOn.filter((d: string) => !statusOf.has(d));
			const waitingFor = m.dependsOn.filter(
				(d: string) => statusOf.has(d) && !FINISHED.has(statusOf.get(d)!)
			);
			const members = [...winners.values()]
				.filter(
					(w) =>
						w.milestone === m.id &&
						!(w.member.kind === 'proposal' && w.member.status === 'rejected')
				)
				.map((w) => w.member)
				.sort((a, b) => a.id.localeCompare(b.id));
			return { ...m, ready: !unknown.length && !waitingFor.length, waitingFor, unknown, members };
		})
		.sort((a, b) => rank(a.status) - rank(b.status) || a.id.localeCompare(b.id));
}

/** The milestone, proposal and spec documents of one ref; unreadable files are listed in `errors`. */
export async function loadRoadmapDocuments(
	source: RepositoryDataSource,
	ref: string,
	signal: AbortSignal
): Promise<{ documents: RepositoryDocument[]; errors: string[] }> {
	const errors: string[] = [];
	const list = async (path: string) => {
		try {
			return normalizeTree(await source.tree(path, ref, signal));
		} catch (error) {
			if (!signal.aborted)
				errors.push(`${path}: ${error instanceof Error ? error.message : error}`);
			return [];
		}
	};
	const root = await list('');
	const docs = root.some((i) => i.path === 'docs' && i.type === 'tree') ? await list('docs') : [];
	const has = (path: string) => docs.some((i) => i.path === path && i.type === 'tree');
	const paths: string[] = [];
	if (has('docs/roadmap'))
		for (const item of await list('docs/roadmap'))
			if (item.type === 'blob' && MILESTONE.test(item.path)) paths.push(item.path);
	if (has('docs/proposals'))
		for (const item of await list('docs/proposals'))
			if (item.type === 'tree' && /^PROP-/.test(item.name)) paths.push(`${item.path}/proposal.md`);
	if (root.some((i) => i.path === 'specs' && i.type === 'tree'))
		for (const month of await list('specs'))
			if (month.type === 'tree' && /^\d{4}-\d{2}$/.test(month.name))
				for (const bundle of await list(month.path))
					if (bundle.type === 'tree') paths.push(`${bundle.path}/spec.md`);
	const documents: RepositoryDocument[] = [];
	for (let i = 0; i < paths.length && !signal.aborted; i += 6)
		await Promise.all(
			paths.slice(i, i + 6).map(async (path) => {
				const report = (error: unknown) =>
					errors.push(`${path}: ${error instanceof Error ? error.message : error}`);
				let blob;
				try {
					blob = await source.blob(path, ref, signal);
				} catch (error) {
					// A proposal directory without proposal.md is not a proposal bundle.
					if (!signal.aborted && !/\/proposal\.md$/.test(path)) report(error);
					return;
				}
				try {
					documents.push(parseBlob(path, blob.content, blob.encoding));
				} catch (error) {
					report(error);
				}
			})
		);
	return { documents: documents.sort((a, b) => a.path.localeCompare(b.path)), errors };
}
