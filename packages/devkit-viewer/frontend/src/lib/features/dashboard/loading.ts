import { extractDashboardData } from './dashboard';
import {
	parseBlob,
	scanDocuments,
	type DocumentIndex,
	type RepositoryDocument
} from '../../api/documents';
import { CACHE_TTL_MS, cachedResult, cacheGeneration, cacheResult } from '../../api/cache';
import type { RepositoryDataSource } from '../../api/repository';
import { appliedOverlay, type OverlayEntry } from '../../api/planning';

export const dashboardSections = ['milestones', 'proposals', 'feedback'] as const;
export type DashboardSection = (typeof dashboardSections)[number];
export const cachedSection = (
	source: RepositoryDataSource,
	ref: string,
	section: DashboardSection
) => cachedResult<DocumentIndex>(source, ref, `dashboard:${section}`);

export async function loadDashboardSection(
	source: RepositoryDataSource,
	ref: string,
	section: DashboardSection,
	signal: AbortSignal
): Promise<DocumentIndex> {
	const cached = cachedSection(source, ref, section);
	if (cached && !signal.aborted) return cached;
	const generation = cacheGeneration(source);
	const result =
		section === 'milestones'
			? await scanDocuments(
					source,
					ref,
					signal,
					['docs/roadmap'],
					(item) => /^docs\/roadmap\/MS-[^/]+\.md$/.test(item.path),
					() => false,
					true,
					false
				)
			: section === 'proposals'
				? await scanDocuments(
						source,
						ref,
						signal,
						['docs/proposals'],
						(item) => /^docs\/proposals\/PROP-[^/]+\/proposal\.md$/.test(item.path),
						(item) => /^docs\/proposals\/PROP-[^/]+$/.test(item.path),
						true,
						false
					)
				: await scanDocuments(
						source,
						ref,
						signal,
						['docs', 'specs'],
						(item) =>
							item.path.includes('/feedback/') &&
							item.name.endsWith('.md') &&
							item.name !== 'README.md',
						() => true,
						true
					);
	if (!signal.aborted && !result.errors.length)
		cacheResult(source, ref, `dashboard:${section}`, result, generation);
	return result;
}

export const pageSizes: Record<DashboardSection, number> = {
	milestones: 6,
	proposals: 9,
	feedback: 6
};
export interface SectionSnapshot {
	metadata: RepositoryDocument[];
	paths: string[];
	documents: RepositoryDocument[];
	errors: string[];
	listErrors: string[];
	expires: number;
	generation: ReturnType<typeof cacheGeneration>;
	fallback?: RepositoryDocument[];
	/** The Planning overlay merged into this list: its documents replace checkout bodies. */
	overlay?: Record<string, OverlayEntry>;
	/** The checkout header each seeded path replaced; `null` for a Planning-only proposal. */
	checkout?: Record<string, RepositoryDocument | null>;
}
export const cachedDashboardPage = (
	source: RepositoryDataSource,
	ref: string,
	section: DashboardSection
) => cachedResult<SectionSnapshot>(source, ref, `dashboard-page:${section}`);

function eligiblePaths(metadata: RepositoryDocument[], section: DashboardSection) {
	const data = extractDashboardData(metadata);
	return (
		section === 'milestones'
			? data.milestones.open
			: section === 'proposals'
				? data.proposals.active
				: data.feedback.open
	).map((item) => item.path);
}
function matchesSection(path: string, section: DashboardSection) {
	if (path.split('/').some((part) => part === '..' || part === '.' || !part)) return false;
	if (section === 'milestones') return /^docs\/roadmap\/MS-[^/]+\.md$/.test(path);
	if (section === 'proposals') return /^docs\/proposals\/PROP-[^/]+\/proposal\.md$/.test(path);
	return (
		/^(docs|specs)\//.test(path) &&
		path.includes('/feedback/') &&
		path.endsWith('.md') &&
		!path.endsWith('/README.md')
	);
}
export async function openDashboardPage(
	source: RepositoryDataSource,
	ref: string,
	section: DashboardSection,
	signal: AbortSignal
): Promise<SectionSnapshot> {
	const cached = cachedDashboardPage(source, ref, section);
	if (cached && !signal.aborted) return cached;
	const generation = cacheGeneration(source);
	const metadata: RepositoryDocument[] = [];
	const errors: string[] = [];
	let fallback: RepositoryDocument[] | undefined;
	if (source.dashboardList) {
		const result = await source.dashboardList(section, ref, signal);
		errors.push(...result.errors);
		const seen = new Set<string>();
		for (const item of result.items) {
			if (!matchesSection(item.path, section) || seen.has(item.path)) continue;
			seen.add(item.path);
			try {
				metadata.push(parseBlob(item.path, item.content, item.encoding));
			} catch (error) {
				errors.push(`${item.path}: ${String(error)}`);
			}
		}
	} else {
		const result = await loadDashboardSection(source, ref, section, signal);
		metadata.push(...result.documents);
		errors.push(...result.errors);
		fallback = result.documents;
	}
	// Order and membership use the last applied Planning overlay; a later overlay never reorders this list.
	const seed = section === 'proposals' ? appliedOverlay(source, ref)?.entries : undefined;
	const overlay = seed && Object.keys(seed).length ? seed : undefined;
	const checkout: Record<string, RepositoryDocument | null> = {};
	if (overlay) {
		const positions = new Map(metadata.map((doc, index) => [doc.path, index]));
		for (const [path, entry] of Object.entries(overlay)) {
			const index = positions.get(path);
			checkout[path] = index === undefined ? null : metadata[index];
			if (index === undefined) metadata.push(entry.document);
			else metadata[index] = entry.document;
		}
	}
	return nextDashboardPage(
		source,
		ref,
		section,
		{
			metadata,
			paths: eligiblePaths(metadata, section),
			documents: [],
			errors: [],
			listErrors: errors,
			expires: Date.now() + CACHE_TTL_MS,
			generation,
			fallback,
			overlay,
			checkout: overlay ? checkout : undefined
		},
		signal
	);
}
export async function nextDashboardPage(
	source: RepositoryDataSource,
	ref: string,
	section: DashboardSection,
	snapshot: SectionSnapshot,
	signal: AbortSignal
): Promise<SectionSnapshot> {
	const paths = snapshot.paths.slice(
		snapshot.documents.length,
		snapshot.documents.length + pageSizes[section]
	);
	const loaded = new Map<string, RepositoryDocument>();
	const errors = [...snapshot.listErrors];
	let cursor = 0;
	await Promise.all(
		Array.from({ length: Math.min(6, paths.length) }, async () => {
			while (!signal.aborted && cursor < paths.length) {
				const path = paths[cursor++];
				try {
					const existing =
						snapshot.overlay?.[path]?.document ??
						snapshot.fallback?.find((doc) => doc.path === path);
					const blob = existing ? undefined : await source.blob(path, ref, signal);
					loaded.set(path, existing ?? parseBlob(path, blob!.content, blob!.encoding));
				} catch (error) {
					if (!signal.aborted) errors.push(`${path}: ${String(error)}`);
				}
			}
		})
	);
	// A page publishes atomically: a failed page leaves the existing cursor and cards intact.
	const result = {
		...snapshot,
		errors,
		documents:
			errors.length > snapshot.listErrors.length || signal.aborted
				? snapshot.documents
				: [...snapshot.documents, ...paths.map((path) => loaded.get(path)!)]
	};
	if (!signal.aborted && !errors.length)
		cacheResult(
			source,
			ref,
			`dashboard-page:${section}`,
			result,
			snapshot.generation,
			snapshot.expires
		);
	return result;
}
