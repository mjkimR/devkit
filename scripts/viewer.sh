#!/usr/bin/env bash
# Frontend commands of the devkit-viewer package (packages/devkit-viewer/frontend); they need Node and npm:
#   viewer.sh install   npm ci
#   viewer.sh lint      prettier --check
#   viewer.sh check     svelte-check, warnings fail
#   viewer.sh test      vitest
#   viewer.sh build     rebuild the committed page into src/devkit_viewer/static/ (artifact viewer-assets)
#   viewer.sh pack [DIR]
#                       package the library and write its npm pack tarball into DIR (default: frontend/dist-pack),
#                       after checking the tarball holds the library only and exports what autohub imports
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../packages/devkit-viewer/frontend"

action=${1:?Expected an action: install, lint, check, test, build or pack}
case "$action" in
    install) npm ci --no-audit --no-fund ;;
    lint) npm run --silent lint ;;
    check) npm run --silent check ;;
    test) npm run --silent test ;;
    build) npm run --silent build:app ;;
    pack)
        out=${2:-dist-pack}
        mkdir -p "$out"
        npm run --silent package
        listing=$(npm pack --dry-run --json)
        node --input-type=module - "$listing" <<'NODE'
import { readFileSync } from 'node:fs';
const [{ files }] = JSON.parse(process.argv[2]);
const pkg = JSON.parse(readFileSync('package.json', 'utf8'));
const problems = [];
const extra = files.map((f) => f.path).filter((p) => !p.startsWith('dist/') && !['package.json', 'README.md'].includes(p));
if (extra.length) problems.push(`files outside the library: ${extra.join(', ')}`);
if (files.some((f) => /\.test\./.test(f.path))) problems.push('test files in the tarball');
const root = pkg.exports?.['.'] ?? {};
if (root.types !== './dist/index.d.ts' || root.svelte !== './dist/index.js') problems.push('exports["."] must point at dist/index');
if (!pkg.peerDependencies?.svelte) problems.push('svelte must be a peer dependency');
const index = readFileSync('dist/index.js', 'utf8');
for (const name of ['SddViewer', 'httpDataSource']) if (!new RegExp(`\\b${name}\\b`).test(index)) problems.push(`dist/index.js does not export ${name}`);
if (!/\bRepositoryDataSource\b/.test(readFileSync('dist/index.d.ts', 'utf8'))) problems.push('dist/index.d.ts does not export RepositoryDataSource');
if (problems.length) {
	console.error(problems.map((p) => `error: ${p}`).join('\n'));
	process.exit(1);
}
NODE
        npm pack --silent --pack-destination "$out"
        ;;
    *) echo "Unknown action: $action" >&2; exit 2 ;;
esac
