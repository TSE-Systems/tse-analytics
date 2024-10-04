from PySide6.QtWidgets import QStyledItemDelegate, QAbstractItemView, QComboBox, QAbstractItemDelegate

from tse_analytics.core.data.shared import Aggregation


class AggregationComboBoxDelegate(QStyledItemDelegate):
    aggregation_operations = (i for i in Aggregation)

    def paint(self, painter, option, index):
        if isinstance(self.parent(), QAbstractItemView):
            self.parent().openPersistentEditor(index)
        QStyledItemDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index):
        combobox = QComboBox(parent)
        combobox.addItems(self.aggregation_operations)
        combobox.currentIndexChanged.connect(self.onCurrentIndexChanged)
        return combobox

    def onCurrentIndexChanged(self, ix):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, QAbstractItemDelegate.EndEditHint.NoHint)
