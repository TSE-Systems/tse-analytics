import pandas as pd

from tse_analytics.core.data.binning import BinningSettings
from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.modules.phenomaster.data.dataset import Dataset


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
        :param tag: An optional string describing the message
        """
        self.sender = sender

    def __str__(self):
        return "{}\n\t Sent from: {}".format(type(self).__name__, self.sender)


class ErrorMessage(Message):
    """Used to send general purpose error messages"""

    pass


class SelectedTreeNodeChangedMessage(Message):
    """Indicates that the selected TreeView node has changed"""

    def __init__(self, sender, node: TreeItem):
        super().__init__(sender)
        self.node = node


class DataChangedMessage(Message):
    """Indicates that selected data changed"""

    def __init__(self, sender):
        super().__init__(sender)


class DataTableUpdateMessage(Message):
    """Indicates that data table should be updated"""

    def __init__(self, sender, dataset: Dataset, df: pd.DataFrame):
        super().__init__(sender)
        self.dataset = dataset
        self.df = df


class DataPlotUpdateMessage(Message):
    """Indicates that data plot should be updated"""

    def __init__(self, sender, dataset: Dataset, df: pd.DataFrame):
        super().__init__(sender)
        self.dataset = dataset
        self.df = df


class DatasetChangedMessage(Message):
    """Indicates that selected dataset is changed"""

    def __init__(self, sender, dataset: Dataset | None):
        super().__init__(sender)
        self.data = dataset


class BinningMessage(Message):
    """Binning signalling"""

    def __init__(self, sender, settings: BinningSettings):
        super().__init__(sender)
        self.settings = settings


class ShowHelpMessage(Message):
    """Request to display help content"""

    def __init__(self, sender, content: str):
        super().__init__(sender)
        self.content = content


class AddToReportMessage(Message):
    def __init__(self, sender, content):
        super().__init__(sender)
        self.content = content
