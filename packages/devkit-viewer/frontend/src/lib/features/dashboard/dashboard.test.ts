import { describe, expect, it } from 'vitest';
import type { RepositoryDocument } from '../../api/documents';
import { extractDashboardData } from './dashboard';

describe('extractDashboardData', () => {
	it('handles empty document list', () => {
		const result = extractDashboardData([]);
		expect(result.milestones.totalCount).toBe(0);
		expect(result.milestones.openCount).toBe(0);
		expect(result.proposals.totalCount).toBe(0);
		expect(result.proposals.activeCount).toBe(0);
		expect(result.feedback.totalCount).toBe(0);
		expect(result.feedback.openCount).toBe(0);
	});

	it('extracts and sorts milestones correctly', () => {
		const docs: RepositoryDocument[] = [
			{
				path: 'docs/roadmap/MS-catalog.md',
				meta: { id: 'MS-catalog', status: 'planned', depends_on: ['MS-auth'] },
				body: 'Milestone summary text',
				raw: '',
				title: 'Catalog'
			},
			{
				path: 'docs/roadmap/MS-auth.md',
				meta: { id: 'MS-auth', status: 'active', summary: 'Authentication milestone' },
				body: '',
				raw: '',
				title: 'Authentication'
			},
			{
				path: 'docs/roadmap/MS-old.md',
				meta: { id: 'MS-old', status: 'done' },
				body: 'Done milestone',
				raw: '',
				title: 'Old'
			}
		];

		const result = extractDashboardData(docs);
		expect(result.milestones.totalCount).toBe(3);
		expect(result.milestones.openCount).toBe(2);
		// Active before planned
		expect(result.milestones.open[0].id).toBe('MS-auth');
		expect(result.milestones.open[0].status).toBe('active');
		expect(result.milestones.open[0].summary).toBe('Authentication milestone');
		expect(result.milestones.open[1].id).toBe('MS-catalog');
		expect(result.milestones.open[1].dependsOn).toEqual(['MS-auth']);
	});

	it('extracts and sorts proposals correctly', () => {
		const docs: RepositoryDocument[] = [
			{
				path: 'docs/proposals/PROP-feature-b/proposal.md',
				meta: {
					id: 'PROP-feature-b',
					status: 'draft',
					task_kind: 'feature',
					planning_effort: 'high',
					dev_effort: 'medium'
				},
				body: 'Feature B description',
				raw: '',
				title: 'Feature B'
			},
			{
				path: 'docs/proposals/PROP-feature-a/proposal.md',
				meta: {
					id: 'PROP-feature-a',
					status: 'review',
					task_kind: 'refactor',
					summary: 'Feature A under review'
				},
				body: '',
				raw: '',
				title: 'Feature A'
			},
			{
				path: 'docs/proposals/PROP-feature-c/proposal.md',
				meta: { id: 'PROP-feature-c', status: 'rejected' },
				body: '',
				raw: '',
				title: 'Feature C'
			}
		];

		const result = extractDashboardData(docs);
		expect(result.proposals.totalCount).toBe(3);
		expect(result.proposals.activeCount).toBe(2);
		// Review before draft
		expect(result.proposals.active[0].id).toBe('PROP-feature-a');
		expect(result.proposals.active[0].status).toBe('review');
		expect(result.proposals.active[0].slug).toBe('feature-a');
		expect(result.proposals.active[1].id).toBe('PROP-feature-b');
		expect(result.proposals.active[1].status).toBe('draft');
	});

	it('extracts and sorts feedback by severity', () => {
		const docs: RepositoryDocument[] = [
			{
				path: 'specs/2026-10/unit-1/feedback/fb-low.md',
				meta: {
					id: 'FB-low',
					status: 'open',
					severity: 'friction',
					target: 'skill.md'
				},
				body: 'Friction details',
				raw: '',
				title: 'Friction item'
			},
			{
				path: 'specs/2026-10/unit-1/feedback/fb-crit.md',
				meta: {
					id: 'FB-crit',
					status: 'open',
					severity: 'critical',
					target: 'core.py'
				},
				body: 'Critical blocker details',
				raw: '',
				title: 'Critical issue'
			},
			{
				path: 'specs/2026-10/unit-1/feedback/fb-resolved.md',
				meta: { id: 'FB-resolved', status: 'resolved', severity: 'critical' },
				body: '',
				raw: '',
				title: 'Resolved issue'
			}
		];

		const result = extractDashboardData(docs);
		expect(result.feedback.totalCount).toBe(3);
		expect(result.feedback.openCount).toBe(2);
		// Critical before friction
		expect(result.feedback.open[0].id).toBe('FB-crit');
		expect(result.feedback.open[0].severity).toBe('critical');
		expect(result.feedback.open[1].id).toBe('FB-low');
		expect(result.feedback.open[1].severity).toBe('friction');
	});
});

