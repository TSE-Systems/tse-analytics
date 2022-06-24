from tse_datatools.data.dataset_component import DatasetComponent

from tse_analytics.models.tree_item import TreeItem


class DatasetComponentTreeItem(TreeItem):
    def __init__(self, dataset_component: DatasetComponent):
        super().__init__(dataset_component.name, dataset_component.meta)

        self.dataset_component = dataset_component
