<script lang="ts">
	import type { Milestone } from '../../api/roadmap';

	let {
		milestone,
		canOpenBase = true,
		canOpenMember,
		onOpen
	}: {
		milestone: Milestone;
		canOpenBase?: boolean;
		canOpenMember: (branch: string | null) => boolean;
		onOpen: (path: string) => void;
	} = $props();
</script>

<li class="milestone">
	<header>
		<span class="id">{milestone.id}</span>
		<span class="status status-{milestone.status}">{milestone.status}</span>
		{#if milestone.ready}
			<span class="readiness ready">Ready</span>
		{:else}
			{#if milestone.waitingFor.length}
				<span class="readiness waiting">Blocked by: {milestone.waitingFor.join(', ')}</span>
			{/if}
			{#if milestone.unknown.length}
				<span class="readiness unknown">Unknown dependencies: {milestone.unknown.join(', ')}</span>
			{/if}
		{/if}
		{#if canOpenBase}
			<button onclick={() => onOpen(milestone.path)}>View raw</button>
		{/if}
	</header>
	<h2>{milestone.title}</h2>
	{#if milestone.members.length}
		<ul class="members">
			{#each milestone.members as member (member.id)}
				<li>
					<span class="settled" class:done={member.settled}>
						{member.settled ? 'Settled' : 'In progress'}
					</span>
					{#if canOpenMember(member.branch)}
						<button class="title" onclick={() => onOpen(member.path)}>{member.title}</button>
					{:else}
						<span class="title">{member.title}</span>
					{/if}
					{#if member.branch}
						<span class="branch">🌿 {member.branch}</span>
					{/if}
					<span class="meta">{member.id} · {member.status}</span>
				</li>
			{/each}
		</ul>
	{:else}
		<p class="empty-members">No members</p>
	{/if}
</li>

<style>
	.milestone {
		padding: 24px;
		border: 1px solid var(--border-panel);
		border-radius: 8px;
		background: var(--bg-panel);
		margin-bottom: 24px;
	}

	.milestone header {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 8px;
		margin-bottom: 12px;
	}

	.milestone h2 {
		font-size: 20px;
		margin: 0 0 16px 0;
	}

	.id {
		font-weight: 700;
		font-family: monospace;
	}

	.status,
	.readiness {
		font-size: 11px;
		text-transform: uppercase;
		padding: 2px 6px;
		border-radius: 4px;
		font-weight: 600;
	}

	.status-active {
		background: #0284c7;
		color: #ffffff;
	}

	.status-planned {
		background: #475569;
		color: #f1f5f9;
	}

	.status-done {
		background: #166534;
		color: #dcfce7;
	}

	.status-dropped {
		background: #7f1d1d;
		color: #fecaca;
	}

	.readiness.ready {
		background: #166534;
		color: #dcfce7;
	}

	.readiness.waiting,
	.readiness.unknown {
		background: #854d0e;
		color: #fef9c3;
	}

	button {
		margin-left: auto;
		cursor: pointer;
		border: 1px solid var(--border-input);
		border-radius: 4px;
		background: transparent;
		color: var(--text-muted);
		padding: 2px 8px;
		font-size: 11px;
	}

	button:hover {
		background: var(--tree-hover-bg);
		color: var(--text-primary);
	}

	.members {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.members li {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 8px 12px;
		background: var(--bg-viewport);
		border: 1px solid var(--border-panel);
		border-radius: 6px;
		font-size: 13px;
	}

	.settled {
		font-size: 11px;
		padding: 2px 6px;
		border-radius: 4px;
		background: #854d0e;
		color: #fef9c3;
	}

	.settled.done {
		background: #166534;
		color: #dcfce7;
	}

	.title {
		flex: 1;
		font-weight: 500;
		text-align: left;
		background: none;
		border: none;
		padding: 0;
		margin: 0;
		color: var(--text-primary);
	}

	button.title:hover {
		text-decoration: underline;
		background: none;
	}

	.branch {
		font-size: 11px;
		color: var(--text-muted);
	}

	.meta {
		font-size: 11px;
		color: var(--text-dim);
		font-family: monospace;
	}

	.empty-members {
		color: var(--text-dim);
		font-size: 13px;
		margin: 0;
	}
</style>
