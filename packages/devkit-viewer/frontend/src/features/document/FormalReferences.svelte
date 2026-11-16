<script lang="ts">
	import type { TreeItem } from '../../api/repository';
	import type { RepositoryDocument } from '../../api/documents';
	import { documentId, hasFormalContext, supportRoot } from '../../api/identity';
	import { deriveReferences, metadataText, type ReferenceRow } from './references';
	let {
		subject,
		documents = [],
		files = [],
		onSupportingOpen = () => {},
		loading = false,
		errors = [],
		onOpen = () => {},
		onReload = () => {}
	}: {
		subject: RepositoryDocument;
		documents?: RepositoryDocument[];
		files?: TreeItem[];
		onSupportingOpen?: (path: string) => void;
		loading?: boolean;
		errors?: string[];
		onOpen?: (path: string) => void;
		onReload?: () => void;
	} = $props();
	const root = $derived(supportRoot(subject));
	const support = $derived(
		root
			? files.filter(
					(file) =>
						file.type === 'blob' && file.path.startsWith(root!) && file.path !== subject.path
				)
			: []
	);
	const refs = $derived(deriveReferences(subject, documents));
</script>

{#snippet rows(values: ReferenceRow[])}
	<ul>
		{#each values as row}<li>
				{#if row.path}<button onclick={() => onOpen(row.path!)}>{row.id} — {row.title}</button
					>{:else}<span>{row.written} — unavailable ({row.unavailable})</span>{/if}
				<small
					>{row.field}{row.status ? ' · ' + row.status : ''}{row.written !== row.id
						? ' · written as ' + row.written
						: ''}{row.referencedAs ? ' · refers to ' + row.referencedAs : ''}</small
				>
			</li>{/each}
	</ul>
{/snippet}
{#if hasFormalContext(subject)}
	<aside class="formal-references" aria-label={`References for ${documentId(subject)}`}>
		<h3>Document context</h3>
		<small>{subject.path}</small>
		{#if loading}<p role="status">Loading references…</p>{/if}
		{#if errors.length || refs.issues.length}<div role="status">
				<strong>Incomplete reference information</strong>
				{#each [...errors, ...refs.issues] as issue}<p>{issue}</p>{/each}<button onclick={onReload}
					>Reload references</button
				>
			</div>{/if}
		<h4>Outgoing references</h4>
		{#if refs.outgoing.length}{@render rows(refs.outgoing)}{:else}<p>
				{loading || errors.length || refs.issues.length
					? 'No outgoing references found in the documents read.'
					: 'No outgoing references.'}
			</p>{/if}
		<h4>Incoming references</h4>
		{#if refs.incoming.length}{@render rows(refs.incoming)}{:else}<p>
				{loading || errors.length || refs.issues.length
					? 'No incoming references found in the documents read.'
					: 'No incoming references.'}
			</p>{/if}
		{#if refs.provenance.length}<h4>Provenance (historical origin)</h4>
			{@render rows(refs.provenance)}{/if}
		{#if root}<h4>Supporting files</h4>
			{#if support.length}<ul>
					{#each support as file}<li>
							<button onclick={() => onSupportingOpen(file.path)}
								>{file.path.slice(root.length)}</button
							>
						</li>{/each}
				</ul>
			{:else}<p>
					{loading || errors.length
						? 'Supporting file inventory incomplete.'
						: 'No supporting files.'}
				</p>{/if}
		{/if}
		<details>
			<summary>Metadata and declared source entrypoints</summary>
			<p>
				Declarations are shown as written; this viewer does not validate source liveness or document
				governance.
			</p>
			<dl>
				{#each Object.entries(subject.meta) as [key, value]}<dt>{key}</dt>
					<dd>{metadataText(value)}</dd>{/each}
			</dl>
		</details>
	</aside>
{/if}

<style>
	.formal-references {
		border: 1px solid var(--border-panel);
		border-radius: 8px;
		padding: 12px 16px;
		margin: 16px 0;
		overflow-wrap: anywhere;
	}
	h3,
	h4 {
		margin: 10px 0;
	}
	ul {
		padding-left: 20px;
	}
	li {
		margin: 8px 0;
	}
	small {
		display: block;
		color: var(--text-muted);
	}
	button {
		font: inherit;
		color: var(--tree-selected-text);
		background: transparent;
		border: 0;
		cursor: pointer;
		text-align: left;
		text-decoration: underline;
	}
	dt {
		font-weight: bold;
	}
	dd {
		white-space: pre-wrap;
		margin: 4px 0 10px;
	}
</style>
