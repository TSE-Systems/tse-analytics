from PySide6.QtGui import QIcon
from tse_datatools.data.actimot_data import ActimotData

from tse_analytics.models.dataset_component_tree_item import DatasetComponentTreeItem


class ActiMotTreeItem(DatasetComponentTreeItem):
    def __init__(self, dataset_component: ActimotData):
        super().__init__(dataset_component)

    @property
    def icon(self):
        return QIcon(":/icons/icons8-data-sheet-16.png")

    @property
    def tooltip(self):
        return "ActiMot data"
