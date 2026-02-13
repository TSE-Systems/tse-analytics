import sys
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication, QWidget


# Fixture to mock dependencies
@pytest.fixture(autouse=True)
def mock_dependencies():
    mocks = {
        "tse_analytics.core": MagicMock(),
        "tse_analytics.core.manager": MagicMock(),
        "tse_analytics.core.data.dataset": MagicMock(),
        "tse_analytics.core.data.datatable": MagicMock(),
        "tse_analytics.core.layouts.layout_manager": MagicMock(),
        "tse_analytics.modules.intellicage.data.intellicage_dataset": MagicMock(),
        "tse_analytics.modules.intellimaze.data.intellimaze_dataset": MagicMock(),
        "tse_analytics.toolbox.data_table.data_table_widget": MagicMock(),
        "tse_analytics.toolbox.fast_data_plot.fast_data_plot_widget": MagicMock(),
    }

    # We also need a mock for toolbox_registry but we want to control it
    # We'll let the user mock it separately or include it here

    with patch.dict("sys.modules", mocks):
        yield


@pytest.fixture
def mock_registry():
    # We mock the registry object inside the actual module
    # But since we are importing ToolboxButton inside the test, and it imports registry...
    # We can mock the module 'tse_analytics.toolbox.toolbox_registry' before import

    mock_reg_module = MagicMock()
    mock_registry_instance = MagicMock()
    # Setup ToolboxPluginInfo as a real dataclass or mock
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class ToolboxPluginInfo:
        category: str
        label: str
        icon: str
        widget_class: type = MagicMock()
        order: int = 0

    mock_reg_module.ToolboxPluginInfo = ToolboxPluginInfo
    mock_reg_module.registry = mock_registry_instance

    with patch.dict("sys.modules", {"tse_analytics.toolbox.toolbox_registry": mock_reg_module}):
        yield mock_registry_instance


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_toolbox_button_structure(qapp, mock_registry):
    """Test that ToolboxButton dynamically builds menus from registry."""
    from tse_analytics.toolbox.toolbox_registry import ToolboxPluginInfo

    # Setup mock registry data
    mock_plugin1 = ToolboxPluginInfo(category="TestCat1", label="Widget1", icon="icon1.png", widget_class=MagicMock())
    mock_plugin2 = ToolboxPluginInfo(category="TestCat1", label="Widget2", icon="icon2.png", widget_class=MagicMock())
    mock_plugin3 = ToolboxPluginInfo(category="TestCat2", label="Widget3", icon="icon3.png", widget_class=MagicMock())

    mock_registry.get_plugins.return_value = {"TestCat1": [mock_plugin1, mock_plugin2], "TestCat2": [mock_plugin3]}

    # Import ToolboxButton NOW, so it uses the mocked modules
    from PySide6.QtWidgets import QWidget
    from tse_analytics.views.misc.toolbox_button import ToolboxButton

    # Instantiate
    parent = QWidget()
    button = ToolboxButton(parent)

    # Verify menus
    assert "TestCat1" in button._menus
    assert "TestCat2" in button._menus

    menu1 = button._menus["TestCat1"]
    actions1 = menu1.actions()
    assert len(actions1) == 2
    assert actions1[0].text() == "Widget1"
    assert actions1[1].text() == "Widget2"

    menu2 = button._menus["TestCat2"]
    actions2 = menu2.actions()
    assert len(actions2) == 1
    assert actions2[0].text() == "Widget3"

    # Verify action keys
    assert "TestCat1.Widget1" in button._actions
    assert "TestCat2.Widget3" in button._actions


def test_add_widget_trigger(qapp, mock_registry, capsys):
    """Test that triggering an action calls _add_widget."""
    from tse_analytics.toolbox.toolbox_registry import ToolboxPluginInfo

    mock_widget_class = MagicMock()
    # Mock title for the widget instance
    mock_widget_instance = mock_widget_class.return_value
    mock_widget_instance.title = "Widget Title"

    mock_plugin = ToolboxPluginInfo(category="TestCat", label="Widget", icon="icon.png", widget_class=mock_widget_class)

    mock_registry.get_plugins.return_value = {"TestCat": [mock_plugin]}

    # Import
    from tse_analytics.views.misc import toolbox_button as toolbox_button_module
    from tse_analytics.views.misc.toolbox_button import ToolboxButton

    # Configure mock on the module directly to be sure
    mock_datatable = MagicMock()
    mock_datatable.dataset.name = "TestDataset"

    # toolbox_button.manager is the object we need to configure
    toolbox_button_module.manager.get_selected_datatable.return_value = mock_datatable

    parent = QWidget()
    button = ToolboxButton(parent)

    # Trigger action
    action = button._actions["TestCat.Widget"]
    action.trigger()

    # Check for exceptions/prints
    captured = capsys.readouterr()
    if captured.out:
        print(f"Stdout: {captured.out}")
    if captured.err:
        print(f"Stderr: {captured.err}")

    # Verify widget instantiation
    mock_widget_class.assert_called_once_with(mock_datatable)

    # Verify LayoutManager call
    toolbox_button_module.LayoutManager.add_widget_to_central_area.assert_called_once()
    args = toolbox_button_module.LayoutManager.add_widget_to_central_area.call_args
    # args: (dataset, widget, title, icon)
    assert args[0][1] == mock_widget_instance
    # Check title formation: "{widget.title} - {dataset.name}"
    assert args[0][2] == "Widget Title - TestDataset"
