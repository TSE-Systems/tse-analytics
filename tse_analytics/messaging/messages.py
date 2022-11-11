from typing import Literal

from tse_datatools.data.animal import Animal
from tse_datatools.data.dataset import Dataset
from tse_datatools.data.group import Group

from tse_analytics.core.view_mode import ViewMode
from tse_analytics.models.tree_item import TreeItem


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
        return '%s: %s\n\t Sent from: %s' % (type(self).__name__,
                                             self.tag or '',
                                             self.sender)


class ErrorMessage(Message):
    """ Used to send general purpose error messages """
    pass


class SelectedTreeNodeChangedMessage(Message):
    """ Indicates that the selected TreeView node has changed """
    def __init__(self, sender, node: TreeItem, tag=None):
        super().__init__(sender, tag=tag)
        self.node = node


class AnimalDataChangedMessage(Message):
    """ Indicates that selected animal data changed """
    def __init__(self, sender, animals: list[Animal], tag=None):
        super().__init__(sender, tag=tag)
        self.animals = animals


class SelectedAnimalsChangedMessage(Message):
    """ Indicates that animal selection had changed """
    def __init__(self, sender, animals: list[Animal], tag=None):
        super().__init__(sender, tag=tag)
        self.animals = animals


class GroupDataChangedMessage(Message):
    """ Indicates that selected group data changed """
    def __init__(self, sender, groups: list[Group], tag=None):
        super().__init__(sender, tag=tag)
        self.groups = groups


class SelectedGroupsChangedMessage(Message):
    """ Indicates that selected groups are changed """
    def __init__(self, sender, groups: list[Group], tag=None):
        super().__init__(sender, tag=tag)
        self.groups = groups


class DatasetChangedMessage(Message):
    """ Indicates that selected dataset is changed """
    def __init__(self, sender, dataset: Dataset, tag=None):
        super().__init__(sender, tag=tag)
        self.data = dataset


class DatasetImportedMessage(Message):
    """ Indicates that the dataset has been imported """
    def __init__(self, sender, dataset: Dataset, tag=None):
        super().__init__(sender, tag=tag)
        self.dataset = dataset


class DatasetRemovedMessage(Message):
    """ Indicates that the dataset has been removed """
    pass


class WorkspaceLoadedMessage(Message):
    """ Indicates that the workspace has been loaded """
    pass


class ViewModeChangedMessage(Message):
    """ Indicates that current view mode is changed """
    def __init__(self, sender, mode: ViewMode, tag=None):
        super().__init__(sender, tag=tag)
        self.mode = mode


class BinningAppliedMessage(Message):
    """ Indicates that binning is applied """
    def __init__(
        self,
        sender,
        unit: Literal["day", "hour", "minute"],
        delta: int,
        mode: Literal["sum", "mean", "median"],
        tag=None
    ):
        super().__init__(sender, tag=tag)
        self.unit = unit
        self.delta = delta
        self.mode = mode
