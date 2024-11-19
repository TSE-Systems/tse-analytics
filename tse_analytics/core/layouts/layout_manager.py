import uuid
from typing import Any
from uuid import UUID

from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QLabel, QMenu, QWidget
from PySide6QtAds import CDockAreaWidget, CDockContainerWidget, CDockManager, CDockWidget, DockWidgetArea

from tse_analytics.modules.phenomaster.data.dataset import Dataset

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

DEFAULT_WIDGETS = {
    "CentralWidget",
    "Datasets",
    "Info",
    "Help",
    "Log",
    "Animals",
    "Factors",
    "Variables",
    "Binning",
}


class LayoutManager:
    dock_manager: CDockManager | None = None
    menu: QMenu | None = None

    _added_widgets: dict[str, CDockWidget] = {}
    _dataset_widgets: dict[UUID, list[CDockWidget]] = {}

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
        add_to_menu: bool = True,
    ) -> CDockWidget | None:
        # if title in cls._added_widgets:
        #     print("Already registered")
        #     return None
        dock_widget = CDockWidget(title)
        dock_widget.setWidget(widget)
        dock_widget.setIcon(icon)
        dock_widget.setMinimumSizeHintMode(CDockWidget.MinimumSizeHintFromContent)
        cls._added_widgets[title] = dock_widget
        if add_to_menu:
            cls.menu.addAction(dock_widget.toggleViewAction())
        return dock_widget

    @classmethod
    def set_central_widget(
        cls,
    ) -> DockWidgetArea:
        label = QLabel()
        label.setText("")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        central_dock_widget = CDockWidget("CentralWidget")
        central_dock_widget.setWidget(label)
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
            cls.dock_manager.removeDockWidget(dock_widget)

    @classmethod
    def clear_dock_manager(cls) -> None:
        map = cls.dock_manager.dockWidgetsMap()
        for title, dock_widget in map.items():
            if title not in DEFAULT_WIDGETS:
                cls.dock_manager.removeDockWidget(dock_widget)

    @classmethod
    def delete_dock_manager(cls) -> None:
        cls.dock_manager.deleteLater()
