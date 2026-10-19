# devkit-viewer (Svelte library)

The viewer of devkit repositories as a Svelte 5 component library: `SddViewer` (the Living Spec, proposals, specs,
roadmap and file tabs), `KnowledgeViews`, `RoadmapView`, `buildRoadmap`, `httpDataSource` and the
`RepositoryDataSource` contract a host implements (`info`, `tree(path, ref)`, `blob(path, ref)`, optional `refs`).

```svelte
<script lang="ts">
	import { SddViewer, type RepositoryDataSource } from 'devkit-viewer';
	let { source }: { source: RepositoryDataSource } = $props();
</script>

<SddViewer dataSource={source} branch="main" initialView="book" />
```

It is not published to a registry. A host vendors the tarball built from a pinned devkit commit:

```sh
just viewer install
just viewer pack /absolute/path/to/host/vendor   # writes devkit-viewer-<version>.tgz there
```

and depends on it with `"devkit-viewer": "file:vendor/devkit-viewer-<version>.tgz"`, reinstalling it to refresh the
lockfile integrity. Contract: `CAP-VIEW-repository-viewer` in the devkit repository.
