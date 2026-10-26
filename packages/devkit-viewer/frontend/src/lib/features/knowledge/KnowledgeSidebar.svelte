<script lang="ts">
	import type { RepositoryDocument, RenderedDocument } from '../../api/documents';
	import { bookGroups, bookGroup, documentAnchor } from '../../api/documents';

	let {
		view,
		namespace = $bindable('all'),
		namespaces = [],
		query = $bindable(''),
		status = $bindable(''),
		statuses = [],
		priority = $bindable(''),
		size = $bindable(''),
		area = $bindable(''),
		areas = [],
		includeCompleted = $bindable(false),
		book = [],
		entries = [],
		sources = {},
		selected = null,
		currentAnchor = '',
		rendered,
		onJump,
		onSelect
	}: {
		view: 'book' | 'proposals' | 'specs';
		namespace?: string;
		namespaces?: string[];
		query?: string;
		status?: string;
		statuses?: string[];
		priority?: string;
		size?: string;
		area?: string;
		areas?: string[];
		includeCompleted?: boolean;
		book?: RepositoryDocument[];
		entries?: RepositoryDocument[];
		/** Planning source label by overlaid proposal path. */
		sources?: Record<string, string>;
		selected?: RepositoryDocument | null;
		currentAnchor?: string;
		rendered: Map<string, RenderedDocument>;
		onJump: (path: string, anchor?: string) => void;
		onSelect: (doc: RepositoryDocument) => void;
	} = $props();
</script>

<aside class="outline" aria-label={view === 'book' ? 'Table of contents' : 'Bundle list'}>
	<div class="filters">
		<label>
			Scope
			<select aria-label="Scope" bind:value={namespace}>
				<option value="all">All</option>
				{#each namespaces as name}
					<option value={name}>{name === 'global' ? 'Global' : name + ' + Global'}</option>
				{/each}
			</select>
		</label>
		{#if view !== 'book'}
			<input aria-label="Search title or ID" placeholder="Search title or ID" bind:value={query} />
			<div class="filter-row">
				<select aria-label="Status" bind:value={status}>
					<option value="">All statuses</option>
					{#each statuses as s}
						<option value={s}>{s}</option>
					{/each}
				</select>
				{#if view === 'proposals'}
					<select aria-label="Priority" bind:value={priority}>
						<option value="">All priorities</option>
						{#each ['critical', 'high', 'medium', 'low'] as p}
							<option value={p}>{p}</option>
						{/each}
					</select>
				{/if}
			</div>
			{#if view === 'proposals'}
				<div class="filter-row">
					<select aria-label="Size" bind:value={size}>
						<option value="">All sizes</option>
						{#each ['S', 'M', 'L', 'XL'] as s}
							<option value={s}>{s}</option>
						{/each}
					</select>
					<select aria-label="Target area" bind:value={area}>
						<option value="">All areas</option>
						{#each areas as a}
							<option value={a}>{a}</option>
						{/each}
					</select>
				</div>
			{:else}
				<label class="checkbox-label">
					<input type="checkbox" bind:checked={includeCompleted} /> Include completed
				</label>
			{/if}
		{/if}
	</div>
	{#if view === 'book'}
		{#each bookGroups as group}
			{#if book.some((d) => bookGroup(d) === group)}
				<h2>{group}</h2>
			{/if}
			{#each book.filter((d) => bookGroup(d) === group) as doc}
				<button
					class:active={currentAnchor === documentAnchor(doc.path) ||
						currentAnchor === rendered.get(doc.path)?.headings[0]?.id}
					onclick={() => onJump(doc.path)}
				>
					{doc.title}
				</button>
				{#each rendered
					.get(doc.path)
					?.headings.filter((h) => h.level > 1 && h.level <= 3) ?? [] as heading}
					<button
						class="subheading"
						class:active={currentAnchor === heading.id}
						style:padding-left={`${heading.level * 8}px`}
						onclick={() => onJump(doc.path, heading.id)}
					>
						{heading.title}
					</button>
				{/each}
			{/each}
		{/each}
	{:else}
		<p class="count">{entries.length} {view === 'proposals' ? 'proposals' : 'specs'}</p>
		{#each entries as doc}
			<button
				class="entry"
				class:active={selected?.path === doc.path}
				onclick={() => onSelect(doc)}
			>
				<strong>{doc.title}</strong>
				<span>{doc.meta.id}</span>
				{#if sources[doc.path]}
					<span class="source" title="Planning source">{sources[doc.path]}</span>
				{/if}
				<span>
					{[
						doc.meta.status,
						doc.meta.priority,
						doc.meta.size,
						doc.meta.target_area,
						doc.meta.milestone
					]
						.filter(Boolean)
						.join(' · ')}
				</span>
			</button>
		{/each}
		{#if !entries.length}
			<p>No matching items found.</p>
		{/if}
	{/if}
</aside>

<style>
	.outline {
		overflow: auto;
		padding: 16px;
		border-right: 1px solid var(--border-panel);
	}

	.filters {
		display: flex;
		flex-direction: column;
		gap: 8px;
		padding-bottom: 12px;
		border-bottom: 1px solid var(--border-panel);
		margin-bottom: 12px;
	}

	.filter-row {
		display: flex;
		gap: 6px;
	}

	.filter-row select {
		flex: 1;
		min-width: 0;
	}

	.checkbox-label {
		display: flex;
		align-items: center;
		gap: 6px;
		font-size: 12px;
		color: var(--text-secondary);
	}

	label {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 8px;
		font-size: 12px;
	}

	label select {
		flex: 1;
		min-width: 0;
	}

	button,
	input,
	select {
		font: inherit;
		color: var(--text-primary);
	}

	input,
	select {
		padding: 6px 8px;
		font-size: 12px;
		border: 1px solid var(--border-input);
		background: var(--bg-input);
		border-radius: 6px;
	}

	button {
		cursor: pointer;
		border: 1px solid var(--border-panel);
		border-radius: 6px;
		background: var(--bg-panel);
		padding: 8px 10px;
		text-align: left;
	}

	button:hover,
	button.active {
		background: var(--tree-selected-bg);
		color: var(--tree-selected-text);
	}

	button:focus-visible {
		outline: 2px solid var(--tree-selected-text);
		outline-offset: 2px;
	}

	.outline h2 {
		font-size: 13px;
		color: var(--text-muted);
		margin: 22px 0 10px;
	}

	.outline button {
		display: block;
		width: 100%;
		border: 0;
		margin: 3px 0;
		background: transparent;
	}

	.outline button.active,
	.outline button:hover {
		background: var(--tree-selected-bg);
	}

	.subheading {
		font-size: 12px;
		color: var(--text-muted);
	}

	.entry {
		display: flex !important;
		flex-direction: column;
		gap: 6px;
		padding: 12px;
		border-bottom: 1px solid var(--border-panel) !important;
	}

	.entry span,
	.count {
		font-size: 12px;
		color: var(--text-muted);
	}

	.entry .source {
		font-family: ui-monospace, SFMono-Regular, monospace;
		color: var(--text-secondary);
	}
</style>
