---
name: docs-sync
description: Realign the hand-maintained docs (.claude/CLAUDE.md and the 14 docs/dev/*.md) with backend code changes — diff the change, map it to the affected pages via a code→doc map, apply the prose edits, and re-verify the cited paths/symbols/cross-links; with an --audit fallback that walks every doc↔code binding when there's no diff. Edits prose only, never source. Use after a code change that touches messaging/services/workers/data-model/persistence/UI/toolbox/pipeline/modules/packaging, when asked to sync or audit the docs against the code, or when the docs have drifted.
user-invocable: true
argument-hint: "[--audit | <code-path…>]"
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(task test), Bash(git diff:*), Bash(git -C * diff:*), Bash(git log:*), Bash(git show:*), Bash(git rev-parse:*), Bash(git status:*)
---

# docs-sync — keep the hand-maintained docs aligned with the code

Keep the project's hand-maintained prose faithful to what the code actually does: the agent-facing
**`.claude/CLAUDE.md`** and the 14-file developer reference **`docs/dev/*.md`**. These are prose
*mirrors* of the source — when code changes and the
docs don't, they **silently drift**: a cited path/symbol rots, a described class/flag/constant stops
matching, a catalog (toolbox categories, pipeline nodes, Taskfile tasks) goes stale, or a renamed
heading breaks a cross-link. This skill detects what changed, maps it to the affected pages, applies
the matching prose edits, and re-verifies the references — the docs analogue of the sibling repos'
`pheno-docs-sync`.

> **IMPORTANT:** the **code is the source of truth**; `CLAUDE.md` and `docs/dev/*` are
> derived prose, **never the other way around** — if the code contradicts a doc, fix the doc and note
> the drift, never edit source to match a doc. Re-read the cited code at run time and re-derive any
> `path:line` ranges (they shift on any edit). This skill **edits prose only** — it does not modify
> code, tests, or generated files. Per CLAUDE.md "When in doubt, ask," surface a genuine doc/code
> conflict and **ask** rather than guessing. The code→doc binding map is in the **Procedure** below —
> walk it every run.

## Scope

- **In scope:** the hand-maintained prose — `.claude/CLAUDE.md` and the 14 `docs/dev/*.md`
  (`01-architecture` … `13-packaging-deployment`, `README.md`). Realign
  their cited paths/symbols, described types/flags/constants, the catalogs (toolbox categories &
  widgets, pipeline nodes, Taskfile tasks, messages, modules/extensions), and the relative
  `#anchor` cross-links — to match the current source.
- **Out of scope (don't touch / delegate):** **any code change** — this skill edits prose only and
  never modifies source, scenarios, or tests to make a doc true. Generated artifacts (`*_ui.py`,
  `*_rc.py`, compiled `*.qss`) — regenerate those via `task build-ui` / `task build-resources` /
  `task qss`, never hand-edit. Writing the *code* a doc describes (that's the relevant scaffold
  skill's job — this only realigns the docs to it).

## Procedure

When invoked (`/docs-sync [--audit | <code-path…>]`):

1. **Pick mode/scope.**
   - **Sync (default):** inspect `git diff` (working tree **and** staged: `git diff` +
     `git diff --cached`) and recent commits (`git log -p`) for code changes, and map each to the
     affected docs via the **code→doc map** (step 2). If `<code-path…>` args are given, scope to those.
     Identify the exact symbol / class / flag / constant / catalog-entry / path deltas.
   - **Audit** (`--audit`, **or** when the sync pass finds no relevant code diff): walk every binding
     in the map and verify each cited path/symbol, catalog entry, and cross-link still matches the
     source — to find pre-existing drift.
2. **Apply the doc edits** for each changed item per the **code→doc map**:
   - `core/messaging/*` → `docs/dev/02-messaging.md` + CLAUDE.md "Messaging backbone".
   - `core/manager.py`, `core/services/*` → `docs/dev/03-services-manager.md` + CLAUDE.md "Service facade".
   - `core/workers/*` → `docs/dev/04-threading-workers.md` + CLAUDE.md "Threading".
   - `core/data/*` (datatable, factor appliers, shared types) → `docs/dev/05-data-model.md` + CLAUDE.md "Domain Model".
   - `core/io/storage.py`, `core/services/workspace_service.py` → `docs/dev/06-persistence.md` + CLAUDE.md "Persistence".
   - `core/layouts/*`, `views/` UI/docking, SCSS/QSS → `docs/dev/07-layouts-ui.md`.
   - `toolbox/toolbox_registry.py`, `toolbox/toolbox_widget_base.py`, `toolbox/__init__.py`, any widget →
     `docs/dev/08-toolbox.md` + CLAUDE.md "Add a toolbox analysis widget".
   - `pipeline/*`, `views/pipeline/pipeline_editor_widget.py`, `*_node.py` → `docs/dev/09-pipeline.md` + CLAUDE.md "Add a pipeline node".
   - `modules/*` (phenomaster `EXTENSIONS_REGISTRY`, intellimaze `EXTENSION_NAME` wiring) →
     `docs/dev/10-modules-extensions.md` + CLAUDE.md "Add a module extension".
   - conventions (Python version, deps, lint) → `docs/dev/11-conventions.md` + CLAUDE.md "Code Style".
   - extending recipes → `docs/dev/12-extending.md`.
   - `Taskfile.yml`, packaging/PyInstaller/Flatpak → `docs/dev/13-packaging-deployment.md` + CLAUDE.md "Commands".
   Keep each page's section skeleton and heading style intact; re-derive any cited paths/symbols from
   the current source rather than trusting old text.
3. **New / removed / renamed extension point?** (a toolbox category, a registered node, a Taskfile
   task, a message type, a module extension) — update both the prose description **and** the matching
   catalog/list in `docs/dev/*` and CLAUDE.md so the inventory stays complete.
4. **CLAUDE.md.** Realign the terse agent-facing file only where the change touches a fact it
   states — keep edits surgical; CLAUDE.md is a companion, not a full copy of `docs/dev`.
5. **Verify (the gate) + report.** Re-grep each cited symbol/path to confirm it still exists and lands
   on the named thing; confirm every relative `#anchor` cross-link resolves (there is **no markdown
   linter** in the repo, so the gate is grep/read self-validation — be thorough); optionally
   `task test` if a change touched documented behavior. Report: code change → doc edits made → any
   residual drift you could **not** auto-resolve. On a genuine doc/code conflict, surface it and
   **ask** rather than guessing.

## Notes

- **Code wins, docs are derived.** Never edit source, a test, or a generated file to make a doc true —
  if they disagree, the code is right; fix the doc and note the drift.
- **CLAUDE.md notes its own intentional spellings/terminology** (e.g. `dafault_factor_builders.py` is
  an intentional in-repo filename; "Experiment" replaced "Run") — don't "fix" those as drift.
- **Cross-link anchors break on heading renames** — grep for the old `#anchor` across `docs/dev/*`
  after any rename.
- **Catalogs drift silently** — the toolbox category list, the registered-node list, and the Taskfile
  task table are the highest-value things to re-derive from source in `--audit` mode.
- **Always re-read the code at run time.** `docs/` and CLAUDE.md are a guide to verify, not ground
  truth; the source wins — note the drift and ask if it's load-bearing.
