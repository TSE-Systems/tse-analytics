from tse_analytics.core.data.binning import BinningParams
from tse_analytics.core.data.shared import GroupingMode
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

    def __init__(self, sender, tag=None):
        """Create a new message

        :param sender: The object sending the message
        :param tag: An optional string describing the message
        """
        self.sender = sender
        self.tag = tag

    def __str__(self):
        return "{}: {}\n\t Sent from: {}".format(type(self).__name__, self.tag or "", self.sender)


class ErrorMessage(Message):
    """Used to send general purpose error messages"""

    pass


class SelectedTreeNodeChangedMessage(Message):
    """Indicates that the selected TreeView node has changed"""

    def __init__(self, sender, node: TreeItem, tag=None):
        super().__init__(sender, tag=tag)
        self.node = node


class DataChangedMessage(Message):
    """Indicates that selected data changed"""

    def __init__(self, sender, tag=None):
        super().__init__(sender, tag=tag)


class DatasetChangedMessage(Message):
    """Indicates that selected dataset is changed"""

    def __init__(self, sender, dataset: Dataset | None, tag=None):
        super().__init__(sender, tag=tag)
        self.data = dataset


class BinningMessage(Message):
    """Binning signalling"""

    def __init__(self, sender, params: BinningParams, tag=None):
        super().__init__(sender, tag=tag)
        self.params = params


class GroupingModeChangedMessage(Message):
    """Indicates that the grouping mode is changed"""

    def __init__(self, sender, mode: GroupingMode, tag=None):
        super().__init__(sender, tag=tag)
        self.mode = mode


class ShowHelpMessage(Message):
    """Request to display help content"""

    def __init__(self, sender, content: str, tag=None):
        super().__init__(sender, tag=tag)
        self.content = content
