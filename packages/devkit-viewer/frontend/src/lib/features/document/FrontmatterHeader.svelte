<script lang="ts">
	import type { Frontmatter } from './document-parser';

	let { frontmatter }: { frontmatter: Frontmatter } = $props();
</script>

<div class="frontmatter-panel">
	<div class="fm-header">
		{#if frontmatter.id}
			<span class="fm-id-badge">{frontmatter.id}</span>
		{/if}
		{#if frontmatter.status}
			<span class="fm-status-badge status-{frontmatter.status}">
				{frontmatter.status}
			</span>
		{/if}
		{#if frontmatter.priority}
			<span class="fm-badge priority-{frontmatter.priority}">
				{frontmatter.priority}
			</span>
		{/if}
		{#if frontmatter.milestone}
			<span class="fm-badge milestone">
				🎯 {frontmatter.milestone}
			</span>
		{/if}
		{#if frontmatter.target_area}
			<span class="fm-badge area">
				📂 {frontmatter.target_area}
			</span>
		{/if}
	</div>
	{#if frontmatter.title}
		<h1 class="document-title">{frontmatter.title}</h1>
	{/if}
</div>

<style>
	.frontmatter-panel {
		background-color: var(--bg-panel);
		border: 1px solid var(--border-panel);
		border-radius: 8px;
		padding: 16px 20px;
		margin-bottom: 24px;
	}

	.fm-header {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 8px;
		margin-bottom: 10px;
	}

	.fm-id-badge {
		font-family: monospace;
		font-size: 12px;
		font-weight: 700;
		background-color: #1e1b4b;
		color: #a5b4fc;
		padding: 2px 8px;
		border-radius: 4px;
		border: 1px solid #4338ca;
	}

	.fm-status-badge {
		font-size: 11px;
		font-weight: 600;
		text-transform: uppercase;
		padding: 2px 8px;
		border-radius: 4px;
	}

	:global(.status-accepted),
	:global(.status-done) {
		background-color: #064e3b;
		color: #6ee7b7;
	}

	:global(.status-draft),
	:global(.status-reviewing) {
		background-color: #78350f;
		color: #fde68a;
	}

	.fm-badge {
		font-size: 11px;
		padding: 2px 8px;
		border-radius: 4px;
		background-color: var(--badge-bg);
		color: var(--badge-text);
	}

	.document-title {
		font-size: 20px;
		font-weight: 700;
		color: var(--text-primary);
		margin: 0;
	}
</style>

