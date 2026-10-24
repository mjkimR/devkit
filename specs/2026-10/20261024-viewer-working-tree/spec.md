---
id: SPEC-viewer-working-tree
title: Show the working tree for the current branch
summary: "The local repository viewer reads saved files from each registered checkout, including uncommitted edits, and identifies the checked-out branch without offering branch selection."
status: completed
created: 2026-10-24
related_capabilities:
  - CAP-VIEW-repository-viewer
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-viewer-working-tree] Show the working tree for the current branch

## 1. Problem Statement & Motivation

The viewer currently reads committed Git objects and offers a branch picker. A developer must commit an edit before the viewer can show it, and the picker makes a local reading tool act like a branch browser. The viewer will instead read the registered repository's current working directory and display its checked-out branch as context.

## 2. User Stories

- **US-1**: As a developer or agent, I want the viewer to show saved repository files from the current checkout so that I can inspect changes before committing them.
- **US-2**: As a developer or agent, I want the viewer to identify the checkout's current branch without a branch selector so that I know which working directory I am viewing.

## 3. Non-Goals

1. **Scope Excluded**: Selecting or reading another branch, exposing unsaved editor buffers, watching files and refreshing automatically, or changing the exact-generation proposal-review route.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The API reads saved working-tree content
- **Given** a registered repository whose tracked file has a saved but uncommitted edit
- **When** the viewer reads that file through the blob endpoint
- **Then** the response contains the saved working-tree bytes and does not require a `ref` query parameter

### [AC-02] The API lists current working-tree entries
- **Given** a registered repository with an untracked file and a nested directory
- **When** the viewer lists the relevant directories through the tree endpoint
- **Then** the entries include the untracked file and nested directory with the existing `{items: [{name, path, type, size?}]}` payload shape

### [AC-03] Repository paths cannot expose Git metadata or escape through traversal and symlinks
- **Given** a request path with an absolute path, a `.git` segment, a `..` segment, or a path resolving outside the registered root
- **When** the viewer reads a tree or blob
- **Then** it returns `400 VIEWER_PATH_INVALID` for syntactically invalid paths or `404 VIEWER_PATH_NOT_FOUND` for absent or out-of-root paths, without returning outside content

### [AC-04] The viewer reports but does not select the current branch
- **Given** a registered repository checked out on a local branch or with detached `HEAD`
- **When** the app loads the repository
- **Then** it displays the current branch name (or `HEAD`) and provides no branch-selection control

### [AC-05] All document views use only the current working tree
- **Given** roadmap, dashboard, document index, and file explorer views
- **When** each view loads repository content
- **Then** each reads the registered current working directory and does not enumerate or read other local branches

### [AC-06] Existing loopback and read-only server boundaries remain
- **Given** the viewer serves working-tree content
- **When** a request has a foreign `Host` header or uses a non-GET method
- **Then** the server preserves `403 VIEWER_HOST_REFUSED` and `405 VIEWER_METHOD_NOT_ALLOWED`, and writes no repository files
