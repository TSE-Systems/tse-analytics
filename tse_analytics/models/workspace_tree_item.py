from tse_analytics.data.workspace import Workspace

from tse_analytics.models.tree_item import TreeItem


class WorkspaceTreeItem(TreeItem):
    def __init__(self, workspace: Workspace):
        super().__init__(workspace.name)

        self.workspace = workspace
