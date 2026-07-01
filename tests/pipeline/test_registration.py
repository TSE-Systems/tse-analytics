"""Drift guard: every ``PipelineNode`` exported from ``pipeline/nodes`` must be
registered in the pipeline editor's ``register_nodes([...])`` call — otherwise a
newly-added node silently never appears in the editor palette.
"""

import re
from pathlib import Path

import tse_analytics.pipeline.nodes as nodes_pkg
from tse_analytics.pipeline.pipeline_node import PipelineNode

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EDITOR = _REPO_ROOT / "tse_analytics" / "views" / "pipeline" / "pipeline_editor_widget.py"


def _defined_node_classes() -> set[str]:
    return {
        name
        for name in dir(nodes_pkg)
        if isinstance(getattr(nodes_pkg, name), type)
        and issubclass(getattr(nodes_pkg, name), PipelineNode)
        and getattr(nodes_pkg, name) is not PipelineNode
    }


def test_all_core_pipeline_nodes_are_registered():
    source = _EDITOR.read_text(encoding="utf-8")
    match = re.search(r"register_nodes\(\[(.*?)\]\)", source, re.S)
    assert match, "register_nodes([...]) call not found in pipeline_editor_widget.py"
    registered_block = match.group(1)

    defined = _defined_node_classes()
    assert defined, "No PipelineNode subclasses exported from tse_analytics.pipeline.nodes"
    missing = {name for name in defined if name not in registered_block}
    assert not missing, f"Pipeline nodes defined but not registered: {sorted(missing)}"
