# devkit-viewer (Svelte library)

The viewer of devkit repositories as a Svelte 5 component library: `SddViewer` (the Living Spec, proposals, specs,
roadmap and file tabs), `KnowledgeViews`, `RoadmapView`, `buildRoadmap`, `httpDataSource` and the
`RepositoryDataSource` contract a host implements (`info`, `tree(path, ref)`, `blob(path, ref)`, optional `refs`, `treeRecursive(path, ref)`, `dashboardList(section, ref, signal)`, `planningProposals(signal)`, `planningTree(source, path, signal)` and `planningBlob(source, path, signal)`).

```svelte
<script lang="ts">
	import { SddViewer, type RepositoryDataSource } from 'devkit-viewer';
	let { source }: { source: RepositoryDataSource } = $props();
</script>

<SddViewer dataSource={source} branch="main" initialView="book" />
```

Keep the same data-source object across tab visits to reuse the 30-second parsed-result cache. An optional `treeRecursive` returns all descendant metadata in the same shape as `tree`; hosts without it use bounded directory discovery. `httpDataSource` implements it for the local server. Dashboard sections load separately; Dashboard Refresh invalidates source caches.

It is not published to a registry. A host vendors the tarball built from a pinned devkit commit:

```sh
just viewer install
just viewer pack /absolute/path/to/host/vendor   # writes devkit-viewer-<version>.tgz there
```

and depends on it with `"devkit-viewer": "file:vendor/devkit-viewer-<version>.tgz"`, reinstalling it to refresh the
lockfile integrity. Contract: `CAP-VIEW-repository-viewer` in the devkit repository.

`dashboardList` returns `{items: RepositoryBlob[], errors: string[]}` for `milestones`, `proposals` or `feedback`. Each item contains only UTF-8 frontmatter, including delimiters, or empty content when there is no frontmatter. The browser derives status/severity ordering and exact counts before fetching only visible full bodies. Load more appends 6 milestones, 9 proposals or 6 feedback entries. Cached lists retain loaded pages and their displayed count for 30 seconds from list completion; page loads do not renew expiry. Refresh resets the list and first page. Hosts without this optional method retain selective full scans on cold load and paged rendering.

`planningProposals` returns `{sources, items, errors}`: each Planning source (`{id, kind, label, slug}`) and its own `docs/proposals/PROP-<slug>/proposal.md`. The Dashboard and Proposals tab request it after the checkout and update matching proposals in place with the source label; `planningTree` and `planningBlob` read an overlaid proposal's bundle from that source. The last loaded overlay seeds the next proposal list build. Hosts without these optional methods show the checkout only.
