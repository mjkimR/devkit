import { cachedResult, cacheGeneration, cacheResult } from './cache';
import { isMilestonePath, loadMilestoneDocuments } from './milestones';
export { isMilestonePath } from './milestones';
import { parseBlob, type RepositoryDocument } from './documents';
import { normalizeTree, type RepositoryDataSource } from './repository';

export interface Member {
	id: string;
	title: string;
	kind: 'proposal';
	status: string;
	/** Direct proposals do not certify milestone completion. */
	settled: boolean;
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
const FINISHED = new Set(['done', 'dropped']);
const ORDER = ['active', 'planned', 'done', 'dropped'];
const PROPOSAL = /^docs\/proposals\/PROP-[^/]+\/proposal\.md$/;

const text = (value: unknown) => (typeof value === 'string' ? value : '');
const rank = (status: string) => {
	const index = ORDER.indexOf(status);
	return index < 0 ? ORDER.length : index;
};

function memberOf(doc: RepositoryDocument) {
	if (!PROPOSAL.test(doc.path)) return null;
	const id = text(doc.meta.id);
	if (!id.startsWith('PROP-')) return null;
	const status = text(doc.meta.status) || 'unknown';
	const member: Member = {
		id,
		title: doc.title,
		kind: 'proposal',
		status,
		settled: false,
		path: doc.path
	};
	return { member, milestone: text(doc.meta.milestone), slug: id.replace(/^PROP-/, '') };
}

/**
 * Milestones of the registered checkout with their readiness and members. Direct PROP members only. One member per
 * slug, the first in `documents` order; rejected proposals are not members.
 */
export function buildRoadmap(
	documents: RepositoryDocument[],
	options: { history: boolean }
): Milestone[] {
	const winners = new Map<string, { member: Member; milestone: string }>();
	for (const doc of documents) {
		const candidate = memberOf(doc);
		if (candidate && !winners.has(candidate.slug)) winners.set(candidate.slug, candidate);
	}
	const milestones = documents
		.filter((doc) => isMilestonePath(doc.path) && text(doc.meta.id))
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
				.filter((w) => w.milestone === m.id && w.member.status !== 'rejected')
				.map((w) => w.member)
				.sort((a, b) => a.id.localeCompare(b.id));
			return { ...m, ready: !unknown.length && !waitingFor.length, waitingFor, unknown, members };
		})
		.sort((a, b) => rank(a.status) - rank(b.status) || a.id.localeCompare(b.id));
}

/** Milestones and direct proposal anchors of one branch; unreadable files are listed in `errors`. */
export async function loadRoadmapDocuments(
	source: RepositoryDataSource,
	branch: string,
	signal: AbortSignal
): Promise<{ documents: RepositoryDocument[]; errors: string[] }> {
	const cached = cachedResult<{ documents: RepositoryDocument[]; errors: string[] }>(
		source,
		branch,
		'roadmap'
	);
	if (cached && !signal.aborted) return cached;
	const generation = cacheGeneration(source);
	const milestones = await loadMilestoneDocuments(source, signal);
	const errors = milestones.errors;
	const paths: string[] = [];
	if (
		!signal.aborted &&
		milestones.docsEntries.some((item) => item.type === 'tree' && item.path === 'docs/proposals')
	) {
		try {
			for (const item of normalizeTree(await source.tree('docs/proposals', signal)))
				if (item.type === 'tree' && /^docs\/proposals\/PROP-[^/]+$/.test(item.path))
					paths.push(`${item.path}/proposal.md`);
		} catch (error) {
			const message = error instanceof Error ? error.message : String(error);
			if (!signal.aborted) errors.push(`docs/proposals: ${message}`);
		}
	}
	const documents: RepositoryDocument[] = [...milestones.documents];
	for (let i = 0; i < paths.length && !signal.aborted; i += 6)
		await Promise.all(
			paths.slice(i, i + 6).map(async (path) => {
				const report = (error: unknown) =>
					errors.push(`${path}: ${error instanceof Error ? error.message : error}`);
				let blob;
				try {
					blob = await source.blob(path, signal);
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
	const result = { documents: documents.sort((a, b) => a.path.localeCompare(b.path)), errors };
	if (!signal.aborted && !errors.length) cacheResult(source, branch, 'roadmap', result, generation);
	return result;
}
