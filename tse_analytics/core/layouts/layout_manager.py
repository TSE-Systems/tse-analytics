import uuid
from typing import Any
from uuid import UUID

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QWidget
from PySide6QtAds import CDockAreaWidget, CDockContainerWidget, CDockManager, CDockWidget, DockWidgetArea

from tse_analytics.core.data.dataset import Dataset

LAYOUT_VERSION = 13

CDockManager.setConfigFlags(CDockManager.DefaultOpaqueConfig)
CDockManager.setConfigFlag(CDockManager.ActiveTabHasCloseButton, True)
CDockManager.setConfigFlag(CDockManager.DockAreaHasCloseButton, False)
CDockManager.setConfigFlag(CDockManager.DockAreaHasUndockButton, False)
CDockManager.setConfigFlag(CDockManager.DockAreaDynamicTabsMenuButtonVisibility, True)
CDockManager.setConfigFlag(CDockManager.FloatingContainerHasWidgetIcon, True)

# CDockManager.setAutoHideConfigFlags(CDockManager.DefaultAutoHideConfig)
# CDockManager.setAutoHideConfigFlag(CDockManager.AutoHideFeatureEnabled, True)
# CDockManager.setAutoHideConfigFlag(CDockManager.DockAreaHasAutoHideButton, False)
# CDockManager.setAutoHideConfigFlag(CDockManager.AutoHideHasCloseButton, False)

DEFAULT_WIDGETS = {
    "CentralWidget",
    "Datasets",
    "Info",
    "Log",
    "Animals",
    "Factors",
    "Variables",
    "Binning",
}


class LayoutManager:
    dock_manager: CDockManager | None = None
    menu: QMenu | None = None

    _dataset_widgets: dict[UUID, list[CDockWidget]] = {}

    def __init__(self, parent: QWidget, menu: QMenu):
        LayoutManager.dock_manager = CDockManager(parent)
        LayoutManager.dock_manager.setStyleSheet("")
        LayoutManager.menu = menu
        # LayoutManager.dock_manager.dockWidgetAboutToBeRemoved.connect(LayoutManager._dockWidgetAboutToBeRemoved)
        # LayoutManager.dock_manager.dockWidgetRemoved.connect(LayoutManager._dockWidgetRemoved)

    # @classmethod
    # def _dockWidgetAboutToBeRemoved(
    #     cls,
    #     dock_widget: CDockWidget,
    # ) -> None:
    #     widget = dock_widget.widget()
    #     if isinstance(widget, messaging.MessengerListener):
    #         messaging.unsubscribe_all(widget)

    # @classmethod
    # def _dockWidgetRemoved(
    #     cls,
    #     dock_widget: CDockWidget,
    # ) -> None:
    #     print(f"Dock widget removed: {dock_widget.objectName()}")

    @classmethod
    def register_dock_widget(
        cls,
        widget: QWidget,
        title: str,
        icon: QIcon,
        add_to_menu: bool = True,
    ) -> CDockWidget:
        dock_widget = CDockWidget(title)
        dock_widget.setFeature(CDockWidget.DockWidgetClosable, False)
        dock_widget.setWidget(widget)
        dock_widget.setIcon(icon)
        dock_widget.setMinimumSizeHintMode(CDockWidget.MinimumSizeHintFromContent)
        if add_to_menu:
            cls.menu.addAction(dock_widget.toggleViewAction())
        return dock_widget

    @classmethod
    def set_central_widget(
        cls,
    ) -> DockWidgetArea:
        central_dock_widget = CDockWidget("CentralWidget")
        central_dock_widget.setWidget(QWidget())
        central_dock_widget.setFeature(CDockWidget.NoTab, True)
        return cls.dock_manager.setCentralWidget(
            central_dock_widget,
        )

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
    def add_widget_to_central_area(
        cls,
        dataset: Dataset | None,
        widget: QWidget,
        title: str,
        icon: QIcon,
    ) -> CDockWidget:
        dock_widget = cls.register_dock_widget(widget, title, icon, False)
        if dock_widget is None:
            return None

        object_name = f"{title} - {str(uuid.uuid4())}"
        dock_widget.setObjectName(object_name)
        dock_widget.setFeature(CDockWidget.DockWidgetDeleteOnClose, True)
        dock_widget.setFeature(CDockWidget.DockWidgetClosable, True)

        central_dock_area = cls.get_central_area_widget()
        cls.add_dock_widget_tab_to_area(dock_widget, central_dock_area)

        if dataset is not None:
            if dataset.id not in cls._dataset_widgets:
                cls._dataset_widgets[dataset.id] = []
            cls._dataset_widgets[dataset.id].append(dock_widget)

        return dock_widget

    @classmethod
    def save_state(cls) -> Any:
        return cls.dock_manager.saveState(LAYOUT_VERSION)

    @classmethod
    def restore_state(cls, state: Any) -> None:
        cls.dock_manager.restoreState(state, LAYOUT_VERSION)

    @classmethod
    def add_perspective(cls, name: str) -> None:
        cls.dock_manager.addPerspective(name)

    @classmethod
    def open_perspective(cls, name: str) -> None:
        cls.dock_manager.openPerspective(name)

    @classmethod
    def get_central_area_widget(cls) -> CDockAreaWidget:
        dock_widget = cls.dock_manager.findDockWidget("CentralWidget")
        return dock_widget.dockAreaWidget()

    @classmethod
    def delete_dataset_widgets(cls, dataset: Dataset) -> None:
        if dataset.id not in cls._dataset_widgets:
            return
        for dock_widget in cls._dataset_widgets[dataset.id]:
            try:
                # cls.dock_manager.removeDockWidget(dock_widget)
                dock_widget.closeDockWidget()
            except RuntimeError:
                # Widget is already closed
                pass
        cls._dataset_widgets.pop(dataset.id)

    @classmethod
    def clear_dock_manager(cls) -> None:
        cls._dataset_widgets.clear()
        map = cls.dock_manager.dockWidgetsMap()
        for title, dock_widget in map.items():
            if title not in DEFAULT_WIDGETS:
                dock_widget.closeDockWidget()

    @classmethod
    def delete_dock_manager(cls) -> None:
        cls.dock_manager.deleteLater()
