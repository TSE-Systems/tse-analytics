"""Tests for the pipeline nodes' ``process()`` logic.

Nodes are ``NodeGraphQt`` widgets, so they need a ``QApplication`` (the ``qapp``
fixture) but — usefully — can be instantiated standalone without a NodeGraph.
Configuration is set via ``set_property`` and inputs are fed as ``PipelinePacket``.
"""

from unittest.mock import MagicMock, patch

import pytest
from tse_analytics.pipeline.pipeline_packet import PipelinePacket


@pytest.fixture
def datatable(make_dataset):
    return make_dataset().datatables["Main"]


# --- DescriptiveStatsNode ----------------------------------------------------


def test_descriptive_stats_produces_report(qapp, datatable):
    from tse_analytics.pipeline.nodes.descriptive_stats_node import DescriptiveStatsNode

    out = DescriptiveStatsNode().process(PipelinePacket(datatable))
    assert out.active
    assert out.value is datatable
    assert out.report is not None and "Descriptive Statistics" in out.report


def test_descriptive_stats_invalid_input_is_inactive(qapp):
    from tse_analytics.pipeline.nodes.descriptive_stats_node import DescriptiveStatsNode

    out = DescriptiveStatsNode().process(PipelinePacket(None))
    assert not out.active


# --- ResampleNode ------------------------------------------------------------


def test_resample_collapses_timepoints(qapp, datatable):
    from tse_analytics.pipeline.nodes.resample_node import ResampleNode

    node = ResampleNode()
    node.set_property("unit", "day")
    node.set_property("delta", 1)
    out = node.process(PipelinePacket(datatable))

    assert out.active
    assert "Weight" in out.value.df.columns
    assert len(out.value.df) < len(datatable.df)  # 2 timepoints/animal → 1 per day
    assert len(datatable.df) == 4  # original untouched (clone used)


def test_resample_invalid_input_is_inactive(qapp):
    from tse_analytics.pipeline.nodes.resample_node import ResampleNode

    out = ResampleNode().process(PipelinePacket("not a datatable"))
    assert not out.active


# --- TransformationNode ------------------------------------------------------


def test_transformation_adds_column_without_mutating_input(qapp, datatable):
    from tse_analytics.pipeline.nodes.transformation_node import TransformationNode

    node = TransformationNode()
    node.set_property("variable", "Weight")
    node.set_property("transformed_variable", "YJWeight")
    node.set_property("method", "Yeo-Johnson")
    out = node.process(PipelinePacket(datatable))

    assert out.active
    assert "YJWeight" in out.value.df.columns
    assert "YJWeight" not in datatable.df.columns  # original datatable untouched


@pytest.mark.parametrize("method", ["Log", "Log10"])
def test_transformation_log_methods_add_column(qapp, datatable, method):
    """Log/Log10 have no lambda; the tooltip must not crash on ``lambda_opt is None``."""
    from tse_analytics.pipeline.nodes.transformation_node import TransformationNode

    node = TransformationNode()
    node.set_property("variable", "Weight")
    node.set_property("transformed_variable", "LogWeight")
    node.set_property("method", method)
    out = node.process(PipelinePacket(datatable))

    assert out.active
    assert "LogWeight" in out.value.df.columns
    assert out.meta["lambda"] is None


def test_transformation_invalid_input_is_inactive(qapp):
    from tse_analytics.pipeline.nodes.transformation_node import TransformationNode

    out = TransformationNode().process(PipelinePacket(None))
    assert not out.active


# --- NormalityTestNode -------------------------------------------------------


def test_normality_routes_to_exactly_one_output(qapp, datatable):
    from tse_analytics.pipeline.nodes.normality_test_node import NormalityTestNode

    node = NormalityTestNode()
    node.set_property("variable", "Weight")
    node.set_property("method", "Shapiro-Wilk")
    out = node.process(PipelinePacket(datatable))

    assert set(out) == {"yes", "no"}
    assert out["yes"].active != out["no"].active  # exactly one branch is active


def test_normality_invalid_input_is_inactive_on_both(qapp):
    from tse_analytics.pipeline.nodes.normality_test_node import NormalityTestNode

    out = NormalityTestNode().process(PipelinePacket(None))
    assert not out["yes"].active
    assert not out["no"].active


# --- CheckboxNode ------------------------------------------------------------


@pytest.mark.parametrize(
    "state, active_key, inactive_key",
    [(True, "true", "false"), (False, "false", "true")],
)
def test_checkbox_routes_by_state(qapp, datatable, state, active_key, inactive_key):
    from tse_analytics.pipeline.nodes.checkbox_node import CheckboxNode

    node = CheckboxNode()
    node.set_property("state", state)
    out = node.process(PipelinePacket(datatable))

    assert out[active_key].active
    assert not out[inactive_key].active


def test_checkbox_invalid_input_is_inactive_on_both(qapp):
    from tse_analytics.pipeline.nodes.checkbox_node import CheckboxNode

    out = CheckboxNode().process(PipelinePacket(None))
    assert not out["true"].active
    assert not out["false"].active


# --- DatatableInputNode (manager-coupled) ------------------------------------


def test_datatable_input_returns_selected_datatable(qapp, make_dataset):
    from tse_analytics.pipeline.nodes import datatable_input_node as mod

    dataset = make_dataset()
    fake_manager = MagicMock()
    fake_manager.get_selected_dataset.return_value = dataset
    with patch.object(mod, "manager", fake_manager):
        node = mod.DatatableInputNode()
        node.set_property("datatable_name", "Main")
        out = node.process(PipelinePacket(None))

    assert out.active
    assert out.value is dataset.datatables["Main"]


def test_datatable_input_missing_name_is_inactive(qapp, make_dataset):
    from tse_analytics.pipeline.nodes import datatable_input_node as mod

    dataset = make_dataset()
    fake_manager = MagicMock()
    fake_manager.get_selected_dataset.return_value = dataset
    with patch.object(mod, "manager", fake_manager):
        node = mod.DatatableInputNode()
        node.set_property("datatable_name", "Nonexistent")
        out = node.process(PipelinePacket(None))

    assert not out.active


# --- DatatableOutputNode (manager-coupled) -----------------------------------


def test_datatable_output_renames_and_forwards_to_manager(qapp, datatable):
    from tse_analytics.pipeline.nodes import datatable_output_node as mod

    fake_manager = MagicMock()
    with patch.object(mod, "manager", fake_manager):
        node = mod.DatatableOutputNode()
        node.set_property("table_name", "Renamed")
        result = node.process(PipelinePacket(datatable))

    assert result is None  # terminal node
    fake_manager.add_datatable.assert_called_once()
    assert fake_manager.add_datatable.call_args.args[0].name == "Renamed"


def test_datatable_output_invalid_input_is_noop(qapp):
    from tse_analytics.pipeline.nodes import datatable_output_node as mod

    fake_manager = MagicMock()
    with patch.object(mod, "manager", fake_manager):
        mod.DatatableOutputNode().process(PipelinePacket(None))

    fake_manager.add_datatable.assert_not_called()
