from tse_analytics.models.tree_item import TreeItem
from tse_datatools.data.workspace import Workspace


class WorkspaceTreeItem(TreeItem):
    def __init__(self, workspace: Workspace):
        super().__init__(workspace.name)

        self.workspace = workspace
