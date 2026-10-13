# devkit-embed

The [potion-base-8M](https://huggingface.co/minishlab/potion-base-8M) static
embedding model (English, 256 dimensions), converted to float16 (15 MB), as a
data-only package for dense and hybrid search in
[`devkit.search`](../../docs/search/reference.md). It registers the
`devkit.embedding_models` entry point `potion-base-8m` and is installed by the
`devkit[search]` extra.

`model.json` pins the source revision and the SHA-256 of every file. The weights
and tokenizer are not committed: `just model-fetch` downloads them from the
pinned revision, verifies them and writes the float16 conversion; building the
wheel fails without them. Licensing: `LICENSE` (MIT) and `NOTICE`.
