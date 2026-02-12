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
        self.selection = SelectionService()
        self.workspace = WorkspaceService(self.selection)
        self.dataset = DatasetService(self.workspace, self.selection)
        self.importer = ImportService(self.selection, self.dataset, self.workspace)

    # --- Selection delegates ---
    def get_selected_dataset(self):
        return self.selection.get_selected_dataset()

    def set_selected_dataset(self, dataset):
        return self.selection.set_selected_dataset(dataset)

    def get_selected_datatable(self):
        return self.selection.get_selected_datatable()

    def set_selected_datatable(self, datatable):
        return self.selection.set_selected_datatable(datatable)

    # --- Workspace delegates ---
    def get_workspace(self):
        return self.workspace.get_workspace()

    def new_workspace(self):
        return self.workspace.new_workspace()

    def load_workspace(self, path):
        return self.workspace.load_workspace(path)

    def save_workspace(self, path):
        return self.workspace.save_workspace(path)

    # --- Import delegates ---
    def import_csv_dataset(self, path):
        return self.importer.import_csv_dataset(path)

    def import_drinkfeed_data(self, path):
        return self.importer.import_drinkfeed_data(path)

    def import_actimot_data(self, path):
        return self.importer.import_actimot_data(path)

    def import_calo_data(self, path):
        return self.importer.import_calo_data(path)

    def import_grouphousing_data(self, path):
        return self.importer.import_grouphousing_data(path)

    # --- Dataset delegates ---
    def add_dataset(self, dataset):
        return self.dataset.add_dataset(dataset)

    def remove_dataset(self, dataset):
        return self.dataset.remove_dataset(dataset)

    def add_datatable(self, datatable):
        return self.dataset.add_datatable(datatable)

    def remove_datatable(self, datatable):
        return self.dataset.remove_datatable(datatable)

    def merge_datasets(self, new_dataset_name, datasets, single_run, continuous_mode, generate_new_animal_names):
        return self.dataset.merge_datasets(
            new_dataset_name, datasets, single_run, continuous_mode, generate_new_animal_names
        )

    def clone_dataset(self, original_dataset, new_dataset_name):
        return self.dataset.clone_dataset(original_dataset, new_dataset_name)

    def add_report(self, report):
        return self.dataset.add_report(report)

    def delete_report(self, report):
        return self.dataset.delete_report(report)


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
add_report = _instance.add_report
delete_report = _instance.delete_report
