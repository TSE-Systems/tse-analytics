from loguru import logger
from PySide6.QtCore import QObject, QThreadPool, QThread

from tse_analytics.core.workers.worker import Worker


class TaskManager(QObject):
    threadpool: QThreadPool | None = None

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        TaskManager.threadpool = QThreadPool(self)
        logger.info(f"Multithreading with maximum {TaskManager.threadpool.maxThreadCount()} threads")

    @classmethod
    def start_task(cls, worker: Worker, priority: QThread.Priority = QThread.Priority.IdlePriority) -> None:
        cls.threadpool.start(worker, priority.value)
