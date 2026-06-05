"""Core manager module for TSE Analytics.

Wires up the four core services and exposes their public methods as
module-level functions.
"""

from tse_analytics.core.services.dataset_service import DatasetService
from tse_analytics.core.services.import_service import ImportService
from tse_analytics.core.services.selection_service import SelectionService
from tse_analytics.core.services.workspace_service import WorkspaceService

selection_service = SelectionService()
workspace_service = WorkspaceService(selection_service)
dataset_service = DatasetService(workspace_service, selection_service)
importer_service = ImportService(selection_service, dataset_service, workspace_service)

# Selection
get_selected_dataset = selection_service.get_selected_dataset
set_selected_dataset = selection_service.set_selected_dataset
get_selected_datatable = selection_service.get_selected_datatable
set_selected_datatable = selection_service.set_selected_datatable

# Workspace
get_workspace = workspace_service.get_workspace
new_workspace = workspace_service.new_workspace
load_workspace = workspace_service.load_workspace
save_workspace = workspace_service.save_workspace

# Import
import_csv_dataset = importer_service.import_csv_dataset
import_drinkfeed_data = importer_service.import_drinkfeed_data
import_actimot_data = importer_service.import_actimot_data
import_calo_data = importer_service.import_calo_data
import_grouphousing_data = importer_service.import_grouphousing_data

# Dataset / Datatable / Report
add_dataset = dataset_service.add_dataset
remove_dataset = dataset_service.remove_dataset
add_datatable = dataset_service.add_datatable
remove_datatable = dataset_service.remove_datatable
merge_datasets = dataset_service.merge_datasets
clone_dataset = dataset_service.clone_dataset
clone_datatable = dataset_service.clone_datatable
clone_report = dataset_service.clone_report
add_report = dataset_service.add_report
delete_report = dataset_service.delete_report
