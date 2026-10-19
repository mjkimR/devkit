"""devkit-viewer: a local, read-only page for the documents of several devkit repositories.

``devkit viewer serve`` (``devkit_viewer.cli``) registers repositories (``repositories``), reads their committed
content through Git at any local ref (``git``) and serves it with the committed app build (``server``,
``static/``). The page itself is built from ``frontend/``, whose Svelte library autohub vendors as a tarball.
Nothing here writes to a repository or takes part in an approval.
"""
