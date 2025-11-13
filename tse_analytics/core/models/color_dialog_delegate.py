from PySide6.QtCore import Qt
from PySide6.QtWidgets import QColorDialog, QStyledItemDelegate


class ColorDialogDelegate(QStyledItemDelegate):
    """Delegate that opens a QColorDialog to edit the color."""

    def createEditor(self, parent, option, index):
        item = index.model().data(index, Qt.ItemDataRole.EditRole)
        new_color = QColorDialog.getColor(item.color, parent, "Select Color")
        if new_color.isValid():
            index.model().setData(index, new_color, Qt.ItemDataRole.EditRole)
        return None
