<script lang="ts">
	import { type RepositoryDocument } from '../../api/documents';
	import { clearRepositoryCache } from '../../api/cache';
	import {
		cachedDashboardPage,
		dashboardSections,
		openDashboardPage,
		nextDashboardPage,
		type SectionSnapshot,
		type DashboardSection
	} from './loading';
	import type { PlanningSource, RepositoryDataSource } from '../../api/repository';
	import { cachedOverlay, loadPlanningOverlay, type PlanningOverlay } from '../../api/planning';
	import { extractDashboardData, type DashboardData, type ProposalItemData } from './dashboard';

	let {
		source = null,
		repoId = '',
		branch = 'main',
		onNavigate = undefined
	}: {
		source?: RepositoryDataSource | null;
		repoId?: string;
		branch?: string;
		onNavigate?: (
			view: 'files' | 'book' | 'proposals' | 'specs' | 'roadmap' | 'shared',
			path?: string
		) => void;
	} = $props();

	type SectionState = {
		documents: RepositoryDocument[];
		loading: boolean;
		errors: string[];
		snapshot?: SectionSnapshot;
	};
	const emptySection = (): SectionState => ({ documents: [], loading: true, errors: [] });
	let sections = $state<Record<DashboardSection, SectionState>>({
		milestones: emptySection(),
		proposals: emptySection(),
		feedback: emptySection()
	});
	let refreshGeneration = $state(0);
	// The Planning overlay loads beside the sections and never delays or fails them.
	let overlay = $state.raw<PlanningOverlay | undefined>();
	let overlayLoading = $state(false);
	let overlayError = $state('');
	const loading = $derived(dashboardSections.some((section) => sections[section].loading));
	let controller: AbortController | undefined;
	async function loadMore(section: DashboardSection) {
		const repository = source;
		const ref = branch;
		const active = controller;
		const snapshot = sections[section].snapshot;
		if (!repository || !snapshot || !active || active.signal.aborted || sections[section].loading)
			return;
		sections[section] = { ...sections[section], loading: true };
		const result = await nextDashboardPage(repository, ref, section, snapshot, active.signal);
		if (!active.signal.aborted) sections[section] = { ...result, snapshot: result, loading: false };
	}
	function hasMore(section: DashboardSection) {
		const snapshot = sections[section].snapshot;
		return snapshot && snapshot.documents.length < snapshot.paths.length;
	}
	function sectionData(section: DashboardSection) {
		const state = sections[section];
		const metadata = new Map(state.snapshot?.metadata.map((doc) => [doc.path, doc]) ?? []);
		// Freeze ordering and membership from the list; bodies supply titles and summaries.
		return state.documents.map((doc) => ({
			...doc,
			meta: metadata.get(doc.path)?.meta ?? doc.meta
		}));
	}

	function refresh() {
		if (source) clearRepositoryCache(source);
		refreshGeneration++;
	}
	$effect(() => {
		const repository = source;
		const ref = branch;
		refreshGeneration;
		const active = new AbortController();
		controller = active;
		const known = repository ? cachedOverlay(repository, ref) : undefined;
		overlay = known;
		overlayError = '';
		overlayLoading = Boolean(repository?.planningProposals) && !known;
		if (repository?.planningProposals && !known)
			void loadPlanningOverlay(repository, ref, active.signal)
				.then((result) => {
					if (active.signal.aborted) return;
					overlay = result;
					overlayLoading = false;
				})
				.catch((error: unknown) => {
					if (active.signal.aborted) return;
					overlayError = error instanceof Error ? error.message : String(error);
					overlayLoading = false;
				});
		for (const section of dashboardSections) {
			const cached = repository ? cachedDashboardPage(repository, ref, section) : undefined;
			sections[section] = cached
				? { ...cached, snapshot: cached, loading: false }
				: { ...emptySection(), loading: Boolean(repository) };
			if (!repository || cached) continue;
			void openDashboardPage(repository, ref, section, active.signal)
				.then((result) => {
					if (!active.signal.aborted)
						sections[section] = { ...result, snapshot: result, loading: false };
				})
				.catch((error: unknown) => {
					if (!active.signal.aborted)
						sections[section] = {
							documents: [],
							loading: false,
							errors: [error instanceof Error ? error.message : String(error)]
						};
				});
		}
		return () => active.abort();
	});
	const data: DashboardData = $derived(
		extractDashboardData(
			dashboardSections.flatMap((section) => sections[section].snapshot?.metadata ?? [])
		)
	);
	const displayedMilestones = $derived(
		extractDashboardData(sectionData('milestones')).milestones.open
	);
	type ProposalCard = ProposalItemData & { source?: PlanningSource };
	const proposalData = (entry: { document: RepositoryDocument; source: PlanningSource }) => ({
		...extractDashboardData([entry.document]).proposals.all[0],
		source: entry.source
	});
	// Cards keep the list's order; the overlay replaces their content in place.
	const listedProposals = $derived.by((): ProposalCard[] => {
		const seed = sections.proposals.snapshot?.overlay ?? {};
		const live = overlay?.entries ?? {};
		return extractDashboardData(sectionData('proposals')).proposals.active.map((item) => {
			const entry = live[item.path] ?? seed[item.path];
			return entry ? proposalData(entry) : item;
		});
	});
	// Planning-only proposals the list does not hold join after its last page.
	const planningOnly = $derived.by((): ProposalCard[] => {
		const snapshot = sections.proposals.snapshot;
		if (!snapshot || !overlay) return [];
		const listed = new Set(snapshot.metadata.map((doc) => doc.path));
		const entries = Object.values(overlay.entries).filter(
			(entry) => !listed.has(entry.document.path)
		);
		const active = new Set(
			extractDashboardData(entries.map((entry) => entry.document)).proposals.active.map(
				(item) => item.path
			)
		);
		return entries
			.filter((entry) => active.has(entry.document.path))
			.map(proposalData)
			.sort((a, b) => a.id.localeCompare(b.id) || a.path.localeCompare(b.path));
	});
	const displayedProposals = $derived(
		hasMore('proposals') ? listedProposals : [...listedProposals, ...planningOnly]
	);
	const proposalCount = $derived(data.proposals.activeCount + planningOnly.length);
	const displayedFeedback = $derived(extractDashboardData(sectionData('feedback')).feedback.open);

	function handleItemClick(
		targetView: 'files' | 'book' | 'proposals' | 'specs' | 'roadmap' | 'shared',
		path?: string
	) {
		if (onNavigate) {
			onNavigate(targetView, path);
		}
	}
</script>

<div class="dashboard-wrapper">
	<div class="dashboard-container">
		<!-- Hidden Semantic AI Context & Operating Guidelines for Chrome Gemini / Assistive AI -->
		<section
			class="sr-only"
			role="note"
			aria-label="AI Assistant Instructions and SDD Dashboard Guide"
		>
			<h2>Project SDD Dashboard - AI Context and Operating Guidelines</h2>
			<p>
				This dashboard summarizes the current Spec-Driven Development status of repository: <strong
					>{repoId}</strong
				>
				on branch: <strong>{branch}</strong>.
			</p>
			<div class="ai-summary-metrics">
				<h3>Repository Status Counts:</h3>
				<ul>
					<li>
						Milestones: {#if sections.milestones.loading}Loading…{:else if sections.milestones.errors.length}Incomplete{:else}{data
								.milestones.openCount} open out of {data.milestones.totalCount} total{/if}
					</li>
					<li>
						Proposals: {#if sections.proposals.loading}Loading…{:else if sections.proposals.errors.length}Incomplete{:else}{proposalCount}
							active/draft out of {data.proposals.totalCount + planningOnly.length} total{/if}
					</li>
					<li>
						Feedback: {#if sections.feedback.loading}Loading…{:else if sections.feedback.errors.length}Incomplete{:else}{data
								.feedback.openCount} open out of {data.feedback.totalCount} total{/if}
					</li>
				</ul>
				<h3>Guidance for answering user queries:</h3>
				<ul>
					<li>
						<strong>Current status inquiries ("현재 작업 상황", "진행 상황"):</strong>
						Cite the active branch ({branch}), summarize open milestones, and describe active
						proposals under development or planning.
					</li>
					<li>
						<strong>Proposals inquiries ("proposal", "제안 현황"):</strong>
						Refer to the Active Proposals section. Mention status (draft/review/accepted), task kind,
						and planning/dev effort.
					</li>
					<li>
						<strong>Friction and blocker inquiries ("피드백", "문제점", "블로커"):</strong>
						Highlight critical and blocked items in Open Feedback and explain their workarounds or suggestions.
					</li>
					<li>
						<strong>Recommended CLI commands:</strong>
						`uv run devkit spec list`, `uv run devkit workflow next`.
					</li>
				</ul>
			</div>
		</section>

		<!-- Dashboard Header -->
		<header class="dashboard-header">
			<div class="header-main">
				<div class="title-row">
					<h1 class="dashboard-title">Dashboard</h1>
					<span class="repo-badge">{repoId} @ {branch}</span>
					<button class="nav-btn" onclick={refresh}>Refresh</button>
					{#if loading}
						<span class="loading-tag">Loading data...</span>
					{/if}
				</div>
				<p class="dashboard-subtitle">
					Consolidated operational overview: active work sessions, milestones, proposals, and
					feedback.
				</p>
			</div>

			<!-- Overview Stat Tiles -->
			<div class="stats-row">
				<div class="stat-card">
					<div class="stat-icon">🗺️</div>
					<div class="stat-content">
						<span class="stat-value"
							>{sections.milestones.loading || sections.milestones.errors.length
								? '—'
								: data.milestones.openCount}</span
						>
						<span class="stat-label">Open Milestones</span>
					</div>
				</div>
				<div class="stat-card">
					<div class="stat-icon">💡</div>
					<div class="stat-content">
						<span class="stat-value"
							>{sections.proposals.loading || sections.proposals.errors.length
								? '—'
								: proposalCount}</span
						>
						<span class="stat-label">Active Proposals</span>
					</div>
				</div>
				<div class="stat-card">
					<div class="stat-icon">⚠️</div>
					<div class="stat-content">
						<span class="stat-value"
							>{sections.feedback.loading || sections.feedback.errors.length
								? '—'
								: data.feedback.openCount}</span
						>
						<span class="stat-label">Open Feedback</span>
					</div>
				</div>
			</div>
		</header>

		<!-- Section 1: Active Worktree Sessions -->
		<section class="dashboard-section" aria-labelledby="section-sessions">
			<div class="section-header">
				<div class="section-title-wrap">
					<span class="section-icon">🚀</span>
					<h2 id="section-sessions" class="section-title">Active Worktree Sessions</h2>
				</div>
				<div class="section-actions">
					<span class="section-meta">Current: <code>{branch}</code></span>
				</div>
			</div>

			<div class="cards-grid">
				<!-- Current checkout session card -->
				<div class="dashboard-card session-card active-session">
					<div class="card-top">
						<span class="badge badge-branch">Current Branch</span>
						<span class="branch-pill">{branch}</span>
					</div>
					<h3 class="card-heading">Active Worktree Session</h3>
					<p class="card-desc">
						The viewer reads saved repository files from this checked-out branch.
					</p>
					<!-- AI Hidden details -->
					<div class="sr-only">
						Active repository {repoId}, checked-out branch {branch}.
					</div>
				</div>
			</div>
		</section>

		<!-- Section 2: Open Milestones -->
		<section
			class="dashboard-section"
			aria-labelledby="section-milestones"
			aria-busy={sections.milestones.loading}
		>
			<div class="section-header">
				<div class="section-title-wrap">
					<span class="section-icon">🗺️</span>
					<h2 id="section-milestones" class="section-title">Open Milestones</h2>
					<span class="count-badge"
						>{sections.milestones.loading || sections.milestones.errors.length
							? '—'
							: data.milestones.openCount}</span
					>
				</div>
				<div class="section-actions">
					{#if hasMore('milestones')}
						<button
							class="toggle-btn"
							disabled={sections.milestones.loading}
							onclick={() => loadMore('milestones')}
						>
							{sections.milestones.loading
								? 'Loading…'
								: sections.milestones.errors.length
									? 'Retry'
									: 'Load more'}
						</button>
					{/if}
					<button class="nav-btn" onclick={() => handleItemClick('roadmap')}>Roadmap View →</button>
				</div>
			</div>

			{#if sections.milestones.loading}
				<p role="status">Loading milestones…</p>
			{/if}
			{#if sections.milestones.errors.length}
				<div class="error-banner" role="alert">
					Could not load all milestones: {sections.milestones.errors.join('; ')}
				</div>
			{/if}
			<div class="cards-grid">
				{#each displayedMilestones as milestone (milestone.path)}
					<div
						class="dashboard-card clickable"
						role="button"
						tabindex="0"
						onclick={() => handleItemClick('roadmap')}
						onkeydown={(e) => e.key === 'Enter' && handleItemClick('roadmap')}
					>
						<div class="card-top">
							<span class="card-id">{milestone.id}</span>
							<span class="badge badge-status-{milestone.status}">{milestone.status}</span>
						</div>
						<h3 class="card-heading">{milestone.title}</h3>
						<p class="card-desc line-clamp-2">{milestone.summary || 'No summary provided.'}</p>
						{#if milestone.dependsOn.length > 0}
							<div class="card-tags">
								<span class="tag-label">Depends on:</span>
								{#each milestone.dependsOn as dep}
									<span class="tag">{dep}</span>
								{/each}
							</div>
						{/if}
						<!-- AI Hidden details -->
						<div class="sr-only">
							Full Milestone Details: ID {milestone.id}, Title: {milestone.title}, Status: {milestone.status},
							Path: {milestone.path}, Dependencies: {milestone.dependsOn.join(', ') || 'none'}. Full
							summary: {milestone.summary}.
						</div>
					</div>
				{:else}
					{#if !sections.milestones.loading && !sections.milestones.errors.length}
						<div class="dashboard-card empty-card">
							<p class="empty-text">No open milestones found.</p>
						</div>
					{/if}
				{/each}
			</div>
		</section>

		<!-- Section 3: Active Proposals -->
		<section
			class="dashboard-section"
			aria-labelledby="section-proposals"
			aria-busy={sections.proposals.loading}
		>
			<div class="section-header">
				<div class="section-title-wrap">
					<span class="section-icon">💡</span>
					<h2 id="section-proposals" class="section-title">Active Proposals</h2>
					<span class="count-badge"
						>{sections.proposals.loading || sections.proposals.errors.length
							? '—'
							: proposalCount}</span
					>
				</div>
				<div class="section-actions">
					{#if overlayLoading}
						<span class="section-meta">Checking Planning sources…</span>
					{:else if overlayError || overlay?.errors.length}
						<span class="section-meta overlay-note"
							>Planning overlay {overlayError ? 'unavailable' : 'incomplete'}: {overlayError ||
								overlay?.errors.join('; ')}</span
						>
					{/if}
					{#if hasMore('proposals')}
						<button
							class="toggle-btn"
							disabled={sections.proposals.loading}
							onclick={() => loadMore('proposals')}
						>
							{sections.proposals.loading
								? 'Loading…'
								: sections.proposals.errors.length
									? 'Retry'
									: 'Load more'}
						</button>
					{/if}
					<button class="nav-btn" onclick={() => handleItemClick('proposals')}
						>Proposals View →</button
					>
				</div>
			</div>

			{#if sections.proposals.loading}
				<p role="status">Loading proposals…</p>
			{/if}
			{#if sections.proposals.errors.length}
				<div class="error-banner" role="alert">
					Could not load all proposals: {sections.proposals.errors.join('; ')}
				</div>
			{/if}
			<div class="cards-grid">
				{#each displayedProposals as proposal (proposal.path)}
					<div
						class="dashboard-card clickable"
						role="button"
						tabindex="0"
						onclick={() => handleItemClick('proposals', proposal.path)}
						onkeydown={(e) => e.key === 'Enter' && handleItemClick('proposals', proposal.path)}
					>
						<div class="card-top">
							<span class="card-id">{proposal.id}</span>
							<span class="badge-group">
								{#if proposal.source}
									<span class="badge badge-source" title="Planning source"
										>{proposal.source.label}</span
									>
								{/if}
								<span class="badge badge-status-{proposal.status}">{proposal.status}</span>
							</span>
						</div>
						<h3 class="card-heading">{proposal.title}</h3>
						<p class="card-desc line-clamp-2">{proposal.summary || 'No summary provided.'}</p>
						<div class="card-tags">
							<span class="tag">kind: {proposal.taskKind}</span>
							<span class="tag">plan: {proposal.planningEffort}</span>
							<span class="tag">dev: {proposal.devEffort}</span>
						</div>
						<!-- AI Hidden details -->
						<div class="sr-only">
							Full Proposal Details: ID {proposal.id}, Title: {proposal.title}, Status: {proposal.status},
							Slug: {proposal.slug}, Task kind: {proposal.taskKind}, Planning effort: {proposal.planningEffort},
							Dev effort: {proposal.devEffort}, Path: {proposal.path}, Source: {proposal.source
								?.label ?? 'checkout'}. Full summary: {proposal.summary}.
						</div>
					</div>
				{:else}
					{#if !sections.proposals.loading && !sections.proposals.errors.length}
						<div class="dashboard-card empty-card">
							<p class="empty-text">No active proposals found.</p>
						</div>
					{/if}
				{/each}
			</div>
		</section>

		<!-- Section 4: Open Feedback -->
		<section
			class="dashboard-section"
			aria-labelledby="section-feedback"
			aria-busy={sections.feedback.loading}
		>
			<div class="section-header">
				<div class="section-title-wrap">
					<span class="section-icon">⚠️</span>
					<h2 id="section-feedback" class="section-title">Open Feedback & Blockers</h2>
					<span class="count-badge count-badge-amber"
						>{sections.feedback.loading || sections.feedback.errors.length
							? '—'
							: data.feedback.openCount}</span
					>
				</div>
				<div class="section-actions">
					{#if hasMore('feedback')}
						<button
							class="toggle-btn"
							disabled={sections.feedback.loading}
							onclick={() => loadMore('feedback')}
						>
							{sections.feedback.loading
								? 'Loading…'
								: sections.feedback.errors.length
									? 'Retry'
									: 'Load more'}
						</button>
					{/if}
					<button class="nav-btn" onclick={() => handleItemClick('files')}>Files View →</button>
				</div>
			</div>

			{#if sections.feedback.loading}
				<p role="status">Loading feedback…</p>
			{/if}
			{#if sections.feedback.errors.length}
				<div class="error-banner" role="alert">
					Could not load all feedback: {sections.feedback.errors.join('; ')}
				</div>
			{/if}
			<div class="cards-grid">
				{#each displayedFeedback as fb (fb.path)}
					<div
						class="dashboard-card clickable"
						role="button"
						tabindex="0"
						onclick={() => handleItemClick('files', fb.path)}
						onkeydown={(e) => e.key === 'Enter' && handleItemClick('files', fb.path)}
					>
						<div class="card-top">
							<span class="card-id">{fb.id}</span>
							<span class="badge badge-sev-{fb.severity}">{fb.severity}</span>
						</div>
						<h3 class="card-heading">{fb.title}</h3>
						<p class="card-desc line-clamp-2">{fb.summary || 'No summary text.'}</p>
						{#if fb.target}
							<div class="card-tags">
								<span class="tag-label">Target:</span>
								<span class="tag code-tag">{fb.target}</span>
							</div>
						{/if}
						<!-- AI Hidden details -->
						<div class="sr-only">
							Full Feedback Details: ID {fb.id}, Title: {fb.title}, Status: {fb.status}, Severity: {fb.severity},
							Category: {fb.category}, Scope: {fb.scope}, Target: {fb.target}, Origin: {fb.origin},
							Path: {fb.path}. Summary: {fb.summary}.
						</div>
					</div>
				{:else}
					{#if !sections.feedback.loading && !sections.feedback.errors.length}
						<div class="dashboard-card empty-card">
							<p class="empty-text">No open feedback items found.</p>
						</div>
					{/if}
				{/each}
			</div>
		</section>
	</div>
</div>

<style>
	/* Accessible Screen Reader & AI Hidden Pattern */
	.sr-only {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		white-space: nowrap;
		border-width: 0;
	}

	.dashboard-wrapper {
		width: 100%;
		height: 100%;
		overflow-y: auto;
		overflow-x: hidden;
		scrollbar-width: thin;
		scrollbar-color: var(--border-btn) transparent;
	}

	.dashboard-wrapper::-webkit-scrollbar {
		width: 8px;
		height: 8px;
	}

	.dashboard-wrapper::-webkit-scrollbar-track {
		background: transparent;
	}

	.dashboard-wrapper::-webkit-scrollbar-thumb {
		background-color: var(--border-btn);
		border-radius: 4px;
	}

	.dashboard-wrapper::-webkit-scrollbar-thumb:hover {
		background-color: var(--btn-hover-bg, #475569);
	}

	.dashboard-container {
		display: flex;
		flex-direction: column;
		gap: 28px;
		padding: 28px 32px;
		max-width: 1400px;
		margin: 0 auto;
		width: 100%;
		box-sizing: border-box;
		color: var(--text-primary);
	}

	/* Header */
	.dashboard-header {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.header-main {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.title-row {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.dashboard-title {
		margin: 0;
		font-size: 26px;
		font-weight: 700;
		letter-spacing: -0.02em;
	}

	.repo-badge {
		font-size: 12px;
		font-family: ui-monospace, SFMono-Regular, monospace;
		padding: 3px 8px;
		border-radius: 6px;
		background: var(--bg-panel);
		border: 1px solid var(--border-panel);
		color: var(--text-dim);
	}

	.loading-tag {
		font-size: 12px;
		color: var(--text-dim);
		font-style: italic;
	}

	.dashboard-subtitle {
		margin: 0;
		font-size: 14px;
		color: var(--text-dim);
	}

	/* Stat Tiles */
	.stats-row {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 14px;
	}

	.stat-card {
		display: flex;
		align-items: center;
		gap: 14px;
		padding: 14px 18px;
		background: var(--bg-panel);
		border: 1px solid var(--border-panel);
		border-radius: 10px;
	}

	.stat-icon {
		font-size: 24px;
	}

	.stat-content {
		display: flex;
		flex-direction: column;
	}

	.stat-value {
		font-size: 20px;
		font-weight: 700;
		line-height: 1.2;
	}

	.stat-label {
		font-size: 12px;
		color: var(--text-dim);
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.error-banner {
		display: flex;
		align-items: center;
		gap: 10px;
		padding: 12px 16px;
		background: rgba(239, 68, 68, 0.12);
		border: 1px solid #ef4444;
		border-radius: 8px;
		color: #ef4444;
		font-size: 13px;
	}

	/* Sections */
	.dashboard-section {
		display: flex;
		flex-direction: column;
		gap: 14px;
	}

	.section-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding-bottom: 8px;
		border-bottom: 1px solid var(--border-panel);
	}

	.section-title-wrap {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.section-icon {
		font-size: 18px;
	}

	.section-title {
		margin: 0;
		font-size: 18px;
		font-weight: 600;
		letter-spacing: -0.01em;
	}

	.count-badge {
		font-size: 11px;
		font-weight: 700;
		padding: 2px 7px;
		border-radius: 10px;
		background: var(--bg-btn);
		color: var(--text-primary);
	}

	.count-badge-amber {
		background: rgba(245, 158, 11, 0.2);
		color: #f59e0b;
	}

	.section-meta {
		font-size: 12px;
		color: var(--text-dim);
	}

	.section-actions {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.toggle-btn,
	.nav-btn {
		font-size: 12px;
		padding: 4px 10px;
		border-radius: 6px;
		border: 1px solid var(--border-panel);
		background: var(--bg-btn);
		color: var(--text-primary);
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.toggle-btn:hover,
	.nav-btn:hover {
		background: var(--border-panel);
	}

	/* Cards Grid */
	.cards-grid {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 14px;
	}

	@media (max-width: 1024px) {
		.cards-grid,
		.stats-row {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}

	@media (max-width: 640px) {
		.cards-grid,
		.stats-row {
			grid-template-columns: 1fr;
		}
	}

	.dashboard-card {
		display: flex;
		flex-direction: column;
		gap: 10px;
		padding: 16px;
		background: var(--bg-panel);
		border: 1px solid var(--border-panel);
		border-radius: 10px;
		box-sizing: border-box;
		transition:
			transform 0.15s ease,
			border-color 0.15s ease,
			box-shadow 0.15s ease;
	}

	.dashboard-card.clickable {
		cursor: pointer;
	}

	.dashboard-card.clickable:hover {
		transform: translateY(-2px);
		border-color: var(--accent, #3b82f6);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}

	.active-session {
		border-color: rgba(59, 130, 246, 0.5);
		background: linear-gradient(180deg, var(--bg-panel) 0%, rgba(59, 130, 246, 0.05) 100%);
	}

	.empty-card {
		padding: 24px;
		align-items: center;
		justify-content: center;
		border-style: dashed;
	}

	.empty-text {
		margin: 0;
		font-size: 13px;
		color: var(--text-dim);
	}

	/* Card Internal Elements */
	.card-top {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 8px;
	}

	.card-id {
		font-size: 12px;
		font-family: ui-monospace, SFMono-Regular, monospace;
		font-weight: 600;
		color: var(--text-dim);
	}

	.card-heading {
		margin: 0;
		font-size: 15px;
		font-weight: 600;
		line-height: 1.35;
		color: var(--text-primary);
	}

	.card-desc {
		margin: 0;
		font-size: 13px;
		color: var(--text-dim);
		line-height: 1.45;
	}

	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.card-tags {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 6px;
		margin-top: auto;
		padding-top: 4px;
	}

	.tag-label {
		font-size: 11px;
		color: var(--text-dim);
	}

	.tag {
		font-size: 11px;
		padding: 2px 6px;
		border-radius: 4px;
		background: var(--bg-btn);
		color: var(--text-primary);
	}

	.code-tag {
		font-family: ui-monospace, SFMono-Regular, monospace;
	}

	.badge-group {
		display: flex;
		align-items: center;
		gap: 6px;
	}

	.badge {
		font-size: 11px;
		font-weight: 600;
		padding: 2px 7px;
		border-radius: 5px;
		text-transform: uppercase;
		letter-spacing: 0.02em;
	}

	.badge-branch {
		background: #2563eb;
		color: #ffffff;
	}

	.badge-review {
		background: #7c3aed;
		color: #ffffff;
	}

	.badge-source {
		background: var(--bg-btn);
		color: var(--text-primary);
		text-transform: none;
		font-family: ui-monospace, SFMono-Regular, monospace;
	}

	.overlay-note {
		max-width: 360px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.badge-highlight {
		background: #10b981;
		color: #ffffff;
	}

	.branch-pill {
		font-size: 12px;
		font-family: ui-monospace, SFMono-Regular, monospace;
		padding: 2px 6px;
		border-radius: 4px;
		background: var(--bg-btn);
		color: var(--text-primary);
	}

	.timestamp-tag {
		font-size: 11px;
		color: var(--text-dim);
	}

	.card-bottom {
		margin-top: auto;
		padding-top: 6px;
	}

	.action-link {
		font-size: 12px;
		color: var(--accent, #3b82f6);
		font-weight: 500;
	}

	/* Status Colors */
	.badge-status-active {
		background: #10b981;
		color: #ffffff;
	}

	.badge-status-planned {
		background: #6366f1;
		color: #ffffff;
	}

	.badge-status-review {
		background: #f59e0b;
		color: #ffffff;
	}

	.badge-status-draft {
		background: var(--bg-btn);
		color: var(--text-dim);
	}

	.badge-status-accepted {
		background: #059669;
		color: #ffffff;
	}

	/* Severity Colors */
	.badge-sev-critical {
		background: #ef4444;
		color: #ffffff;
	}

	.badge-sev-blocked {
		background: #f97316;
		color: #ffffff;
	}

	.badge-sev-workaround {
		background: #eab308;
		color: #1f2937;
	}

	.badge-sev-friction {
		background: #3b82f6;
		color: #ffffff;
	}
</style>
