# Toolbox Widget Pattern

New analysis widgets inherit from `ToolboxWidgetBase` and register with the `@toolbox_plugin` decorator:

```python
@toolbox_plugin(category="Exploration", label="Histogram", icon="...", order=0)
class HistogramWidget(ToolboxWidgetBase):
    def __init__(self, datatable, parent=None):
        super().__init__(datatable, SettingsDataclass, title="...", parent=parent)

    def _create_toolbar_items(self, toolbar):  # add UI controls
    def _get_settings_value(self):             # return current settings
    def _update(self):                         # perform analysis + update display
```

See `tse_analytics/toolbox/histogram/` and `tse_analytics/toolbox/ancova/` for reference implementations.
