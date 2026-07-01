"""Tests for :class:`ToolboxButton` — menu construction and the metadata-driven
visibility logic (``_refresh_visibility`` / ``set_enabled_actions`` /
``enable_internal_tools``) plus the ``_add_widget`` dispatch and its error path.

These drive the *real* ``ToolboxButton`` and the *real* ``ToolboxPluginInfo`` /
``registry`` (only ``registry.get_plugins`` is patched to inject controlled test
plugins), so the actual ``is_applicable`` gating is exercised rather than a
re-declared mock copy that could drift from the source.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
import tse_analytics.views.misc.toolbox_button as toolbox_button
from tse_analytics.toolbox.toolbox_registry import ToolboxPluginInfo, registry, validate_registry
from tse_analytics.views.misc.toolbox_button import ToolboxButton

# --- controlled test plugins (built with the REAL ToolboxPluginInfo) ---------
# One unrestricted tool, one IntelliCage Visits-gated tool, one internal tool —
# enough to cover every branch of ``_refresh_visibility``.
OPEN = ToolboxPluginInfo("Exploration", "Histogram", ":/icons/h.png", MagicMock())
VISITS = ToolboxPluginInfo(
    "IntelliCage",
    "Transitions",
    ":/icons/t.png",
    MagicMock(),
    dataset_types=("IntelliCage", "IntelliMaze"),
    required_datatable_name="Visits",
)
AI = ToolboxPluginInfo("AI", "AI Agent", ":/icons/ai.png", MagicMock(), internal=True)
PLUGINS = {"AI": [AI], "Exploration": [OPEN], "IntelliCage": [VISITS]}


def _ds(dataset_type: str):
    return SimpleNamespace(dataset_type=dataset_type)


def _dt(name: str):
    return SimpleNamespace(name=name)


def _make_button(qapp, plugins=None):
    """Build a ToolboxButton, keeping its Qt parent alive.

    The parent is stashed on the button so Python does not GC it — otherwise Qt
    deletes the whole child tree (menus/actions) out from under the test.
    ``plugins=None`` builds against the real, populated registry.
    """
    from PySide6.QtWidgets import QWidget

    parent = QWidget()
    if plugins is None:
        button = ToolboxButton(parent)
    else:
        with patch.object(registry, "get_plugins", return_value=plugins):
            button = ToolboxButton(parent)
    button._keepalive_parent = parent
    return button


@pytest.fixture
def button(qapp):
    """A ToolboxButton built from the controlled PLUGINS set."""
    return _make_button(qapp, PLUGINS)


# --- menu construction -------------------------------------------------------


def test_builds_menus_from_registry(button):
    assert set(button._menus) == {"AI", "Exploration", "IntelliCage"}
    assert [a.text() for a in button._menus["Exploration"].actions()] == ["Histogram"]
    assert set(button._actions) == {"AI.AI Agent", "Exploration.Histogram", "IntelliCage.Transitions"}


# --- visibility logic --------------------------------------------------------


def test_initial_visibility_hides_internal_and_dataset_restricted(button):
    """No dataset selected: unrestricted tools show, restricted + internal hide."""
    assert button._actions["Exploration.Histogram"].isVisible()
    assert not button._actions["IntelliCage.Transitions"].isVisible()
    assert not button._actions["AI.AI Agent"].isVisible()
    # A category submenu is visible iff it has a visible action.
    assert button._menus["Exploration"].menuAction().isVisible()
    assert not button._menus["IntelliCage"].menuAction().isVisible()
    assert not button._menus["AI"].menuAction().isVisible()


def test_set_enabled_actions_shows_matching_gated_tool(button):
    button.set_enabled_actions(_ds("IntelliCage"), _dt("Visits"))
    assert button._actions["IntelliCage.Transitions"].isVisible()
    assert button._actions["Exploration.Histogram"].isVisible()
    assert button._menus["IntelliCage"].menuAction().isVisible()


@pytest.mark.parametrize(
    "dataset_type, datatable_name",
    [
        ("PhenoMaster", "Visits"),  # wrong dataset type
        ("IntelliCage", "Nosepokes"),  # wrong datatable name
        ("IntelliCage", None),  # required datatable missing
    ],
)
def test_set_enabled_actions_hides_nonmatching_gated_tool(button, dataset_type, datatable_name):
    datatable = _dt(datatable_name) if datatable_name is not None else None
    button.set_enabled_actions(_ds(dataset_type), datatable)
    assert not button._actions["IntelliCage.Transitions"].isVisible()
    # An unrestricted tool is visible whenever any dataset is selected.
    assert button._actions["Exploration.Histogram"].isVisible()


def test_enable_internal_tools_toggles_internal_action(button):
    assert not button._actions["AI.AI Agent"].isVisible()
    button.enable_internal_tools(True)
    assert button._actions["AI.AI Agent"].isVisible()
    assert button._menus["AI"].menuAction().isVisible()
    button.enable_internal_tools(False)
    assert not button._actions["AI.AI Agent"].isVisible()
    assert not button._menus["AI"].menuAction().isVisible()


# --- _add_widget dispatch ----------------------------------------------------


def _build_button(qapp, plugin):
    return _make_button(qapp, {plugin.category: [plugin]})


def test_add_widget_instantiates_and_docks(qapp):
    widget_cls = MagicMock()
    widget_cls.return_value.title = "Histogram Chart"
    plugin = ToolboxPluginInfo("Exploration", "HistogramTool", ":/icons/h.png", widget_cls)
    datatable = SimpleNamespace(name="Main", dataset=object())
    button = _build_button(qapp, plugin)

    with (
        patch.object(toolbox_button.manager, "get_selected_datatable", return_value=datatable),
        patch.object(toolbox_button.LayoutManager, "add_widget_to_central_area") as add_mock,
    ):
        button._actions["Exploration.HistogramTool"].trigger()

    widget_cls.assert_called_once_with(datatable)
    add_mock.assert_called_once()
    dataset_arg, widget_arg, title_arg, _icon = add_mock.call_args.args
    assert dataset_arg is datatable.dataset
    assert widget_arg is widget_cls.return_value
    assert title_arg == "Histogram Chart - Main"  # widget.title wins


def test_add_widget_title_falls_back_to_label(qapp):
    widget_cls = MagicMock()
    widget_cls.return_value = object()  # no ``title`` attribute
    plugin = ToolboxPluginInfo("Exploration", "HistogramTool", ":/icons/h.png", widget_cls)
    datatable = SimpleNamespace(name="Main", dataset=object())
    button = _build_button(qapp, plugin)

    with (
        patch.object(toolbox_button.manager, "get_selected_datatable", return_value=datatable),
        patch.object(toolbox_button.LayoutManager, "add_widget_to_central_area") as add_mock,
    ):
        button._actions["Exploration.HistogramTool"].trigger()

    assert add_mock.call_args.args[2] == "HistogramTool - Main"  # plugin label fallback


def test_add_widget_noop_without_selected_datatable(qapp):
    widget_cls = MagicMock()
    plugin = ToolboxPluginInfo("Exploration", "HistogramTool", ":/icons/h.png", widget_cls)
    button = _build_button(qapp, plugin)

    with (
        patch.object(toolbox_button.manager, "get_selected_datatable", return_value=None),
        patch.object(toolbox_button.LayoutManager, "add_widget_to_central_area") as add_mock,
    ):
        button._actions["Exploration.HistogramTool"].trigger()

    widget_cls.assert_not_called()
    add_mock.assert_not_called()


def test_add_widget_swallows_instantiation_error(qapp):
    """A widget whose constructor raises must not crash the menu or dock anything."""
    widget_cls = MagicMock(side_effect=RuntimeError("boom"))
    plugin = ToolboxPluginInfo("Exploration", "BadWidget", ":/icons/b.png", widget_cls)
    datatable = SimpleNamespace(name="Main", dataset=object())
    button = _build_button(qapp, plugin)

    with (
        patch.object(toolbox_button.manager, "get_selected_datatable", return_value=datatable),
        patch.object(toolbox_button.LayoutManager, "add_widget_to_central_area") as add_mock,
    ):
        button._actions["Exploration.BadWidget"].trigger()  # must not raise

    add_mock.assert_not_called()


# --- misc presentation -------------------------------------------------------


def test_set_state_toggles_enabled(button):
    button.set_state(True)
    assert button.isEnabled()
    button.set_state(False)
    assert not button.isEnabled()


def test_action_tooltip_is_applied(qapp):
    plugin = ToolboxPluginInfo("Exploration", "Tip", ":/icons/h.png", MagicMock(), tooltip="Helpful hint")
    button = _build_button(qapp, plugin)
    assert button._actions["Exploration.Tip"].toolTip() == "Helpful hint"


# --- integration against the real, populated registry ------------------------


def test_real_registry_builds_valid_button(qapp):
    """Constructing against the real registry populates menus and reports no issues."""
    button = _make_button(qapp)
    assert validate_registry() == []
    assert len(button._action_plugins) == sum(len(v) for v in registry.get_plugins().values())
