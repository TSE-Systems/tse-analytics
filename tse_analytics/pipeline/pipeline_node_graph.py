from NodeGraphQt import NodeGraph, PropertiesBinWidget
from PySide6.QtCore import Qt


class PipelineNodeGraph(NodeGraph):
    def __init__(self, parent=None):
        super().__init__(parent)

        # properties bin widget.
        self._prop_bin = PropertiesBinWidget(node_graph=self)
        self._prop_bin.setWindowFlags(Qt.WindowType.Tool)

        # wire signal.
        self.node_double_clicked.connect(self.display_prop_bin)

    def display_prop_bin(self, node):
        """
        function for displaying the properties bin when a node is double clicked
        """
        if not self._prop_bin.isVisible():
            self._prop_bin.show()
