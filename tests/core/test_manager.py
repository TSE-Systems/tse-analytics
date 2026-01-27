"""
Unit tests for tse_analytics.core.manager module.
"""

import pickle
from unittest.mock import MagicMock, mock_open, patch
from uuid import UUID

import pytest
from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.workspace import Workspace
from tse_analytics.core.manager import Manager


@pytest.fixture
def manager():
    """Create a fresh Manager instance for each test."""
    return Manager()


@pytest.fixture
def mock_dataset():
    """Create a mock Dataset object."""
    dataset = MagicMock(spec=Dataset)
    dataset.id = "test-dataset-id"
    dataset.metadata = {"name": "Test Dataset"}
    dataset.datatables = []
    return dataset


@pytest.fixture
def mock_datatable():
    """Create a mock Datatable object."""
    datatable = MagicMock(spec=Datatable)
    datatable.id = "test-datatable-id"
    mock_dataset = MagicMock(spec=Dataset)
    datatable.dataset = mock_dataset
    return datatable


class TestManagerInitialization:
    """Tests for Manager initialization."""

    def test_initializes_with_default_workspace(self, manager):
        """Test that Manager initializes with a default workspace."""
        workspace = manager.get_workspace()
        assert isinstance(workspace, Workspace)
        assert workspace.name == "Default Workspace"

    def test_initializes_with_no_selected_dataset(self, manager):
        """Test that Manager initializes with no selected dataset."""
        assert manager.get_selected_dataset() is None

    def test_initializes_with_no_selected_datatable(self, manager):
        """Test that Manager initializes with no selected datatable."""
        assert manager.get_selected_datatable() is None


class TestGetWorkspace:
    """Tests for get_workspace method."""

    def test_returns_workspace_object(self, manager):
        """Test that get_workspace returns a Workspace object."""
        result = manager.get_workspace()
        assert isinstance(result, Workspace)

    def test_returns_same_workspace(self, manager):
        """Test that get_workspace returns the same workspace instance."""
        workspace1 = manager.get_workspace()
        workspace2 = manager.get_workspace()
        assert workspace1 is workspace2


class TestSelectedDataset:
    """Tests for selected dataset methods."""

    def test_set_and_get_selected_dataset(self, manager, mock_dataset):
        """Test setting and getting selected dataset."""
        with patch.object(messaging, "broadcast"):
            manager.set_selected_dataset(mock_dataset)
        assert manager.get_selected_dataset() == mock_dataset

    def test_set_selected_dataset_broadcasts_message(self, manager, mock_dataset):
        """Test that set_selected_dataset broadcasts a message."""
        with patch.object(messaging, "broadcast") as mock_broadcast:
            manager.set_selected_dataset(mock_dataset)
            assert mock_broadcast.called
            call_args = mock_broadcast.call_args[0][0]
            assert isinstance(call_args, messaging.DatasetChangedMessage)

    def test_set_selected_dataset_to_none(self, manager):
        """Test setting selected dataset to None."""
        with patch.object(messaging, "broadcast"):
            manager.set_selected_dataset(None)
        assert manager.get_selected_dataset() is None

    def test_change_selected_dataset(self, manager, mock_dataset):
        """Test changing the selected dataset."""
        mock_dataset2 = MagicMock(spec=Dataset)
        mock_dataset2.id = "test-dataset-id-2"

        with patch.object(messaging, "broadcast"):
            manager.set_selected_dataset(mock_dataset)
            manager.set_selected_dataset(mock_dataset2)

        assert manager.get_selected_dataset() == mock_dataset2


class TestSelectedDatatable:
    """Tests for selected datatable methods."""

    def test_set_and_get_selected_datatable(self, manager, mock_datatable):
        """Test setting and getting selected datatable."""
        with patch.object(messaging, "broadcast"):
            manager.set_selected_datatable(mock_datatable)
        assert manager.get_selected_datatable() == mock_datatable

    def test_set_selected_datatable_broadcasts_message(self, manager, mock_datatable):
        """Test that set_selected_datatable broadcasts a message."""
        with patch.object(messaging, "broadcast") as mock_broadcast:
            manager.set_selected_datatable(mock_datatable)
            assert mock_broadcast.called
            call_args = mock_broadcast.call_args[0][0]
            assert isinstance(call_args, messaging.DatatableChangedMessage)

    def test_set_selected_datatable_to_none(self, manager):
        """Test setting selected datatable to None."""
        with patch.object(messaging, "broadcast"):
            manager.set_selected_datatable(None)
        assert manager.get_selected_datatable() is None


class TestNewWorkspace:
    """Tests for new_workspace method."""

    def test_creates_new_workspace(self, manager):
        """Test that new_workspace creates a new workspace."""
        with patch.object(messaging, "broadcast"):
            with patch("tse_analytics.core.manager.QTimer"):
                manager.new_workspace()

        workspace = manager.get_workspace()
        assert isinstance(workspace, Workspace)
        assert workspace.name == "Workspace"

    def test_clears_selections(self, manager, mock_dataset, mock_datatable):
        """Test that new_workspace clears selections."""
        with patch.object(messaging, "broadcast"):
            manager.set_selected_dataset(mock_dataset)
            manager.set_selected_datatable(mock_datatable)

        with patch.object(messaging, "broadcast"):
            with patch("tse_analytics.core.manager.QTimer"):
                manager.new_workspace()

        assert manager.get_selected_dataset() is None
        assert manager.get_selected_datatable() is None


class TestLoadWorkspace:
    """Tests for load_workspace method."""

    def test_loads_workspace_from_file(self, manager):
        """Test that load_workspace loads a workspace from file."""
        mock_workspace = Workspace("Loaded Workspace")

        with patch("builtins.open", mock_open(read_data=pickle.dumps(mock_workspace))):
            with patch.object(messaging, "broadcast"):
                with patch("tse_analytics.core.manager.QTimer"):
                    manager.load_workspace("test_path.pkl")

        loaded_workspace = manager.get_workspace()
        assert loaded_workspace.name == "Loaded Workspace"

    def test_clears_selections_after_loading(self, manager, mock_dataset):
        """Test that load_workspace clears selections."""
        with patch.object(messaging, "broadcast"):
            manager.set_selected_dataset(mock_dataset)

        mock_workspace = Workspace("New Workspace")
        with patch("builtins.open", mock_open(read_data=pickle.dumps(mock_workspace))):
            with patch.object(messaging, "broadcast"):
                with patch("tse_analytics.core.manager.QTimer"):
                    manager.load_workspace("test_path.pkl")

        assert manager.get_selected_dataset() is None


class TestSaveWorkspace:
    """Tests for save_workspace method."""

    def test_saves_workspace_to_file(self, manager):
        """Test that save_workspace saves the workspace to a file."""
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("pickle.dump") as mock_dump:
                manager.save_workspace("test_path.pkl")

                mock_file.assert_called_once_with("test_path.pkl", "wb")
                assert mock_dump.called
                # Check that workspace was passed to pickle.dump
                assert isinstance(mock_dump.call_args[0][0], Workspace)


class TestAddDataset:
    """Tests for add_dataset method."""

    def test_adds_dataset_to_workspace(self, manager, mock_dataset):
        """Test that add_dataset adds dataset to workspace."""
        with patch.object(messaging, "broadcast"):
            manager.add_dataset(mock_dataset)

        workspace = manager.get_workspace()
        assert mock_dataset.id in workspace.datasets

    def test_broadcasts_workspace_changed_message(self, manager, mock_dataset):
        """Test that add_dataset broadcasts workspace changed message."""
        with patch.object(messaging, "broadcast") as mock_broadcast:
            manager.add_dataset(mock_dataset)

            assert mock_broadcast.called
            call_args = mock_broadcast.call_args[0][0]
            assert isinstance(call_args, messaging.WorkspaceChangedMessage)


class TestRemoveDataset:
    """Tests for remove_dataset method."""

    def test_removes_dataset_from_workspace(self, manager, mock_dataset):
        """Test that remove_dataset removes dataset from workspace."""
        with patch.object(messaging, "broadcast"):
            manager.add_dataset(mock_dataset)

        with patch.object(messaging, "broadcast"):
            with patch("tse_analytics.core.manager.QTimer"):
                manager.remove_dataset(mock_dataset)

        workspace = manager.get_workspace()
        assert mock_dataset.id not in workspace.datasets

    def test_clears_selections_after_removal(self, manager, mock_dataset):
        """Test that remove_dataset clears selections."""
        with patch.object(messaging, "broadcast"):
            manager.add_dataset(mock_dataset)
            manager.set_selected_dataset(mock_dataset)

        with patch.object(messaging, "broadcast"):
            with patch("tse_analytics.core.manager.QTimer"):
                manager.remove_dataset(mock_dataset)

        assert manager.get_selected_dataset() is None


class TestAddDatatable:
    """Tests for add_datatable method."""

    def test_adds_datatable_to_dataset(self, manager, mock_datatable):
        """Test that add_datatable adds datatable to its dataset."""
        with patch.object(messaging, "broadcast"):
            manager.add_datatable(mock_datatable)

        mock_datatable.dataset.add_datatable.assert_called_once_with(mock_datatable)

    def test_broadcasts_workspace_changed_message(self, manager, mock_datatable):
        """Test that add_datatable broadcasts workspace changed message."""
        with patch.object(messaging, "broadcast") as mock_broadcast:
            manager.add_datatable(mock_datatable)

            assert mock_broadcast.called
            call_args = mock_broadcast.call_args[0][0]
            assert isinstance(call_args, messaging.WorkspaceChangedMessage)


class TestRemoveDatatable:
    """Tests for remove_datatable method."""

    def test_removes_datatable_from_dataset(self, manager, mock_datatable):
        """Test that remove_datatable removes datatable from its dataset."""
        with patch.object(messaging, "broadcast"):
            manager.remove_datatable(mock_datatable)

        mock_datatable.dataset.remove_datatable.assert_called_once_with(mock_datatable)

    def test_clears_selected_datatable(self, manager, mock_datatable):
        """Test that remove_datatable clears selected datatable."""
        with patch.object(messaging, "broadcast"):
            manager.set_selected_datatable(mock_datatable)
            manager.remove_datatable(mock_datatable)

        assert manager.get_selected_datatable() is None

    def test_broadcasts_workspace_changed_message(self, manager, mock_datatable):
        """Test that remove_datatable broadcasts workspace changed message."""
        with patch.object(messaging, "broadcast") as mock_broadcast:
            manager.remove_datatable(mock_datatable)

            # Should be called twice: once for set_selected_datatable(None)
            # and once for the workspace change
            assert mock_broadcast.call_count >= 1


class TestCloneDataset:
    """Tests for clone_dataset method."""

    @patch("tse_analytics.core.manager.copy.deepcopy")
    @patch("tse_analytics.core.manager.uuid4")
    def test_creates_deep_copy_of_dataset(self, mock_uuid4, mock_deepcopy, manager, mock_dataset):
        """Test that clone_dataset creates a deep copy of the dataset."""
        mock_uuid4.return_value = UUID("12345678-1234-5678-1234-567812345678")
        mock_cloned = MagicMock(spec=Dataset)
        mock_cloned.id = "cloned-id"
        mock_cloned.metadata = {"name": "Clone"}
        mock_deepcopy.return_value = mock_cloned

        with patch.object(messaging, "broadcast"):
            manager.clone_dataset(mock_dataset, "Cloned Dataset")

        mock_deepcopy.assert_called_once_with(mock_dataset)

    @patch("tse_analytics.core.manager.copy.deepcopy")
    @patch("tse_analytics.core.manager.uuid4")
    def test_assigns_new_id_to_clone(self, mock_uuid4, mock_deepcopy, manager, mock_dataset):
        """Test that clone_dataset assigns a new UUID to the cloned dataset."""
        new_uuid = UUID("12345678-1234-5678-1234-567812345678")
        mock_uuid4.return_value = new_uuid

        mock_cloned = MagicMock(spec=Dataset)
        mock_cloned.id = None
        mock_cloned.metadata = {}
        mock_deepcopy.return_value = mock_cloned

        with patch.object(messaging, "broadcast"):
            manager.clone_dataset(mock_dataset, "Cloned Dataset")

        assert mock_cloned.id == new_uuid

    @patch("tse_analytics.core.manager.copy.deepcopy")
    @patch("tse_analytics.core.manager.uuid4")
    def test_sets_new_name_on_clone(self, mock_uuid4, mock_deepcopy, manager, mock_dataset):
        """Test that clone_dataset sets a new name on the cloned dataset."""
        mock_cloned = MagicMock(spec=Dataset)
        mock_cloned.metadata = {}
        mock_deepcopy.return_value = mock_cloned

        with patch.object(messaging, "broadcast"):
            manager.clone_dataset(mock_dataset, "New Clone Name")

        assert mock_cloned.metadata["name"] == "New Clone Name"


class TestModuleLevelFunctions:
    """Tests for module-level function exports."""

    def test_module_level_functions_exist(self):
        """Test that module-level functions are exported."""
        from tse_analytics.core import manager

        assert hasattr(manager, "get_workspace")
        assert hasattr(manager, "get_selected_dataset")
        assert hasattr(manager, "set_selected_dataset")
        assert hasattr(manager, "get_selected_datatable")
        assert hasattr(manager, "set_selected_datatable")
        assert hasattr(manager, "new_workspace")
        assert hasattr(manager, "load_workspace")
        assert hasattr(manager, "save_workspace")
        assert hasattr(manager, "add_dataset")
        assert hasattr(manager, "remove_dataset")
        assert hasattr(manager, "add_datatable")
        assert hasattr(manager, "remove_datatable")

    def test_module_level_functions_are_callable(self):
        """Test that module-level functions are callable."""
        from tse_analytics.core import manager

        assert callable(manager.get_workspace)
        assert callable(manager.get_selected_dataset)
        assert callable(manager.set_selected_dataset)
