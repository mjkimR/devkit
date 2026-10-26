import { parseBlob, scanDocuments, type DocumentIndex, type RepositoryDocument } from './documents';
import { cachedResult, cacheGeneration, cacheResult, isCurrentGeneration } from './cache';
import type { PlanningSource, RepositoryDataSource } from './repository';

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

const PURPOSE = 'planning:proposals';
const PROPOSAL = /^docs\/proposals\/PROP-([^/]+)\/proposal\.md$/;
// The overlay last loaded per source and branch: it seeds the next list build, also after Refresh.
const applied = new WeakMap<RepositoryDataSource, Map<string, PlanningOverlay>>();

export const cachedOverlay = (source: RepositoryDataSource, ref: string) =>
	cachedResult<PlanningOverlay>(source, ref, PURPOSE);
export const appliedOverlay = (source: RepositoryDataSource, ref: string) =>
	applied.get(source)?.get(ref);

/** One independent request; `undefined` for a host without the overlay. */
export async function loadPlanningOverlay(
	source: RepositoryDataSource,
	ref: string,
	signal: AbortSignal
): Promise<PlanningOverlay | undefined> {
	if (!source.planningProposals) return undefined;
	const cached = cachedOverlay(source, ref);
	if (cached && !signal.aborted) return cached;
	const generation = cacheGeneration(source);
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
	const overlay = { entries, errors };
	if (!signal.aborted && isCurrentGeneration(source, generation)) {
		if (!errors.length) cacheResult(source, ref, PURPOSE, overlay, generation);
		let byRef = applied.get(source);
		if (!byRef) applied.set(source, (byRef = new Map()));
		byRef.set(ref, overlay);
	}
	return overlay;
}

/** A data source whose reads go to one Planning source's proposal directory. */
export function planningDataSource(
	source: RepositoryDataSource,
	planning: string
): RepositoryDataSource {
	const listing = (path: string, _ref: string, signal: AbortSignal) =>
		source.planningTree!(planning, path, signal);
	return {
		info: (signal) => source.info(signal),
		tree: listing,
		treeRecursive: listing,
		blob: (path, _ref, signal) => source.planningBlob!(planning, path, signal)
	};
}

/** The Markdown files of an overlaid proposal's bundle, read from its own source. */
export async function loadPlanningBundle(
	source: RepositoryDataSource,
	entry: OverlayEntry,
	signal: AbortSignal
): Promise<DocumentIndex> {
	if (!source.planningTree || !source.planningBlob)
		return { documents: [entry.document], errors: [] };
	const path = entry.document.path;
	return scanDocuments(planningDataSource(source, entry.source.id), '', signal, [
		path.slice(0, path.lastIndexOf('/'))
	]);
}
