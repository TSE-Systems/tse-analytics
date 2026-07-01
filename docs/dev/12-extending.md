# 12 — Extending the app (cookbook)

[← Back to index](README.md)

Recipes for the most common extension tasks. Each references the patterns documented elsewhere;
follow the links for the underlying detail.

---

## Add a toolbox analysis widget

**Goal:** a new analysis appears in the toolbox menu and runs against the selected datatable.

1. **Create the package** `toolbox/<tool>/` with:
   - `<tool>_widget.py` — the `ToolboxWidgetBase` subclass.
   - `processor.py` — the pure computation (DataFrame + settings → results/figure). Keep the math
     here so it's testable and reusable by a pipeline node.
2. **Subclass `ToolboxWidgetBase`** and register it with `@toolbox_plugin`:

   ```python
   @toolbox_plugin(category="Exploration", label="My Tool", icon=":/icons/exploration.png", order=99)
   class MyToolWidget(ToolboxWidgetBase):
       title = "My Tool"

       def __init__(self, datatable, parent=None):
           super().__init__(datatable, MyToolSettings, parent=parent)

       def _create_toolbar_items(self, toolbar): ...  # selectors, spinboxes
       def _get_settings_value(self):
           return MyToolSettings(...)

       def _update(self):
           self.report_view.setHtml(run(self.datatable.get_filtered_df([...]), self._settings))
   ```

   - `category` must be one of `CATEGORY_ORDER` (or it's appended alphabetically).
   - Use an icon from `:/icons/...`; add new icons via `resources/` + `task build-resources`.
   - Settings is a `@dataclass`; the base persists/loads it under the class name automatically.
   - To restrict the tool to specific datasets/tables, pass the optional keyword-only decorator args
     `dataset_types=(...)`, `required_datatable_name="..."`, or `internal=True`; `ToolboxButton`
     hides the action when they don't match the current selection.
3. **Register for discovery:** add an import line in `toolbox/__init__.py`
   (`import tse_analytics.toolbox.<tool>.<tool>_widget  # noqa: F401`). Without this the decorator
   never runs and the widget won't show — `tests/toolbox/test_toolbox_registry.py` fails if a
   decorated widget is missing from this manifest.
4. **(Optional) offload heavy work** to a [`Worker`](04-threading-workers.md) in `_update` and show
   a toast; update the report view in the `result` slot.
5. **Test** the `processor.py` under `tests/toolbox/<tool>/test_processor.py`.

Reference implementations: `toolbox/histogram/` (simple) and `toolbox/ancova/` (with a `.ui` settings
dialog). Full contract: [08-toolbox.md](08-toolbox.md).

---

## Add a matching pipeline node

**Goal:** the same analysis is usable inside the visual pipeline.

1. Create `toolbox/<tool>/<tool>_node.py` subclassing `PipelineNode`
   ([09-pipeline.md](09-pipeline.md)):

   ```python
   class MyToolNode(PipelineNode):
       NODE_NAME = "My Tool"

       def initialize(self, dataset, datatable):  # optional: bind context
           ...

       def process(self, packet):
           df = packet.value
           result = run(df, self._settings)  # reuse processor.py
           return PipelinePacket(value=result, report=html)
   ```

   Add input/output ports in `__init__` (NodeGraphQt API) and reuse the widget's `processor.py`.
2. **Register it in the editor:** import the node and add it to the `register_nodes([...])` list in
   `views/pipeline/pipeline_editor_widget.py`.

Return a single `PipelinePacket` for a normal node, or a `dict[port_name, PipelinePacket]` to route
to multiple output ports. Set `active=False` (or return `PipelinePacket.inactive(...)`) to stop a
downstream branch.

---

## Add a module extension

**Goal:** handle a new sub-device data stream from a data source.

**Import-only (IntelliMaze style):** create `modules/<module>/extensions/<ext>/{data,io}`, implement
the loader in `io/`, expose an `EXTENSION_NAME` constant, and wire it into the per-feature dicts in
`io/dataset_loader.py` and `views/export_merged_csv/export_merged_csv_dialog.py` (which import the
extension directly). Its table lands in `Dataset.raw_datatables`. (`extensions/__init__.py` is only
a convenience listing — it is not what activates the extension.)

**Full extension with a viewer (PhenoMaster style):**
1. Scaffold `modules/phenomaster/extensions/<ext>/` with `data/`, `io/data_loader.py`,
   `processor.py` (if needed), `<ext>_settings.py`, and `views/<ext>_widget.py` (+ `.ui`).
2. Add the raw-table-name constant in `io/tse_import_settings.py` and import the data in the loader.
3. **Register** the mapping in `modules/phenomaster/extensions/extensions_registry.py`:
   ```python
   EXTENSIONS_REGISTRY[MY_RAW_TABLE] = {"icon": QIcon(":/icons/..."), "widget": MyExtWidget}
   ```
4. If you added a `.ui`, wire it into `task build-ui` and run it.

Details and the registry diagram: [10-modules-extensions.md](10-modules-extensions.md).

---

## Add a message type

**Goal:** a new app-wide event for UI/services to react to.

1. Add a `Message` subclass in `core/messaging/messages.py` with its payload:
   ```python
   class MyThingChangedMessage(Message):
       def __init__(self, sender, thing):
           super().__init__(sender)
           self.thing = thing
   ```
2. Re-export it from `core/messaging/__init__.py`.
3. **Broadcast** where the state changes (ideally inside a service —
   [03-services-manager.md](03-services-manager.md)):
   `messaging.broadcast(messaging.MyThingChangedMessage(self, thing))`.
4. **Subscribe** in a `MessengerListener`:
   `messaging.subscribe(self, messaging.MyThingChangedMessage, self._on_thing_changed)`.

Remember the hierarchy: subscribing to a base class receives subclasses, and the most-specific
subscription wins. See [02-messaging.md](02-messaging.md).

---

## Run a long task without freezing the UI

```python
worker = Worker(expensive_fn, *args)  # core/workers/worker.py
worker.signals.result.connect(self._on_result)
worker.signals.error.connect(self._on_error)
worker.signals.finished.connect(self._on_finished)
TaskManager.start_task(worker)  # shared pool, initialized at bootstrap
```

Do the compute in `expensive_fn` (off-thread), return plain data, and touch widgets only in the
`result`/`finished` slots. Pass copied data in (`datatable.get_filtered_df(...)`). Full pattern and
gotchas: [04-threading-workers.md](04-threading-workers.md).

---

## Checklists

**New toolbox widget**
- [ ] `toolbox/<tool>/<tool>_widget.py` subclasses `ToolboxWidgetBase`, decorated with `@toolbox_plugin`
- [ ] `_create_toolbar_items`, `_get_settings_value`, `_update` implemented; `title` set
- [ ] settings is a `@dataclass`
- [ ] compute lives in `processor.py` (+ a test)
- [ ] import added to `toolbox/__init__.py`
- [ ] heavy work offloaded to a `Worker`
- [ ] (optional) matching `<tool>_node.py` registered in the pipeline editor

**Before committing**
- [ ] `task ruff-format` and `task ruff-check`
- [ ] `task build-ui` / `task build-resources` / `task qss` if you touched `.ui` / `.qrc` / `.scss`
- [ ] `task test`
- [ ] `pyproject.toml` + `uv.lock` committed together if deps changed
- [ ] plan saved to `./.claude/plans/` (see [11-conventions.md](11-conventions.md))

---

**Next:** [13 — Packaging & deployment →](13-packaging-deployment.md)
