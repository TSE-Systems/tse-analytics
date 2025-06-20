from PySide6.QtWidgets import QAbstractItemDelegate, QAbstractItemView, QComboBox, QStyledItemDelegate

from tse_analytics.core.data.shared import Aggregation


class AggregationComboBoxDelegate(QStyledItemDelegate):
    """
    A delegate that provides a combo box for selecting aggregation operations.

    This delegate displays a combo box with available aggregation operations
    when editing a cell in a view, allowing users to select from predefined options.
    """

    aggregation_operations = list(Aggregation)

    def paint(self, painter, option, index):
        """
        Paint the delegate using the given painter and style option.

        This method opens a persistent editor for the index if the parent is an
        QAbstractItemView, ensuring the combo box is always visible.

        Args:
            painter: The QPainter to use for painting.
            option: The QStyleOptionViewItem containing style options.
            index (QModelIndex): The index to paint.
        """
        if isinstance(self.parent(), QAbstractItemView):
            self.parent().openPersistentEditor(index)
        QStyledItemDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index):
        """
        Create and return an editor for the item at the given index.

        This method creates a combo box with all available aggregation operations.

        Args:
            parent (QWidget): The parent widget.
            option: The QStyleOptionViewItem containing style options.
            index (QModelIndex): The index for which to create an editor.

        Returns:
            QComboBox: A combo box containing aggregation operations.
        """
        combobox = QComboBox(parent)
        combobox.addItems(self.aggregation_operations)
        combobox.currentIndexChanged.connect(self.onCurrentIndexChanged)
        return combobox

    def onCurrentIndexChanged(self, ix):
        """
        Handle changes in the combo box selection.

        This method commits the data and closes the editor when the user
        selects a different item in the combo box.

        Args:
            ix (int): The index of the newly selected item.
        """
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, QAbstractItemDelegate.EndEditHint.NoHint)
