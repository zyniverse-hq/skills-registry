# 1. Adopt native Claude Code plugin primitives for dependencies, config, and bundling

- **Status:** Accepted
- **Date:** 2026-06-20
- **Deciders:** Registry maintainers
- **Tracking issue:** [#135](https://github.com/zyniverse-hq/skills-registry/issues/135)
- **Related issues:** #113, #131, #132, #133, #134, #136

## Context

The registry ships ~34 skills, several of which depend on other skills, on plugins from other
marketplaces, or on external configuration (GitHub Projects boards, API tokens, MCP servers).
Three problems surfaced:

1. **Dependencies are invisible.** `auto-ship` requires `ship-issue`; `ship-issue` and
   `handle-review` require the `superpowers` and `pr-review-toolkit` plugins (different
   marketplaces). Nothing declares this in a machine-readable way, so installing one skill alone
   silently fails or silently degrades. Only `ship-issue` checks at runtime.
2. **Configuration is undiscoverable at install time.** A user installing a board-driven skill
   gets no signal it needs setup. Required config lives only in prose inside `SKILL.md`, and skills
   use three different ad-hoc config mechanisms (`config.local.json`, manual placeholder
   replacement, undeclared env vars).
3. **No way to install a whole workflow.** The skills compose a real SDLC pipeline, but users must
   find and install each one individually.

The initial plan was to invent a parallel `requires:` block in our own SKILL.md frontmatter
(declaring `depends_on`, `external_plugins`, `config`, `secrets`) plus a bespoke
`config.local.json` standard, and to surface all of it through our own tooling and website.

Before building that, we verified what the Claude Code plugin system already provides
(verified 2026-06-20 against the live docs — see References). It turns out the platform natively
supports nearly everything we were about to reinvent.

## Decision

**Use native Claude Code plugin primitives wherever they exist; build our own mechanism only for
the genuine gaps. Author intent is declared once in our source of truth and the native fields are
*generated*, never hand-maintained.**

### What we use natively

| Need | Native mechanism |
|------|------------------|
| Skill → skill dependency | `dependencies` array in `plugin.json` — auto-installed, transitively enabled, semver-constrained |
| Cross-marketplace dependency | dependency object's `marketplace` key + the root marketplace's `allowCrossMarketplaceDependenciesOn` allowlist |
| Install-time config & secrets | `userConfig` schema (`sensitive: true` → system keychain) |
| Workflow bundle | multi-skill plugin + meta-plugin whose `dependencies` pull the set (analogous to a VS Code Extension Pack) |
| MCP servers + hooks | bundled in the plugin, auto-activated on enable |

### Verified spec (live docs, 2026-06-20)

- **`dependencies`** entries are a bare string or `{ "name", "version", "marketplace" }`.
  `version` accepts npm node-semver ranges (`~`, `^`, `>=`, `=`) and resolves against git tags named
  **`{plugin-name}--v{version}`** (created with `claude plugin tag --push`).
- A missing/unsatisfied dependency **disables** the dependent plugin with a named error
  (`dependency-unsatisfied`, `dependency-version-unsatisfied`, `range-conflict`, `no-matching-tag`),
  readable via `claude plugin list --json` → `errors`.
- **`allowCrossMarketplaceDependenciesOn`** is a top-level `marketplace.json` array. Only the *root*
  marketplace's allowlist is consulted — trust does not chain.
- **`userConfig`** prompts at enable time; `sensitive: true` masks input and stores it in the keychain
  (~2 KB limit). Values substitute as `${user_config.KEY}` / `CLAUDE_PLUGIN_OPTION_<KEY>`.
- **Minimum Claude Code versions:** dependency constraints **v2.1.110+**, transitive enable/disable
  v2.1.143+, `claude plugin prune` v2.1.121+, `defaultEnabled` v2.1.154+.

### What is NOT native — we still own these

1. **No "prerequisites / setup notes" manifest field.** Surface prerequisites via README +
   `userConfig` + a `SessionStart` hook. (#132)
2. **Cross-marketplace deps are not auto-fetched if the user hasn't added that marketplace.** The docs
   are explicit: *"Dependencies from a marketplace you have not added are left unresolved."* The
   allowlist only *permits* the dependency. Therefore the **runtime preflight** — `ship-issue`'s
   "stop with an actionable message when a required plugin is absent" — is retained as the peer-
   dependency safety net and standardized across dependent skills. (#134)

### Authoring model

Authors declare intent **once** in `SKILL.md` frontmatter (e.g. `depends_on`); `scripts/generate_index.py`
emits the native `plugin.json` `dependencies` and the `marketplace.json` entries. We never hand-edit the
generated manifests, consistent with the existing index/marketplace generation contract.

## Alternatives considered

- **Build a parallel `requires:` system in our frontmatter + our own resolver/UI.** Rejected: it
  would duplicate native auto-install, version resolution, keychain secret storage, and error
  reporting that Claude Code already does better, and it would not actually install anything for the
  user (no client-side resolver). Strictly worse and higher-maintenance.
- **Prose-docs-only (status quo).** Rejected: it is the current failure mode — requirements are
  invisible until something breaks.
- **One mega-plugin containing every skill.** Rejected: it forces all-or-nothing installs, breaks
  per-skill versioning, and conflicts with the registry's "small, sharp, non-overlapping" curation
  principle. Meta-plugins give the bundle benefit without collapsing the catalog.

## Consequences

**Positive**
- #132, #133, #134, and #113 get *simpler* — "generate the native field + document the pattern"
  instead of "build a parallel system."
- Users get real auto-install, semver safety, secure secret prompts, and one-install workflow bundles.
- Author burden drops to a single declaration per skill.

**Negative / costs**
- We inherit Claude Code version floors (constraints need v2.1.110+); document them and degrade
  gracefully on older clients.
- Versioned dependencies require maintaining `{plugin-name}--v{version}` git tags — new release
  discipline for the registry.
- The keychain ~2 KB secret limit constrains how much `userConfig` secret data a skill can store.
- Cross-marketplace UX still needs the preflight + README guidance because allowlisting alone does
  not subscribe the user to `superpowers`/`pr-review-toolkit`.

## Implementation pointers

- **#134** — generate `dependencies` + cross-marketplace `marketplace`/allowlist; standardize the preflight.
- **#133 / #132** — migrate config/secrets to `userConfig`; surface non-native prerequisites.
- **#136** — ship meta-plugin bundles (e.g. `engineering-workflow`).
- **#131** — the workflow map doc that the `engineering-workflow` bundle makes executable.

## References

- [Plugins reference](https://code.claude.com/docs/en/plugins-reference)
- [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- [Constrain plugin dependency versions](https://code.claude.com/docs/en/plugin-dependencies)
