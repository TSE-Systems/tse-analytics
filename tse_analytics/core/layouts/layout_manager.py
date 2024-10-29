from typing import Any

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QWidget
from PySide6QtAds import CDockAreaWidget, CDockContainerWidget, CDockManager, CDockWidget, DockWidgetArea

LAYOUT_VERSION = 11

CDockManager.setConfigFlags(CDockManager.DefaultOpaqueConfig)
CDockManager.setConfigFlag(CDockManager.ActiveTabHasCloseButton, False)
CDockManager.setConfigFlag(CDockManager.DockAreaHasCloseButton, False)
CDockManager.setConfigFlag(CDockManager.DockAreaHasUndockButton, False)
CDockManager.setConfigFlag(CDockManager.DockAreaDynamicTabsMenuButtonVisibility, True)
CDockManager.setConfigFlag(CDockManager.FloatingContainerHasWidgetIcon, True)

# CDockManager.setAutoHideConfigFlags(CDockManager.DefaultAutoHideConfig)
# CDockManager.setAutoHideConfigFlag(CDockManager.AutoHideFeatureEnabled, True)
# CDockManager.setAutoHideConfigFlag(CDockManager.DockAreaHasAutoHideButton, False)
# CDockManager.setAutoHideConfigFlag(CDockManager.AutoHideHasCloseButton, False)


class LayoutManager:
    dock_manager: CDockManager | None = None
    menu: QMenu | None = None

    def __init__(self, parent: QWidget, menu: QMenu):
        LayoutManager.dock_manager = CDockManager(parent)
        LayoutManager.dock_manager.setStyleSheet("")
        LayoutManager.menu = menu

    @classmethod
    def register_dock_widget(
        cls,
        widget: QWidget,
        title: str,
        icon: QIcon,
    ) -> CDockWidget:
        dock_widget = CDockWidget(title)
        dock_widget.setWidget(widget)
        dock_widget.setIcon(icon)
        dock_widget.setMinimumSizeHintMode(CDockWidget.MinimumSizeHintFromContent)
        cls.menu.addAction(dock_widget.toggleViewAction())
        return dock_widget

    @classmethod
    def add_dock_widget(
        cls,
        dock_widget_area: DockWidgetArea,
        dock_widget: CDockWidget,
    ) -> DockWidgetArea:
        return cls.dock_manager.addDockWidget(
            dock_widget_area,
            dock_widget,
        )

    @classmethod
    def add_dock_widget_to_area(
        cls,
        dock_widget_area: DockWidgetArea,
        dock_widget: CDockWidget,
        dock_area_widget: CDockAreaWidget,
    ) -> DockWidgetArea:
        return cls.dock_manager.addDockWidget(
            dock_widget_area,
            dock_widget,
            dock_area_widget,
        )

    @classmethod
    def add_dock_widget_to_container(
        cls,
        dock_widget_area: DockWidgetArea,
        dock_widget: CDockWidget,
        dock_container_widget: CDockContainerWidget,
    ) -> DockWidgetArea:
        return cls.dock_manager.addDockWidgetToContainer(
            dock_widget_area,
            dock_widget,
            dock_container_widget,
        )

    @classmethod
    def add_dock_widget_tab(
        cls,
        dock_widget_area: DockWidgetArea,
        dock_widget: CDockWidget,
    ) -> DockWidgetArea:
        return cls.dock_manager.addDockWidgetTab(
            dock_widget_area,
            dock_widget,
        )

    @classmethod
    def add_dock_widget_tab_to_area(
        cls,
        dock_widget: CDockWidget,
        dock_area_widget: CDockAreaWidget,
    ) -> DockWidgetArea:
        return cls.dock_manager.addDockWidgetTabToArea(
            dock_widget,
            dock_area_widget,
        )

    @classmethod
    def add_dock_widget_floating(
        cls,
        dock_widget: CDockWidget,
    ) -> DockWidgetArea:
        return cls.dock_manager.addDockWidgetFloating(
            dock_widget,
        )

    @classmethod
    def save_state(cls) -> Any:
        return cls.dock_manager.saveState(LAYOUT_VERSION)

    @classmethod
    def restore_state(cls, state: Any) -> None:
        cls.dock_manager.restoreState(state, LAYOUT_VERSION)
