#!/usr/bin/env bash
# Frontend commands of the devkit-viewer package (packages/devkit-viewer/frontend); they need Node and npm:
#   viewer.sh install   npm ci
#   viewer.sh lint      prettier --check
#   viewer.sh check     svelte-check, warnings fail
#   viewer.sh test      vitest
#   viewer.sh probe DIR [ARGS...]
#                       vitest on the *.test.ts files under the absolute directory DIR outside src/ (a reviewer's
#                       throwaway probes), with the package's config and its dependencies resolved from the package;
#                       ARGS go to vitest
#   viewer.sh build     rebuild the committed page into src/devkit_viewer/static/ (artifact viewer-assets)
#   viewer.sh pack [DIR]
#                       package the library and write its npm pack tarball into DIR (default: frontend/dist-pack),
#                       after checking the tarball holds the library only and exports what autohub imports
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../packages/devkit-viewer/frontend"

action=${1:?Expected an action: install, lint, check, test, probe, build or pack}
if [[ $action != install && ! -d node_modules ]]; then
    echo "error: viewer frontend dependencies are not installed (no packages/devkit-viewer/frontend/node_modules); run \`just viewer install\` first" >&2
    exit 2
fi
case "$action" in
    install) npm ci --no-audit --no-fund ;;
    lint) npm run --silent lint ;;
    check) npm run --silent check ;;
    test) npm run --silent test ;;
    probe)
        dir=${2:?Expected the absolute directory of the probe tests}
        if [[ $dir != /* || ! -d $dir ]]; then
            echo "error: probe directory must be an existing absolute path: $dir" >&2
            exit 2
        fi
        dir=$(cd "$dir" && pwd -P)
        # vitest has no include flag, so a config beside the probes extends the package's: it collects DIR's tests and
        # resolves every dependency the package declares from the package, as a test under src/ would.
        config="$dir/.viewer-probe.vitest.config.mts"
        trap 'rm -f "$config"' EXIT
        cat >"$config" <<'CONFIG'
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
const root = process.env.VIEWER_PROBE_ROOT!;
const { default: base } = await import(join(root, 'vite.config.ts'));
const pkg = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
const dedupe = Object.keys({ ...pkg.dependencies, ...pkg.devDependencies, ...pkg.peerDependencies });
export default {
	...base,
	root,
	resolve: { ...base.resolve, dedupe },
	test: { ...base.test, dir: process.env.VIEWER_PROBE_DIR, include: ['**/*.test.ts'] }
};
CONFIG
        VIEWER_PROBE_ROOT=$PWD VIEWER_PROBE_DIR=$dir npx --no-install vitest run --config "$config" "${@:3}"
        ;;
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
