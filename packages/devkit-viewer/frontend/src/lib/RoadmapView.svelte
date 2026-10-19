<script lang="ts">
	import type { RepositoryDocument } from './documents';
	import type { RepositoryDataSource } from './repository';
	import {
		buildRoadmap,
		isActivityBranch,
		loadRoadmapDocuments,
		type BranchDocuments
	} from './roadmap';

	let {
		source,
		branch,
		onOpen
	}: {
		source: RepositoryDataSource | null;
		branch: string;
		onOpen: (path: string) => void;
	} = $props();

	let base = $state<RepositoryDocument[]>([]);
	let branches = $state<BranchDocuments[]>([]);
	let errors = $state<string[]>([]);
	let loading = $state(false);
	let branchesUnavailable = $state(false);
	let history = $state(false);

	$effect(() => {
		const repository = source,
			ref = branch;
		const controller = new AbortController();
		base = [];
		branches = [];
		errors = [];
		branchesUnavailable = false;
		loading = Boolean(repository);
		if (repository)
			void (async () => {
				const signal = controller.signal;
				const selected = await loadRoadmapDocuments(repository, ref, signal);
				let names: string[] = [];
				if (repository.refs) {
					try {
						names = (await repository.refs(signal)).branches.filter(
							(name) => name !== ref && isActivityBranch(name)
						);
					} catch {
						if (!signal.aborted) branchesUnavailable = true;
					}
				} else branchesUnavailable = true;
				const others = await Promise.all(
					names.map(async (name) => ({
						name,
						...(await loadRoadmapDocuments(repository, name, signal))
					}))
				);
				if (signal.aborted) return;
				base = selected.documents;
				branches = others.map(({ name, documents }) => ({ name, documents }));
				errors = [
					...selected.errors,
					...others.flatMap((o) => o.errors.map((error) => `${o.name}: ${error}`))
				];
				loading = false;
			})();
		return () => controller.abort();
	});

	const milestones = $derived(buildRoadmap(base, branches, { history }));
</script>

<div class="roadmap">
	<div class="filters">
		<label><input type="checkbox" bind:checked={history} /> 완료·중단 포함</label>
		{#if branchesUnavailable}
			<span class="note">작업 브랜치를 읽을 수 없어 {branch} 브랜치만 표시합니다.</span>
		{:else if branches.length}
			<span class="note">작업 브랜치 {branches.length}개 포함</span>
		{/if}
	</div>
	{#if errors.length}<details class="index-errors">
			<summary>불러오지 못한 문서 {errors.length}개</summary>{#each errors as error}<p>
					{error}
				</p>{/each}
		</details>{/if}
	{#if loading}<p role="status">로드맵을 불러오는 중…</p>
	{:else if !source}<p>저장소를 연결하면 로드맵을 볼 수 있습니다.</p>
	{:else if !milestones.length}<p class="empty">표시할 마일스톤이 없습니다.</p>
	{:else}
		<ol class="milestones">
			{#each milestones as milestone (milestone.id)}
				<li class="milestone">
					<header>
						<span class="id">{milestone.id}</span>
						<span class="status status-{milestone.status}">{milestone.status}</span>
						{#if milestone.ready}
							<span class="readiness ready">시작 가능</span>
						{:else}
							{#if milestone.waitingFor.length}
								<span class="readiness waiting">선행 대기: {milestone.waitingFor.join(', ')}</span>
							{/if}
							{#if milestone.unknown.length}
								<span class="readiness unknown"
									>알 수 없는 선행: {milestone.unknown.join(', ')}</span
								>
							{/if}
						{/if}
						<button onclick={() => onOpen(milestone.path)}>원본 보기</button>
					</header>
					<h2>{milestone.title}</h2>
					{#if milestone.members.length}
						<ul class="members">
							{#each milestone.members as member (member.id)}
								<li>
									<span class="settled" class:done={member.settled}
										>{member.settled ? '정리됨' : '진행 중'}</span
									>
									{#if member.branch}
										<span class="title">{member.title}</span>
										<span class="branch">🌿 {member.branch}</span>
									{:else}
										<button class="title" onclick={() => onOpen(member.path)}>{member.title}</button
										>
									{/if}
									<span class="meta">{member.id} · {member.status}</span>
								</li>
							{/each}
						</ul>
					{:else}
						<p class="empty-members">구성원 없음</p>
					{/if}
				</li>
			{/each}
		</ol>
	{/if}
</div>

<style>
	.roadmap {
		height: 100%;
		overflow: auto;
		color: var(--text-primary);
	}
	.filters {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 16px;
		padding: 16px;
		border-bottom: 1px solid var(--border-panel);
		font-size: 13px;
	}
	.note {
		color: var(--text-muted);
	}
	.milestones {
		list-style: none;
		margin: 0 auto;
		padding: 24px 16px;
		max-width: 960px;
		display: flex;
		flex-direction: column;
		gap: 16px;
	}
	.milestone {
		border: 1px solid var(--border-panel);
		border-radius: 8px;
		background: var(--bg-panel);
		padding: 16px 20px;
	}
	.milestone header {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 8px;
	}
	.milestone h2 {
		font-size: 17px;
		margin: 10px 0;
	}
	.id {
		font-family: monospace;
		font-size: 12px;
		font-weight: 700;
		color: var(--tree-selected-text);
	}
	.status,
	.readiness,
	.branch,
	.settled {
		font-size: 11px;
		padding: 2px 8px;
		border-radius: 4px;
		background: var(--badge-bg);
		color: var(--badge-text);
	}
	.status-active,
	.ready,
	.settled.done {
		background: #064e3b;
		color: #6ee7b7;
	}
	.status-planned,
	.waiting {
		background: #78350f;
		color: #fde68a;
	}
	.unknown {
		background: #7f1d1d;
		color: #fecaca;
	}
	button {
		font: inherit;
		cursor: pointer;
		color: var(--text-primary);
		border: 1px solid var(--border-panel);
		border-radius: 6px;
		background: var(--bg-btn);
		padding: 4px 10px;
		font-size: 12px;
	}
	header button {
		margin-left: auto;
	}
	button:hover {
		background: var(--tree-selected-bg);
		color: var(--tree-selected-text);
	}
	button:focus-visible {
		outline: 2px solid var(--tree-selected-text);
	}
	.members {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}
	.members li {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 8px;
		font-size: 13px;
	}
	.members .title {
		border: 0;
		background: transparent;
		padding: 0;
		font-size: 13px;
		text-align: left;
	}
	.meta,
	.empty-members,
	.empty {
		color: var(--text-muted);
		font-size: 12px;
	}
	.empty {
		text-align: center;
		margin: 80px 0;
	}
	.index-errors {
		padding: 12px 16px;
		color: var(--text-secondary);
	}
	.index-errors p {
		font-size: 12px;
		overflow-wrap: anywhere;
	}
</style>
