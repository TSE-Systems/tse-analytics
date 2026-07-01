import functools

from loguru import logger
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QToolButton, QWidget

from tse_analytics.core import manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.layouts.layout_manager import LayoutManager
from tse_analytics.toolbox.toolbox_registry import ToolboxPluginInfo, registry, validate_registry


class ToolboxButton(QToolButton):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setText("Toolbox")
        self.setIcon(QIcon(":/icons/icons8-toolbox-16.png"))
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setEnabled(False)

        self._toolbox_menu = QMenu("ToolboxMenu", self)

        # Keep track of menus and actions for enabling/disabling.
        self._menus: dict[str, QMenu] = {}
        self._actions: dict[str, QAction] = {}
        # (action, plugin) pairs drive metadata-based visibility – no per-tool special-casing.
        self._action_plugins: list[tuple[QAction, ToolboxPluginInfo]] = []

        # Current selection / feature state used by ``_refresh_visibility``.
        self._internal_enabled: bool = False
        self._current_dataset: Dataset | None = None
        self._current_datatable: Datatable | None = None

        # Surface any registry inconsistencies without breaking the menu.
        for issue in validate_registry():
            logger.warning(f"Toolbox registry: {issue}")

        # Dynamically populate the menu from the registry.
        for category, plugins in registry.get_plugins().items():
            if category not in self._menus:
                self._menus[category] = self._toolbox_menu.addMenu(category)
            submenu = self._menus[category]

            for plugin in plugins:
                action = submenu.addAction(QIcon(plugin.icon), plugin.label)
                if plugin.tooltip:
                    action.setToolTip(plugin.tooltip)
                key = f"{category}.{plugin.label}"
                self._actions[key] = action
                self._action_plugins.append((action, plugin))
                action.triggered.connect(functools.partial(self._add_widget, plugin))

        # Apply the initial visibility (hides internal + dataset-specific tools).
        self._refresh_visibility()

        self.setMenu(self._toolbox_menu)

    def set_state(self, state: bool) -> None:
        """Enable or disable the toolbox button.

        Args:
            state: True to enable the button, False to disable it.
        """
        self.setEnabled(state)

    def enable_internal_tools(self, state: bool) -> None:
        """Enable or disable internal toolbox tools (e.g. the AI menu)."""
        self._internal_enabled = state
        self._refresh_visibility()

    def set_enabled_actions(self, dataset: Dataset, datatable: Datatable | None) -> None:
        """Update which actions are available for the selected dataset/datatable.

        Visibility is computed entirely from each plugin's declarative metadata
        (``dataset_types`` / ``required_datatable_name`` / ``internal``), so no
        tool needs to be special-cased here.

        Args:
            dataset: The currently selected dataset.
            datatable: The currently selected datatable, or None if no datatable is selected.
        """
        self._current_dataset = dataset
        self._current_datatable = datatable
        self._refresh_visibility()

    def _refresh_visibility(self) -> None:
        """Recompute action and category-submenu visibility from current state."""
        for action, plugin in self._action_plugins:
            if plugin.internal and not self._internal_enabled:
                visible = False
            elif self._current_dataset is not None:
                visible = plugin.is_applicable(self._current_dataset, self._current_datatable)
            else:
                # No dataset selected yet: dataset-restricted tools stay hidden;
                # unrestricted tools (incl. enabled internal ones) are shown.
                visible = plugin.dataset_types is None
            action.setVisible(visible)

        # A category submenu is visible iff it has at least one visible action.
        for menu in self._menus.values():
            menu.menuAction().setVisible(any(a.isVisible() for a in menu.actions()))

    def _add_widget(self, plugin_info: ToolboxPluginInfo):
        """Generic method to add a widget to the central area.

        Args:
            plugin_info: The metadata for the widget to add.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return

        widget_class = plugin_info.widget_class
        try:
            widget = widget_class(datatable)
        except Exception as e:
            logger.exception(f"Failed to instantiate {plugin_info.label}: {e}")
            return

        # Use widget.title if available, otherwise fall back to the plugin label.
        title = getattr(widget, "title", plugin_info.label)
        final_title = f"{title} - {datatable.name}"

        LayoutManager.add_widget_to_central_area(datatable.dataset, widget, final_title, QIcon(plugin_info.icon))
