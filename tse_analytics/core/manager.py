from PySide6.QtCore import QThreadPool

from tse_analytics.data.data_hub import DataHub
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.workspace.workspace_manager import WorkspaceManager


class Manager:
    messenger = Messenger()
    workspace = WorkspaceManager(messenger)
    data = DataHub(messenger)
    threadpool = QThreadPool()

    def __init__(self):
        print("Multithreading with maximum %d threads" % Manager.threadpool.maxThreadCount())
