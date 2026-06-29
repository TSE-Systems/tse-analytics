---
name: toolbox-widget-scaffold
description: Scaffold a new analysis toolbox widget end-to-end — a settings @dataclass, a ToolboxWidgetBase subclass decorated with @toolbox_plugin, the _create_toolbar_items / _get_settings_value / _update method contract, an optional processor.py, and (critically) the registration import in tse_analytics/toolbox/__init__.py — following the toolbox-widget-pattern build order, then verify. Use when asked to add a new toolbox widget / analysis tool / exploration panel to the app, or to scaffold a ToolboxWidgetBase subclass.
user-invocable: true
argument-hint: "[<widget-name>] [--module phenomaster|intellicage|intellimaze]"
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(task test), Bash(task ruff-check), Bash(task ruff-fix), Bash(task ruff-format), Bash(task pyrefly), Bash(task ty), Bash(task build-ui), Bash(uv run tse-analytics), Bash(git diff:*), Bash(git -C * diff:*), Bash(git status:*), Bash(git log:*)
---

# toolbox-widget-scaffold — add an analysis toolbox widget

Add a new analysis widget to the app as **one cohesive package** under `tse_analytics/toolbox/<name>/`
(or `tse_analytics/modules/<module>/toolbox/<name>/` for a module-specific widget). A widget is a
`ToolboxWidgetBase` subclass that owns its settings `@dataclass`, its toolbar selectors, and its
`_update()` analysis — and is **discovered only because its module is imported in
`tse_analytics/toolbox/__init__.py`**. This skill drives the build in the documented order and ends
on a verification gate.

> **IMPORTANT:** the authoritative pattern is **`.claude/rules/toolbox-widget-pattern.md`** and the
> deeper walkthrough is **`docs/dev/08-toolbox.md`** — read them; this skill orchestrates them, it is
> not a replacement. **Copy the closest existing widget wholesale** as your template rather than
> writing from scratch: `tse_analytics/toolbox/histogram/` (simple: variable + group-by selectors,
> `processor.py`) or `tse_analytics/toolbox/ancova/` (with a generated `.ui` settings dialog).
> **The single most common bug is forgetting the registration import** in
> `tse_analytics/toolbox/__init__.py` — the `@toolbox_plugin` decorator only runs when that module is
> imported, so without the import the widget silently never appears. **Delegate the matching pipeline
> node to the `/pipeline-node-scaffold` skill** — do not hand-write `<name>_node.py` here. Per
> CLAUDE.md "When in doubt, ask," surface a genuine doc/code conflict or an ill-fitting category and
> **ask** rather than guessing. Always re-read the code at run time — source wins, docs are derived.

## Scope

- **In scope:** a complete new widget package — the settings `@dataclass`, the `ToolboxWidgetBase`
  subclass decorated with `@toolbox_plugin(category=, label=, icon=, order=)`, the three subclass
  hooks (`_create_toolbar_items`, `_get_settings_value`, `_update`), an optional `processor.py`
  (pure analysis function returning a result with a `.report` HTML payload), an optional generated
  settings `.ui` dialog (and its `pyside6-uic` line in the matching `build-ui:*` task of
  `Taskfile.yml`), and **the registration import in `tse_analytics/toolbox/__init__.py`**.
- **Out of scope (delegate / don't touch):** the matching **pipeline node** — that is
  `/pipeline-node-scaffold`'s job. Editing generated `*_ui.py` / `*_rc.py` (regenerate via
  `task build-ui` / `task build-resources` instead). Inventing a new **category** — `CATEGORY_ORDER`
  in `tse_analytics/toolbox/toolbox_registry.py` is the fixed set: `AI`, `Data`, `Exploration`,
  `Bivariate`, `ANOVA`, `Factor Analysis`, `Chronobiology`, `Time Series`, `IntelliCage`.

## Procedure

When invoked (`/toolbox-widget-scaffold [<widget-name>] [--module …]`):

1. **Resolve inputs.** Take the widget name from `$ARGUMENTS` (snake_case package name, e.g.
   `effect_size`); if absent, ask. Pick its **category** from `CATEGORY_ORDER` and a `label`/`icon`
   (reuse an existing category icon such as `:/icons/exploration.png`). `--module <m>` ⇒ create the
   package under `tse_analytics/modules/<m>/toolbox/<name>/`; default ⇒ `tse_analytics/toolbox/<name>/`.
   If the package already exists, stop and ask — this skill is not idempotent. **Read
   `.claude/rules/toolbox-widget-pattern.md` and the chosen template before editing.**
2. **Copy the template.** Duplicate `toolbox/histogram/` (or `ancova/` if you need a `.ui` settings
   dialog) into the new package, then rename files/classes.
3. **Settings dataclass.** At the top of `<name>_widget.py`, define
   `@dataclass class <Name>WidgetSettings:` with the persisted fields (defaults required — it is
   constructed argument-free on first load).
4. **Widget class.** `@toolbox_plugin(category=…, label=…, icon=…, order=…)` on
   `class <Name>Widget(ToolboxWidgetBase)`. In `__init__`, call
   `super().__init__(datatable, <Name>WidgetSettings, title="…", parent=parent)` — pass the settings
   **type**, not an instance. The base already adds the "Update" action (wired to `_update`), the
   "Add Report" action, and `self.report_view` (a `ReportEdit`); read loaded settings from
   `self._settings`.
5. **Implement the three hooks.** `_create_toolbar_items(self, toolbar)` adds selectors (reuse
   `views/misc/variable_selector.py`, `views/misc/group_by_selector.py`); `_get_settings_value(self)`
   returns a fresh `<Name>WidgetSettings(...)` from the current widget state; `_update(self)` runs
   the analysis and calls `self.report_view.set_content(result.report)` (clear first if needed).
6. **Optional `processor.py`.** Put the pure compute in `get_<name>_result(datatable, …, figsize)`
   returning an object with a `.report` HTML string — keep numpy-nullable dtypes, no Qt in the
   processor.
7. **Optional `.ui` settings dialog.** If the widget needs a dialog, add `<name>_settings.ui`, add a
   `pyside6-uic` line to the matching `build-ui:*` task in `Taskfile.yml`, run `task build-ui`, and
   import the generated `*_ui.py` (never edit it).
8. **Register it.** Add `import tse_analytics.toolbox.<name>.<name>_widget  # noqa: F401` (or the
   `modules.<m>.toolbox.<name>.<name>_widget` path) to **`tse_analytics/toolbox/__init__.py`**,
   keeping the list alphabetically sorted. **This step is mandatory — without it the widget never
   registers.**
9. **Verify (the gate) + report.** `task ruff-format` → `task ruff-check` → `task pyrefly`
   (and/or `task ty`) → `task test`. Confirm the import is present in `toolbox/__init__.py` and the
   decorator's `category` is one of `CATEGORY_ORDER`. **Optional manual smoke:** `uv run tse-analytics`,
   open the Toolbox menu, confirm the widget appears under its category and `_update` renders.
   Persist the executed plan to `./.claude/plans/YYYY-MM-DD-<summary>.md` (CLAUDE.md rule — never
   `~/.claude/plans/`), then report files touched and any follow-ups.

## Notes

- **Registration ≠ definition.** A `@toolbox_plugin`-decorated class does nothing until its module is
  imported in `toolbox/__init__.py`; that file is the single discovery driver (`ToolboxButton` imports
  it at construction). Module-specific widgets under `modules/<m>/toolbox/` still register there.
- **Settings persist automatically** via `QSettings` keyed on the class name (saved on destroy); just
  return them from `_get_settings_value`. Every field needs a default.
- **Pass the settings *type*** to `super().__init__`, not an instance — the base constructs it.
- **numpy-nullable dtypes only** (`Int64`, `Float64`, `string`); keep Qt out of `processor.py`.
- **Don't invent categories** — use one of `CATEGORY_ORDER`; `order` controls position within it.
- **Always re-read the code at run time.** `docs/`/rules are a guide to verify, not ground truth;
  the source wins — note any drift and ask if it's load-bearing.
