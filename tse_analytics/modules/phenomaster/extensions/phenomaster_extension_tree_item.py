import weakref

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.modules.phenomaster.data.phenomaster_extension_data import PhenoMasterExtensionData


class PhenoMasterExtensionTreeItem(TreeItem):
    def __init__(
        self,
        extension_data: PhenoMasterExtensionData,
        icon: QIcon,
        extension_widget_type: type | None = None,
    ):
        super().__init__(extension_data.name)

        self._extension_data = weakref.ref(extension_data)
        self._icon = icon
        self._extension_widget_type = extension_widget_type

    @property
    def extension_data(self):
        return self._extension_data()

    @property
    def dataset(self):
        return self.extension_data.dataset

    @property
    def icon(self):
        return self._icon

    @property
    def foreground(self):
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        return self.extension_data.name

    @property
    def extension_widget_type(self) -> type | None:
        return self._extension_widget_type
