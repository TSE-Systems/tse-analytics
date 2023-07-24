import os

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import ShowHelpMessage


LAYOUT_VERSION = 5


def show_help(sender, path: str):
    if path is not None and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            content = file.read().rstrip()
            if content is not None:
                Manager.messenger.broadcast(ShowHelpMessage(sender, content))
