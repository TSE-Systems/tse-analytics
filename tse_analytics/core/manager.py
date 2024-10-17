import copy
import timeit
from pathlib import Path
from uuid import uuid4

from PySide6.QtWidgets import QWidget
from loguru import logger
from PySide6.QtCore import QModelIndex, QSettings, QThreadPool

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.core.data.data_hub import DataHub
from tse_analytics.core.dataset_merger import merge_datasets
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.models.workspace_model import WorkspaceModel
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.tse_import_settings import TseImportSettings
from tse_analytics.core.workers.worker import Worker
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.modules.phenomaster.io.csv_dataset_loader import load_csv_dataset
from tse_analytics.modules.phenomaster.io.tse_dataset_loader import load_tse_dataset


class Manager:
    messenger = Messenger()
    workspace_model = WorkspaceModel()
    data = DataHub(messenger)
    threadpool = QThreadPool()

    def __init__(self):
        logger.info(f"Multithreading with maximum {Manager.threadpool.maxThreadCount()} threads")

    @classmethod
    def load_workspace(cls, path: str) -> None:
        cls.workspace_model.load_workspace(path)
        cls.data.clear()

    @classmethod
    def save_workspace(cls, path: str) -> None:
        cls.workspace_model.save_workspace(path)

    @classmethod
    def import_csv_dataset(cls, path: Path) -> None:
        settings = QSettings()
        csv_import_settings: CsvImportSettings = settings.value("CsvImportSettings", CsvImportSettings.get_default())
        dataset = load_csv_dataset(path, csv_import_settings)
        if dataset is not None:
            cls.workspace_model.add_dataset(dataset)

    @classmethod
    def import_tse_dataset(cls, path: Path, import_settings: TseImportSettings, parent: QWidget) -> None:
        tic = timeit.default_timer()

        toast = make_toast(parent, "Importing Dataset", "Please wait...")
        toast.show()

        def _work_result(dataset: Dataset) -> None:
            if dataset is not None:
                cls.workspace_model.add_dataset(dataset)

        def _work_finished() -> None:
            toast.hide()
            logger.info(f"Dataset [{path}] import complete in {timeit.default_timer() - tic} sec.")

        worker = Worker(load_tse_dataset, path, import_settings)
        worker.signals.result.connect(_work_result)
        worker.signals.finished.connect(_work_finished)
        Manager.threadpool.start(worker)

    @classmethod
    def import_meal_details(cls, dataset_index: QModelIndex, path: str) -> None:
        cls.workspace_model.add_meal_details(dataset_index, path)

    @classmethod
    def import_actimot_details(cls, dataset_index: QModelIndex, path: str) -> None:
        cls.workspace_model.add_actimot_details(dataset_index, path)

    @classmethod
    def import_calo_details(cls, dataset_index: QModelIndex, path: str) -> None:
        cls.workspace_model.add_calo_details(dataset_index, path)

    @classmethod
    def remove_dataset(cls, indexes: list[QModelIndex]) -> None:
        cls.workspace_model.remove_dataset(indexes)
        cls.data.clear()

    @classmethod
    def merge_datasets(
        cls,
        new_dataset_name: str,
        datasets: list[Dataset],
        single_run: bool,
        continuous_mode: bool,
        generate_new_animal_names: bool,
    ) -> None:
        merged_dataset = merge_datasets(
            new_dataset_name, datasets, single_run, continuous_mode, generate_new_animal_names
        )
        if merged_dataset is not None:
            cls.workspace_model.add_dataset(merged_dataset)

    @classmethod
    def clone_dataset(cls, original_dataset: Dataset, new_dataset_name: str) -> None:
        new_dataset = copy.deepcopy(original_dataset)
        new_dataset.id = uuid4()
        new_dataset.name = new_dataset_name
        if new_dataset is not None:
            cls.workspace_model.add_dataset(new_dataset)
