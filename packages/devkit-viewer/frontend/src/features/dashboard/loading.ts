import { isMilestonePath } from '../../api/milestones';
import { extractDashboardData } from './dashboard';
import { parseBlob, type RepositoryDocument } from '../../api/documents';
import type { RepositoryDataSource } from '../../api/repository';

export const dashboardSections = ['milestones', 'proposals', 'feedback'] as const;
export type DashboardSection = (typeof dashboardSections)[number];

/** One section: every listed header, the bodies read in display order, and what failed. */
export interface SectionResult {
	/** The frontmatter of every listed entry: membership, order and counts. */
	metadata: RepositoryDocument[];
	/** The eligible entries whose bodies were read. */
	documents: RepositoryDocument[];
	/** Listing failures: the membership and counts are incomplete. */
	listErrors: string[];
	/** Listing failures and `path: error` for each eligible body that could not be read. */
	errors: string[];
}

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
	if (section === 'milestones') return isMilestonePath(path);
	if (section === 'proposals') return /^docs\/proposals\/PROP-[^/]+\/proposal\.md$/.test(path);
	return (
		/^(docs|specs)\//.test(path) &&
		path.includes('/feedback/') &&
		path.endsWith('.md') &&
		!path.endsWith('/README.md')
	);
}

/** Lists the section's headers once, then reads every eligible body with six continuous workers. */
export async function loadDashboardSection(
	source: RepositoryDataSource,
	section: DashboardSection,
	signal: AbortSignal
): Promise<SectionResult> {
	const listing = await source.dashboardList(section, signal);
	const metadata: RepositoryDocument[] = [];
	const listErrors = [...listing.errors];
	const seen = new Set<string>();
	for (const item of listing.items) {
		if (!matchesSection(item.path, section) || seen.has(item.path)) continue;
		seen.add(item.path);
		try {
			metadata.push(parseBlob(item.path, item.content, item.encoding));
		} catch (error) {
			listErrors.push(`${item.path}: ${String(error)}`);
		}
	}
	const paths = eligiblePaths(metadata, section);
	const loaded = new Map<string, RepositoryDocument>();
	const readErrors = new Map<string, string>();
	let cursor = 0;
	await Promise.all(
		Array.from({ length: Math.min(6, paths.length) }, async () => {
			while (!signal.aborted && cursor < paths.length) {
				const path = paths[cursor++];
				try {
					const blob = await source.blob(path, signal);
					loaded.set(path, parseBlob(path, blob.content, blob.encoding));
				} catch (error) {
					if (!signal.aborted)
						readErrors.set(
							path,
							`${path}: ${error instanceof Error ? error.message : String(error)}`
						);
				}
			}
		})
	);
	return {
		metadata,
		documents: paths.flatMap((path) => loaded.get(path) ?? []),
		listErrors,
		errors: [...listErrors, ...paths.flatMap((path) => readErrors.get(path) ?? [])]
	};
}
