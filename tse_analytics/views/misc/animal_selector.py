from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QTableView, QHeaderView

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Animal
from tse_analytics.core.models.animals_simple_model import AnimalsSimpleModel


class AnimalSelector(QComboBox):
    """
    A custom combo box for selecting animals from a dataset.

    This widget displays a table view of animals in a dropdown list,
    allowing users to select a single animal from the dataset.
    """

    def __init__(self, parent=None):
        """
        Initialize the AnimalSelector widget.

        Args:
            parent: The parent widget. Default is None.
        """
        super().__init__(parent)

        self.table_view = QTableView(
            self,
            sortingEnabled=False,
        )
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setAutoScroll(False)
        self.table_view.horizontalHeader().ResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_view.verticalHeader().hide()
        self.table_view.verticalHeader().setDefaultSectionSize(20)

        self.setView(self.table_view)

        self.dataset: Dataset | None = None

    def set_data(self, dataset: Dataset, selected_animal: str = None) -> None:
        """
        Set the dataset for the animal selector and update the model.

        This method configures the combo box to display animals from the provided dataset
        and adjusts the view to properly display all columns.

        Args:
            dataset: The Dataset object containing animal information.
            selected_animal: Animal ID to select.
        """
        self.dataset = dataset
        model = AnimalsSimpleModel(self.dataset)
        self.setModel(model)
        self.table_view.resizeColumnsToContents()
        self.table_view.resizeRowsToContents()
        self.table_view.setMinimumWidth(self.table_view.horizontalHeader().length())
        if selected_animal is not None:
            self.setCurrentText(selected_animal)

    def get_selected_animal(self) -> Animal | None:
        """
        Get the currently selected animal from the combo box.

        Returns:
            The selected Animal object, or None if no animal is selected.
        """
        animal_name = self.currentText()
        return self.dataset.animals[animal_name] if animal_name != "" else None
