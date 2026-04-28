"""
Core manager module for TSE Analytics.

This module provides a façade Manager class that delegates to focused service
classes for managing workspaces, datasets, datatables, and data imports.
Module-level function aliases are exported for backward compatibility.
"""

from tse_analytics.core.services.dataset_service import DatasetService
from tse_analytics.core.services.import_service import ImportService
from tse_analytics.core.services.selection_service import SelectionService
from tse_analytics.core.services.workspace_service import WorkspaceService


class Manager:
    """Façade class delegating to focused service classes.

    This class wires together the four service classes and exposes
    their methods for backward compatibility. All 34+ consumer files
    continue to work via the module-level function aliases below.
    """

    def __init__(self):
        """Initialize the Manager and its service dependencies."""
        self.selection_service = SelectionService()
        self.workspace_service = WorkspaceService(self.selection_service)
        self.dataset_service = DatasetService(self.workspace_service, self.selection_service)
        self.importer_service = ImportService(self.selection_service, self.dataset_service, self.workspace_service)

    # --- Selection delegates ---
    def get_selected_dataset(self):
        return self.selection_service.get_selected_dataset()

    def set_selected_dataset(self, dataset):
        return self.selection_service.set_selected_dataset(dataset)

    def get_selected_datatable(self):
        return self.selection_service.get_selected_datatable()

    def set_selected_datatable(self, datatable):
        return self.selection_service.set_selected_datatable(datatable)

    # --- Workspace delegates ---
    def get_workspace(self):
        return self.workspace_service.get_workspace()

    def new_workspace(self):
        return self.workspace_service.new_workspace()

    def load_workspace(self, path):
        return self.workspace_service.load_workspace(path)

    def save_workspace(self, path):
        return self.workspace_service.save_workspace(path)

    # --- Import delegates ---
    def import_csv_dataset(self, path):
        return self.importer_service.import_csv_dataset(path)

    def import_drinkfeed_data(self, path):
        return self.importer_service.import_drinkfeed_data(path)

    def import_actimot_data(self, path):
        return self.importer_service.import_actimot_data(path)

    def import_calo_data(self, path):
        return self.importer_service.import_calo_data(path)

    def import_grouphousing_data(self, path):
        return self.importer_service.import_grouphousing_data(path)

    # --- Dataset delegates ---
    def add_dataset(self, dataset):
        return self.dataset_service.add_dataset(dataset)

    def remove_dataset(self, dataset):
        return self.dataset_service.remove_dataset(dataset)

    def add_datatable(self, datatable):
        return self.dataset_service.add_datatable(datatable)

    def remove_datatable(self, datatable):
        return self.dataset_service.remove_datatable(datatable)

    def merge_datasets(self, new_dataset_name, datasets, single_run, continuous_mode, generate_new_animal_names):
        return self.dataset_service.merge_datasets(
            new_dataset_name, datasets, single_run, continuous_mode, generate_new_animal_names
        )

    def clone_dataset(self, original_dataset, new_name):
        return self.dataset_service.clone_dataset(original_dataset, new_name)

    def clone_datatable(self, original_datatable, new_name):
        return self.dataset_service.clone_datatable(original_datatable, new_name)

    def clone_report(self, original_report, new_name):
        return self.dataset_service.clone_report(original_report, new_name)

    def add_report(self, report):
        return self.dataset_service.add_report(report)

    def delete_report(self, report):
        return self.dataset_service.delete_report(report)


_instance = Manager()

# Selection
get_selected_dataset = _instance.get_selected_dataset
set_selected_dataset = _instance.set_selected_dataset
get_selected_datatable = _instance.get_selected_datatable
set_selected_datatable = _instance.set_selected_datatable

# Workspace
get_workspace = _instance.get_workspace
new_workspace = _instance.new_workspace
load_workspace = _instance.load_workspace
save_workspace = _instance.save_workspace

# Import
import_csv_dataset = _instance.import_csv_dataset
import_drinkfeed_data = _instance.import_drinkfeed_data
import_actimot_data = _instance.import_actimot_data
import_calo_data = _instance.import_calo_data
import_grouphousing_data = _instance.import_grouphousing_data

# Dataset/Datatable/Report
add_dataset = _instance.add_dataset
remove_dataset = _instance.remove_dataset
add_datatable = _instance.add_datatable
remove_datatable = _instance.remove_datatable
merge_datasets = _instance.merge_datasets
clone_dataset = _instance.clone_dataset
clone_datatable = _instance.clone_datatable
clone_report = _instance.clone_report
add_report = _instance.add_report
delete_report = _instance.delete_report
