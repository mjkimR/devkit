import { parseBlob, scanDocuments, type DocumentIndex, type RepositoryDocument } from './documents';
import type { FileSource, PlanningSource, RepositoryDataSource } from './repository';

/** A proposal read from its Planning source instead of the checkout. */
export interface OverlayEntry {
	document: RepositoryDocument;
	source: PlanningSource;
}
/** Planning proposals by `proposal.md` path. */
export interface PlanningOverlay {
	entries: Record<string, OverlayEntry>;
	errors: string[];
}

const PROPOSAL = /^docs\/proposals\/PROP-([^/]+)\/proposal\.md$/;

/** One independent request, asked again on every load: the overlay is never cached. */
export async function loadPlanningOverlay(
	source: RepositoryDataSource,
	signal: AbortSignal
): Promise<PlanningOverlay> {
	const result = await source.planningProposals(signal);
	const sources = new Map(result.sources.map((planning) => [planning.id, planning]));
	const entries: Record<string, OverlayEntry> = {};
	const errors = [...result.errors];
	for (const item of result.items) {
		const planning = sources.get(item.source);
		// A source contributes only its own PROP-<slug>; anything else is ignored.
		if (!planning || item.path.match(PROPOSAL)?.[1] !== planning.slug || entries[item.path])
			continue;
		try {
			entries[item.path] = {
				document: parseBlob(item.path, item.content, item.encoding),
				source: planning
			};
		} catch (error) {
			errors.push(`${planning.label}: ${item.path}: ${String(error)}`);
		}
	}
	return { entries, errors };
}

/** The reads of one Planning source's proposal directory. */
export function planningDataSource(source: RepositoryDataSource, planning: string): FileSource {
	const listing = (path: string, signal: AbortSignal) =>
		source.planningTree(planning, path, signal);
	return {
		tree: listing,
		treeRecursive: listing,
		blob: (path, signal) => source.planningBlob(planning, path, signal)
	};
}

/** The Markdown files of an overlaid proposal's bundle, read from its own source. */
export async function loadPlanningBundle(
	source: RepositoryDataSource,
	entry: OverlayEntry,
	signal: AbortSignal
): Promise<DocumentIndex> {
	const path = entry.document.path;
	return scanDocuments(planningDataSource(source, entry.source.id), signal, [
		path.slice(0, path.lastIndexOf('/'))
	]);
}
