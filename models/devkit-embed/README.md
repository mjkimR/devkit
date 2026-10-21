# devkit-embed

The [potion-base-8M](https://huggingface.co/minishlab/potion-base-8M) static
embedding model (English, 256 dimensions), converted to float16 (15 MB), as a
data-only package for dense and hybrid search in
[`devkit_dist.features.search`](../../docs/development/reference/search.md). It registers the
`devkit.embedding_models` entry point `potion-base-8m` and is installed by the
`devkit-agt[search]` extra.

It sits outside the uv workspace and is built by hand only when the model
changes: devkit installs the committed wheel from `wheels/` via the local path
in `[tool.uv.sources]`. `model.json` pins the source
revision and the SHA-256 of every file. The raw weights and tokenizer source files are not
committed: `just model-build` downloads them from the pinned revision, verifies
them, writes the float16 conversion and builds the wheel into `dist/model/`; copying
it to `wheels/` updates the committed wheel. Licensing: `LICENSE` (MIT) and `NOTICE`.
