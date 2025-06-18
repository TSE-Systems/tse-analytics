import pandas as pd
from PySide6.QtWidgets import QAbstractItemView, QListView, QWidget

from tse_analytics.core.models.pandas_list_model import PandasListModel


class PandasListView(QListView):
    """
    A list view widget for displaying pandas DataFrame data.

    This widget provides a simple way to display pandas DataFrame data
    in a list format, with each row of the DataFrame shown as an item in the list.
    """

    def __init__(self, parent: QWidget | None = None):
        """
        Initialize the PandasListView widget.

        Args:
            parent: The parent widget. Default is None.
        """
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    def set_data(self, df: pd.DataFrame):
        """
        Set the pandas DataFrame to be displayed in the list view.

        This method creates a new PandasListModel with the provided DataFrame
        and sets it as the model for this view.

        Args:
            df: The pandas DataFrame to display.
        """
        model = PandasListModel(df)
        self.setModel(model)
