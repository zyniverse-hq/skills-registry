# Architecture Decision Records

This directory holds **ADRs** — short documents capturing a significant, hard-to-reverse decision
about the registry: the context, the decision, the alternatives weighed, and the consequences.

## Convention

- One file per decision, named `NNNN-kebab-case-title.md` (zero-padded, sequential).
- Status is one of `Proposed` · `Accepted` · `Superseded by NNNN` · `Deprecated`.
- ADRs are append-only history: don't rewrite an accepted ADR to reverse it — write a new one that
  supersedes it, and update the old one's status.
- Keep them concise. Link the tracking GitHub issue rather than duplicating discussion.

## Index

| # | Title | Status |
|---|-------|--------|
| [0001](0001-adopt-native-plugin-primitives-for-dependencies-config-and-bundling.md) | Adopt native Claude Code plugin primitives for dependencies, config, and bundling | Accepted |
