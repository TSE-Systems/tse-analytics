---
name: pipeline-node-scaffold
description: Scaffold a new pipeline node (a PipelineNode subclass with process() and optional initialize()) and register it in the two coupled spots in views/pipeline/pipeline_editor_widget.py — the import block and the graph.register_nodes([...]) list — then verify. With an --audit mode that globs every *_node.py, diffs the defined nodes against the registered ones, and reports nodes that exist but were never registered. Use when asked to add a pipeline node, wire a node into the pipeline editor, or check for unregistered nodes.
user-invocable: true
argument-hint: "[--audit | <node-name>]"
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(task test), Bash(task ruff-check), Bash(task ruff-fix), Bash(task ruff-format), Bash(task pyrefly), Bash(task ty), Bash(uv run tse-analytics), Bash(git diff:*), Bash(git -C * diff:*), Bash(git status:*), Bash(git log:*)
---

# pipeline-node-scaffold — add a pipeline node (and audit registration)

Add a node to the visual data-processing pipeline (NodeGraphQt). A node is a `PipelineNode` subclass
that implements `process(packet) -> PipelinePacket | dict[str, PipelinePacket]` and is registered in
**`tse_analytics/views/pipeline/pipeline_editor_widget.py`** in **two coupled spots** — an import at
the top and an entry in the `self.graph.register_nodes([...])` list inside `_init_graph()`. Editing
only one of the two is the classic "node defined but never appears in the palette" bug; the `--audit`
mode exists to catch exactly that drift.

> **IMPORTANT:** the authoritative reference is **`docs/dev/09-pipeline.md`** plus the base classes
> **`tse_analytics/pipeline/pipeline_node.py`** (`PipelineNode(BaseNode)`) and
> **`tse_analytics/pipeline/pipeline_packet.py`** (`PipelinePacket`, `PipelinePacket.inactive(reason=…)`)
> — read them; this skill orchestrates them. **Copy the closest existing node wholesale** as your
> template: `tse_analytics/toolbox/histogram/histogram_node.py` (single input/output, a couple of
> NodeGraphQt widgets, an `initialize()` that fills combos from the datatable). Most toolbox widgets
> ship a sibling `<name>_node.py`; the **node and the widget are separate** — the widget is
> `/toolbox-widget-scaffold`'s job. Per CLAUDE.md "When in doubt, ask," surface a genuine conflict and
> **ask** rather than guessing. Always re-read the code at run time — source wins, docs are derived.

## Scope

- **In scope (scaffold):** `tse_analytics/toolbox/<name>/<name>_node.py` — a `PipelineNode` subclass
  with `__identifier__` (the palette group, e.g. `"stats"`), `NODE_NAME`, its `add_input`/`add_output`
  ports, its NodeGraphQt widgets (`add_text_input`, `add_combo_menu`, …), an optional
  `initialize(dataset, datatable)` to populate selectors, and `process(packet)`. **Then register in
  `tse_analytics/views/pipeline/pipeline_editor_widget.py`**: add
  `from tse_analytics.toolbox.<name>.<name>_node import <Name>Node` to the import block (top) **and**
  add `<Name>Node` to the `self.graph.register_nodes([...])` list in `_init_graph()`.
- **In scope (`--audit`):** glob `tse_analytics/**/*_node.py`, collect every `PipelineNode` subclass,
  diff against the import block + `register_nodes([...])` list in `pipeline_editor_widget.py`, and
  **report each node that is defined but unregistered** (at time of writing: `CorrelationMatrixNode`
  in `toolbox/correlation_matrix/` and `UmapNode` in `toolbox/umap/` — both have registered toolbox
  widgets but no registered node). Recommend the fix; **do not silently mass-edit** — confirm each is
  a genuine omission vs. intentional before registering.
- **Out of scope:** the toolbox widget itself (`/toolbox-widget-scaffold`); core/built-in nodes live
  in `tse_analytics.pipeline.nodes` (`DatatableInputNode`, `TransformationNode`, `ResampleNode`, …);
  NodeGraphQt library internals.

## Procedure

When invoked (`/pipeline-node-scaffold [--audit | <node-name>]`):

1. **Pick mode.**
   - **`--audit`:** run the audit (Scope §2). For each unregistered node, report
     `path → <Name>Node` and the missing import + `register_nodes` line; ask before applying fixes.
   - **Scaffold (default):** take the node name from `$ARGUMENTS` (snake_case, e.g. `effect_size` →
     `<name>_node.py`, class `EffectSizeNode`); if absent, ask. If `<name>_node.py` already exists,
     stop and ask. **Read `docs/dev/09-pipeline.md` and the histogram-node template before editing.**
2. **Write the node.** New file `tse_analytics/toolbox/<name>/<name>_node.py` copying the histogram
   template: set `__identifier__` + `NODE_NAME`, declare ports in `__init__`
   (`self.add_input("datatable")`, `self.add_output("result")`), add any widgets, and implement
   `process(self, packet) -> PipelinePacket`. Guard the input
   (`if not isinstance(packet.value, Datatable): return PipelinePacket.inactive(reason=…)`), reuse the
   widget's `processor.py` for the compute, and return `PipelinePacket(value, report=result.report)`.
   A **branching** node returns `dict[str, PipelinePacket]` keyed by output-port name.
3. **Optional `initialize`.** If the node has selectors to fill from the data, implement
   `initialize(self, dataset, datatable)` and populate the NodeGraphQt widgets (see the histogram
   template's `group_by` combo).
4. **Register in both spots.** In `tse_analytics/views/pipeline/pipeline_editor_widget.py`: add the
   `from tse_analytics.toolbox.<name>.<name>_node import <Name>Node` import (keep the block
   alphabetized) **and** add `<Name>Node` to the `self.graph.register_nodes([...])` list (also
   alphabetized). Missing either ⇒ the node won't load.
5. **Verify (the gate) + report.** `task ruff-check` → `task pyrefly` (and/or `task ty`) →
   `task test`. Confirm `<Name>Node` is in **both** the import block and `register_nodes([...])`.
   **Optional manual smoke:** `uv run tse-analytics` → open the pipeline editor → confirm the node is
   in the palette/tree under its `__identifier__` group and executes. Persist the executed plan to
   `./.claude/plans/YYYY-MM-DD-<summary>.md` (never `~/.claude/plans/`), then report files touched.

## Notes

- **Two-spot registration.** The import is what makes the symbol available; `register_nodes([...])`
  is what makes NodeGraphQt show it. Both are required — this is the drift `--audit` targets.
- **`process` return contract.** Return a `PipelinePacket` (single output) or
  `dict[str, PipelinePacket]` (branching, keyed by output port). On bad/empty input return
  `PipelinePacket.inactive(reason="…")` rather than raising.
- **Reuse the processor.** The node should call the same `get_<name>_result(...)` the widget uses —
  don't duplicate analysis logic between node and widget.
- **Keep lists alphabetized** in `pipeline_editor_widget.py` to match the existing style and minimize
  diff churn.
- **Always re-read the code at run time.** `docs/`/rules are a guide to verify, not ground truth; the
  source wins — note any drift and ask if it's load-bearing.
