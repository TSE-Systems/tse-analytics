from tse_analytics.core.data.binning import BinningSettings
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.data.workspace import Workspace
from tse_analytics.core.models.tree_item import TreeItem


class Message:
    """
    Base class for messages that the messenger handles.

    Each message represents a specific kind of event. After clients
    register to a messenger, they subscribe to specific message classes, and
    will only receive those kinds of messages.

    The message class family is hierarchical, and a client subscribing
    to a message class implicitly subscribes to all of its subclasses.

    :attr sender: The object which sent the message
    :attr tag: An optional string describing the message
    """

    def __init__(self, sender):
        """Create a new message

        :param sender: The object sending the message
        """
        self.sender = sender

    def __str__(self):
        return f"{type(self).__name__}\n\t Sent from: {self.sender}"


class SelectedTreeItemChangedMessage(Message):
    """Indicates that the selected TreeView item has changed"""

    def __init__(self, sender, tree_item: TreeItem):
        """Create a new SelectedTreeItemChangedMessage

        :param sender: The object sending the message
        :param tree_item: The newly selected tree item
        """
        super().__init__(sender)
        self.tree_item = tree_item


class DataChangedMessage(Message):
    """Indicates that selected data changed"""

    def __init__(self, sender, dataset: Dataset):
        """Create a new DataChangedMessage

        :param sender: The object sending the message
        :param dataset: The dataset that changed
        """
        super().__init__(sender)
        self.dataset = dataset


class WorkspaceChangedMessage(Message):
    """Indicates that the workspace has changed"""

    def __init__(self, sender, workspace: Workspace):
        """Create a new WorkspaceChangedMessage

        :param sender: The object sending the message
        :param workspace: The workspace that changed
        """
        super().__init__(sender)
        self.workspace = workspace


class DatasetChangedMessage(Message):
    """Indicates that the selected dataset is changed"""

    def __init__(self, sender, dataset: Dataset | None):
        """Create a new DatasetChangedMessage

        :param sender: The object sending the message
        :param dataset: The newly selected dataset, or None if no dataset is selected
        """
        super().__init__(sender)
        self.dataset = dataset


class DatatableChangedMessage(Message):
    """Indicates that the selected datatable is changed"""

    def __init__(self, sender, datatable: Datatable | None):
        """Create a new DatatableChangedMessage

        :param sender: The object sending the message
        :param datatable: The newly selected datatable, or None if no datatable is selected
        """
        super().__init__(sender)
        self.datatable = datatable


class ReportsChangedMessage(Message):
    def __init__(self, sender, report: Report | None):
        super().__init__(sender)
        self.report = report


class BinningMessage(Message):
    """Indicates that a binning operation should be performed on a dataset"""

    def __init__(self, sender, dataset: Dataset, settings: BinningSettings):
        """Create a new BinningMessage

        :param sender: The object sending the message
        :param dataset: The dataset to perform binning on
        :param settings: The binning settings to use
        """
        super().__init__(sender)
        self.dataset = dataset
        self.settings = settings


class AddToReportMessage(Message):
    """Indicates that a dataset should be added to the report"""

    def __init__(self, sender, dataset: Dataset):
        """Create a new AddToReportMessage

        :param sender: The object sending the message
        :param dataset: The dataset to add to the report
        """
        super().__init__(sender)
        self.dataset = dataset
