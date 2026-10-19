#!/usr/bin/env bash
# Build the release assets for a version tag:
#   release.sh vX.Y.Z
# Checks that the tag is vX.Y.Z and names the version of the three lockstep
# packages (devkit-dist, devkit-agt, devkit-advisory), builds a wheel of every
# workspace package into dist/release/, writes SHA256SUMS there and the release
# notes (install commands for this tag) to dist/release-notes.md. The
# devkit-embed model wheel is not rebuilt: the notes point at the release that
# ships it, pinned in the devkit-dist package's [tool.uv.sources].
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source ./scripts/_lib.sh

tag=${1:?Expected a version tag such as v0.1.0}
if [[ ! "$tag" =~ ^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]]; then
    echo "error: $tag is not a vX.Y.Z version tag" >&2
    exit 1
fi
version=${tag#v}
# devkit-dist, devkit-agt and devkit-advisory are released in lockstep from one tag, at one version.
for metadata in packages/devkit-dist/pyproject.toml packages/devkit/pyproject.toml packages/devkit-advisory/pyproject.toml; do
    package_version=$(project_version "$metadata")
    if [ "$package_version" != "$version" ]; then
        echo "error: $tag does not match the version $package_version in $metadata" >&2
        exit 1
    fi
done

out=dist/release
rm -rf "$out"
mkdir -p "$out"
modules=$(list_modules)
model_url=$(model_wheel_url)
for module in $modules; do
    uv build --package "$module" --wheel --out-dir "$out" >/dev/null
done
(cd "$out" && shasum -a 256 -- *.whl > SHA256SUMS)

repository=${GITHUB_REPOSITORY:-$(git remote get-url origin | sed -E 's#^(git@github\.com:|https://github\.com/)##; s#\.git$##')}
base="https://github.com/$repository/releases/download/$tag"
dist_wheel=$(basename "$out"/devkit_dist-*.whl)
devkit_wheel=$(basename "$out"/devkit_agt-*.whl)
advisory_wheel=$(basename "$out"/devkit_advisory-*.whl)
spec_wheel=$(basename "$out"/devkit_spec-*.whl)
viewer_wheel=$(basename "$out"/devkit_viewer-*.whl)
cat > dist/release-notes.md <<EOF
## Install

\`\`\`bash
# devkit with the harness: rules, commit gates, workflows, worktrees, devkit run
# (devkit-agt requires devkit-dist and devkit-advisory of the same version, named here as release wheels)
uv add --dev "devkit-agt @ $base/$devkit_wheel" "devkit-dist @ $base/$dist_wheel" "devkit-advisory @ $base/$advisory_wheel"

# Agent asset distribution only: sync, context, playbooks, native hooks (no harness commands or guidance)
uv add --dev "devkit-dist @ $base/$dist_wheel" "devkit-advisory @ $base/$advisory_wheel"

# devkit with dense and hybrid search (adds numpy, tokenizers and the 15 MB embedding model)
uv add --dev "devkit-agt[search] @ $base/$devkit_wheel" "devkit-dist[search] @ $base/$dist_wheel" "devkit-advisory @ $base/$advisory_wheel" "devkit-embed @ $model_url"

# Spec-Driven Development extension (includes the required devkit wheels)
uv add --dev "devkit-spec @ $base/$spec_wheel" "devkit-agt @ $base/$devkit_wheel" "devkit-dist @ $base/$dist_wheel" "devkit-advisory @ $base/$advisory_wheel"

# Local read-only viewer of devkit repositories: devkit viewer serve (includes the required devkit wheels)
uv add --dev "devkit-viewer @ $base/$viewer_wheel" "devkit-agt @ $base/$devkit_wheel" "devkit-dist @ $base/$dist_wheel" "devkit-advisory @ $base/$advisory_wheel"

# A tool installation: devkit-dist owns the devkit executable, devkit-agt adds the harness to it
uv tool install "devkit-dist @ $base/$dist_wheel" --with "devkit-agt @ $base/$devkit_wheel" --with "devkit-advisory @ $base/$advisory_wheel"

# devkit.advisory alone, as a runtime dependency of a library or service (standard library only)
uv add "devkit-advisory @ $base/$advisory_wheel"
\`\`\`

Checksums: \`SHA256SUMS\`.

## Upgrading from a devkit-agt release without devkit-dist

The CLI now ships as \`devkit-dist\` (distribution and the \`devkit\` executable) and \`devkit-agt\` (the harness), released
together. A release-wheel installation of \`devkit-agt\` names the \`devkit-dist\` wheel too. The first \`devkit sync\`
deploys the new auto-selected \`harness\` bundle (re-selected in projects that opted out with \`devkit = false\`; opt out
again with \`harness = false\`); a \`devkit:run\` selection stops the sync with \`SELECTION_INVALID\` until it becomes
\`harness:run\`, and \`devkit:all\` no longer deploys the \`devkit run\` guidance. Overrides of \`devkit:devkit-run\` and
\`devkit:run-pointer\` stop applying (re-create them under \`harness\`); overrides of \`devkit:consumption\` or the \`devkit\`
constitution keep the old harness text until reconciled. Details:
https://github.com/$repository/blob/$tag/guides/install/existing-repository.md#upgrading-across-the-package-split
EOF

echo "[RELEASE: $tag assets=$out]"
cat "$out/SHA256SUMS"
