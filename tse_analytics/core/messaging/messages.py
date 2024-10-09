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
        """
        self.sender = sender

    def __str__(self):
        return f"{type(self).__name__}\n\t Sent from: {self.sender}"


class SelectedTreeNodeChangedMessage(Message):
    """Indicates that the selected TreeView node has changed"""

    def __init__(self, sender, node: TreeItem):
        super().__init__(sender)
        self.node = node


class DataChangedMessage(Message):
    """Indicates that selected data changed"""

    def __init__(self, sender, dataset: Dataset):
        super().__init__(sender)
        self.dataset = dataset


class DatasetChangedMessage(Message):
    """Indicates that selected dataset is changed"""

    def __init__(self, sender, dataset: Dataset | None):
        super().__init__(sender)
        self.dataset = dataset


class BinningMessage(Message):
    """Binning signalling"""

    def __init__(self, sender, dataset: Dataset, settings: BinningSettings):
        super().__init__(sender)
        self.dataset = dataset
        self.settings = settings


class ShowHelpMessage(Message):
    """Request to display help content"""

    def __init__(self, sender, content: str):
        super().__init__(sender)
        self.content = content


class AddToReportMessage(Message):
    def __init__(self, sender, content, dataset: Dataset | None = None):
        super().__init__(sender)
        self.content = content
        self.dataset = dataset
