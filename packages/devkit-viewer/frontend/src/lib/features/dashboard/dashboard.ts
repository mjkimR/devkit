import { isMilestonePath } from '../../api/roadmap';
import type { RepositoryDocument } from '../../api/documents';

export interface MilestoneItemData {
	id: string;
	title: string;
	status: string;
	summary: string;
	path: string;
	dependsOn: string[];
}

export interface ProposalItemData {
	id: string;
	slug: string;
	title: string;
	status: string;
	taskKind: string;
	planningEffort: string;
	devEffort: string;
	path: string;
	summary: string;
}

export interface FeedbackItemData {
	id: string;
	title: string;
	status: string;
	severity: string;
	category: string;
	scope: string;
	target: string;
	origin: string;
	path: string;
	summary: string;
}

export interface DashboardData {
	milestones: {
		all: MilestoneItemData[];
		open: MilestoneItemData[];
		totalCount: number;
		openCount: number;
	};
	proposals: {
		all: ProposalItemData[];
		active: ProposalItemData[];
		totalCount: number;
		activeCount: number;
	};
	feedback: {
		all: FeedbackItemData[];
		open: FeedbackItemData[];
		totalCount: number;
		openCount: number;
	};
}

const MILESTONE_STATUS_ORDER: Record<string, number> = {
	active: 1,
	planned: 2,
	done: 3,
	dropped: 4
};

const PROPOSAL_STATUS_ORDER: Record<string, number> = {
	review: 1,
	draft: 2,
	accepted: 3,
	completed: 4,
	rejected: 5,
	superseded: 6
};

const FEEDBACK_SEVERITY_ORDER: Record<string, number> = {
	critical: 1,
	blocked: 2,
	workaround: 3,
	friction: 4
};

function cleanSummary(text: string): string {
	return text
		.replace(/^#+\s+.+$/gm, '')
		.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
		.replace(/[*_`]/g, '')
		.replace(/\s+/g, ' ')
		.trim();
}

function extractFirstParagraph(body: string): string {
	const lines = body
		.split('\n')
		.map((l) => l.trim())
		.filter((l) => l && !l.startsWith('#'));
	if (!lines.length) return '';
	return cleanSummary(lines.slice(0, 3).join(' '));
}

export function extractDashboardData(documents: RepositoryDocument[]): DashboardData {
	const allMilestones: MilestoneItemData[] = [];
	const allProposals: ProposalItemData[] = [];
	const allFeedback: FeedbackItemData[] = [];

	for (const doc of documents) {
		const path = doc.path;
		const meta = doc.meta || {};

		// 1. Milestones
		if (isMilestonePath(path)) {
			const id = String(meta.id || path.split('/').at(-1)?.replace(/\.md$/, ''));
			const title = doc.title || id;
			const status = String(meta.status || 'planned').toLowerCase();
			const dependsOn = Array.isArray(meta.depends_on)
				? meta.depends_on.map(String)
				: typeof meta.depends_on === 'string'
					? [meta.depends_on]
					: [];
			const summary =
				typeof meta.summary === 'string' && meta.summary
					? cleanSummary(meta.summary)
					: extractFirstParagraph(doc.body);

			allMilestones.push({
				id,
				title,
				status,
				summary,
				path,
				dependsOn
			});
			continue;
		}

		// 2. Proposals
		if (path.startsWith('docs/proposals/PROP-') && path.endsWith('/proposal.md')) {
			const folderName = path.split('/')[2] || '';
			const id = String(meta.id || folderName);
			const slug = id.replace(/^PROP-/, '') || folderName.replace(/^PROP-/, '');
			const title = doc.title || id;
			const status = String(meta.status || 'draft').toLowerCase();
			const taskKind = String(meta.task_kind || 'feature');
			const planningEffort = String(meta.planning_effort || 'medium');
			const devEffort = String(meta.dev_effort || 'medium');
			const summary =
				typeof meta.summary === 'string' && meta.summary
					? cleanSummary(meta.summary)
					: extractFirstParagraph(doc.body);

			allProposals.push({
				id,
				slug,
				title,
				status,
				taskKind,
				planningEffort,
				devEffort,
				path,
				summary
			});
			continue;
		}

		// 3. Feedback
		if (path.includes('/feedback/') && path.endsWith('.md') && !path.endsWith('/README.md')) {
			const id = String(meta.id || path.split('/').at(-1)?.replace(/\.md$/, ''));
			const title = doc.title || id;
			const status = String(meta.status || 'open').toLowerCase();
			const severity = String(meta.severity || 'friction').toLowerCase();
			const category = String(meta.category || '');
			const scope = String(meta.scope || 'repo');
			const target = String(meta.target || '');
			const origin = String(meta.origin || 'agent');
			const summary =
				typeof meta.summary === 'string' && meta.summary
					? cleanSummary(meta.summary)
					: extractFirstParagraph(doc.body);

			allFeedback.push({
				id,
				title,
				status,
				severity,
				category,
				scope,
				target,
				origin,
				path,
				summary
			});
			continue;
		}
	}

	// Sort and partition milestones
	allMilestones.sort((a, b) => {
		const orderA = MILESTONE_STATUS_ORDER[a.status] ?? 99;
		const orderB = MILESTONE_STATUS_ORDER[b.status] ?? 99;
		if (orderA !== orderB) return orderA - orderB;
		return a.id.localeCompare(b.id) || a.path.localeCompare(b.path);
	});
	const openMilestones = allMilestones.filter(
		(m) => m.status === 'active' || m.status === 'planned'
	);

	// Sort and partition proposals
	allProposals.sort((a, b) => {
		const orderA = PROPOSAL_STATUS_ORDER[a.status] ?? 99;
		const orderB = PROPOSAL_STATUS_ORDER[b.status] ?? 99;
		if (orderA !== orderB) return orderA - orderB;
		return a.id.localeCompare(b.id) || a.path.localeCompare(b.path);
	});
	const activeProposals = allProposals.filter(
		(p) => p.status === 'draft' || p.status === 'review' || p.status === 'accepted'
	);

	// Sort and partition feedback
	allFeedback.sort((a, b) => {
		const orderA = FEEDBACK_SEVERITY_ORDER[a.severity] ?? 99;
		const orderB = FEEDBACK_SEVERITY_ORDER[b.severity] ?? 99;
		if (orderA !== orderB) return orderA - orderB;
		return a.id.localeCompare(b.id) || a.path.localeCompare(b.path);
	});
	const openFeedback = allFeedback.filter((f) => f.status === 'open');

	return {
		milestones: {
			all: allMilestones,
			open: openMilestones,
			totalCount: allMilestones.length,
			openCount: openMilestones.length
		},
		proposals: {
			all: allProposals,
			active: activeProposals,
			totalCount: allProposals.length,
			activeCount: activeProposals.length
		},
		feedback: {
			all: allFeedback,
			open: openFeedback,
			totalCount: allFeedback.length,
			openCount: openFeedback.length
		}
	};
}
