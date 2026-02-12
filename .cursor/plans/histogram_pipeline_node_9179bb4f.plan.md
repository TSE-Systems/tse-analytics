---
name: Histogram Pipeline Node
overview: Create a new HistogramNode pipeline node that extracts histogram functionality from the histogram widget, allowing histograms to be generated within data analysis pipelines.
todos: []
---

# Histogram Pipeline Node Implementation

## Overview

Create a new `HistogramNode` class that converts the histogram widget functionality into a pipeline node, similar to how `ResampleNode` works. The node will generate histogram visualizations as HTML reports that can be used in pipelines.

## Implementation Details

### 1. Create HistogramNode Class

**File:** `tse_analytics/pipeline/nodes/histogram_node.py`

- Extend `PipelineNode` base class
- Set `__identifier__ = "stats"` (same category as DescriptiveStatsNode)
- Set `NODE_NAME = "Histogram"`
- Add input port: `"datatable"`
- Add output port: `"result"` (returns HTML string like DescriptiveStatsNode)

### 2. Node Properties

The node will have two properties initialized in `__init__`:

- **Variable selection**: Combo menu (empty initially, populated via `initialize` method)
- **Group by mode**: Combo menu (empty initially, populated via `initialize` method using `datatable.get_group_by_columns()`)

### 3. Initialize Method

Implement `initialize(self, dataset: Dataset)` method similar to `OneWayAnovaNode`:

- Get the selected datatable from manager
- Populate variable combo menu with variable names from datatable
- Populate group_by combo menu using `datatable.get_group_by_columns()`

### 4. Process Method

Implement `process(self, packet: PipelinePacket) -> PipelinePacket`:

- Extract datatable from packet and validate
- Get variable name and group_by string from properties
- Convert group_by string to `SplitMode` enum and factor_name:
- "Animal" → `SplitMode.ANIMAL`, factor_name = ""
- "Run" → `SplitMode.RUN`, factor_name = ""
- "Total" → `SplitMode.TOTAL`, factor_name = ""
- Factor name → `SplitMode.FACTOR`, factor_name = selected string
- Call `datatable.get_df([variable_name], split_mode, factor_name)` to get dataframe
- Call `get_histogram_result()` from `tse_analytics.toolbox.histogram.processor`:
- Pass: dataset, df, variable_name, split_mode, factor_name, figsize=None
- Return `PipelinePacket` containing the HTML report string from `result.report`

### 5. Register Node

**File:** `tse_analytics/pipeline/nodes/__init__.py`

- Import `HistogramNode`
- Add to `__all__` list

### 6. Register in Pipeline Editor

**File:** `tse_analytics/views/general/pipeline/pipeline_editor_widget.py`

- Import `HistogramNode` in the imports section
- Add `HistogramNode` to the `register_nodes()` call

## Key Dependencies

- `tse_analytics.toolbox.histogram.processor.get_histogram_result()` - core histogram generation
- `tse_analytics.core.data.datatable.Datatable.get_df()` - get dataframe with grouping
- `tse_analytics.core.data.shared.SplitMode` - enum for split modes
- `NodeGraphQt.widgets.node_widgets.NodeComboBox` - for dynamic combo menu updates

## Output Format

The node outputs an HTML string (similar to `DescriptiveStatsNode`) containing the histogram visualization, which can be:

- Passed to downstream nodes
- Used with `ReportNode` to save as a report
- Displayed in pipeline results