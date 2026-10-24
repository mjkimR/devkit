import { scanDocuments, type DocumentIndex } from '../../api/documents';
import { cachedResult, cacheGeneration, cacheResult } from '../../api/cache';
import type { RepositoryDataSource } from '../../api/repository';

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
