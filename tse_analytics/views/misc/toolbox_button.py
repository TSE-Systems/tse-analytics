import functools

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QToolButton, QWidget

from tse_analytics.core import manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.layouts.layout_manager import LayoutManager
from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset
from tse_analytics.toolbox.toolbox_registry import ToolboxPluginInfo, registry


class ToolboxButton(QToolButton):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setText("Toolbox")
        self.setIcon(QIcon(":/icons/icons8-toolbox-16.png"))
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setEnabled(False)

        self._toolbox_menu = QMenu("ToolboxMenu", self)

        # Keep track of menus and actions for enabling/disabling
        self._menus: dict[str, QMenu] = {}
        self._actions: dict[str, QAction] = {}

        self._populate_menu()
        self.setMenu(self._toolbox_menu)

    def _populate_menu(self) -> None:
        """Dynamically populate the menu from the registry."""
        plugins_by_category = registry.get_plugins()

        for category, plugins in plugins_by_category.items():
            # Create or get submenu for the category
            if category not in self._menus:
                self._menus[category] = self._toolbox_menu.addMenu(category)
            submenu = self._menus[category]

            for plugin in plugins:
                action = submenu.addAction(QIcon(plugin.icon), plugin.label)
                # Store action with a unique key (e.g., "Category.Label") for future reference if needed
                # For IntelliCage logic, we might need specific keys or just check category
                key = f"{category}.{plugin.label}"
                self._actions[key] = action

                # Connect action to the generic add_widget method
                # We use functools.partial to pass the plugin info
                action.triggered.connect(functools.partial(self._add_widget, plugin))

                # Special handling for IntelliCage actions to store them in attributes
                # for backward compatibility or easier access in set_enabled_actions
                if category == "IntelliCage":
                    if plugin.label == "Transitions":
                        self.intellicage_transitions_action = action
                    elif plugin.label == "Place Preference":
                        self.intellicage_place_preference_action = action

            # Store IntelliCage menu for set_enabled_actions
            if category == "IntelliCage":
                self.intellicage_menu = submenu

    def set_state(self, state: bool) -> None:
        """Enable or disable the toolbox button.

        Args:
            state: True to enable the button, False to disable it.
        """
        self.setEnabled(state)

    def set_enabled_actions(self, dataset: Dataset, datatable: Datatable | None) -> None:
        """Enable or disable specific actions based on the selected dataset and datatable.

        This method controls which analysis tools are available based on the type of dataset
        and datatable that are currently selected.

        Args:
            dataset: The currently selected dataset.
            datatable: The currently selected datatable, or None if no datatable is selected.
        """
        # Example logic for IntelliCage (needs to be adapted if registry keys change)
        if isinstance(dataset, IntelliCageDataset) or isinstance(dataset, IntelliMazeDataset):
            if hasattr(self, "intellicage_menu"):
                self.intellicage_menu.setEnabled(True)

            if hasattr(self, "intellicage_transitions_action"):
                self.intellicage_transitions_action.setEnabled(datatable is not None and datatable.name == "Visits")

            if hasattr(self, "intellicage_place_preference_action"):
                self.intellicage_place_preference_action.setEnabled(
                    datatable is not None and datatable.name == "Visits"
                )
        else:
            if hasattr(self, "intellicage_menu"):
                self.intellicage_menu.setEnabled(False)

    def _add_widget(self, plugin_info: ToolboxPluginInfo):
        """Generic method to add a widget to the central area.

        Args:
            plugin_info: The metadata for the widget to add.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return

        # If the widget class is in the registry, we use it.
        widget_class = plugin_info.widget_class
        try:
            widget = widget_class(datatable)
        except Exception as e:
            # Fallback or error logging if instantiation fails
            print(f"Failed to instantiate {plugin_info.label}: {e}")
            return

        # Determine title and icon
        # Use widget.title if available, otherwise plugin label
        title = getattr(widget, "title", plugin_info.label)
        final_title = f"{title} - {datatable.dataset.name}"

        LayoutManager.add_widget_to_central_area(datatable.dataset, widget, final_title, QIcon(plugin_info.icon))
