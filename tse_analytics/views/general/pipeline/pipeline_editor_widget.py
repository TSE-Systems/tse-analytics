"""Pipeline editor widget using NodeGraphQt."""

import json
from pathlib import Path

from NodeGraphQt import NodeGraph
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QFileDialog, QMessageBox, QToolBar, QVBoxLayout, QWidget

from tse_analytics.views.general.pipeline.nodes import (
    ANOVANode,
    AggregateNode,
    BinningNode,
    CorrelationNode,
    DatasetInputNode,
    DatasetOutputNode,
    FilterNode,
    MergeNode,
    StatisticsNode,
    TTestNode,
    ViewerNode,
)


class PipelineEditorWidget(QWidget):
    """Widget for creating and editing data analysis pipelines."""

    pipeline_executed = Signal(object)  # Emits result when pipeline is executed

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._init_graph()
        self._current_file = None

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create toolbar
        self.toolbar = QToolBar("Pipeline Toolbar")
        self.toolbar.setMovable(False)

        # Add toolbar actions
        self.action_new = QAction(QIcon(":/icons/new.png"), "New Pipeline", self)
        self.action_new.setToolTip("Create a new pipeline")
        self.action_new.triggered.connect(self._new_pipeline)
        self.toolbar.addAction(self.action_new)

        self.action_open = QAction(QIcon(":/icons/open.png"), "Open Pipeline", self)
        self.action_open.setToolTip("Open an existing pipeline")
        self.action_open.triggered.connect(self._open_pipeline)
        self.toolbar.addAction(self.action_open)

        self.action_save = QAction(QIcon(":/icons/save.png"), "Save Pipeline", self)
        self.action_save.setToolTip("Save the current pipeline")
        self.action_save.triggered.connect(self._save_pipeline)
        self.toolbar.addAction(self.action_save)

        self.action_save_as = QAction(QIcon(":/icons/save.png"), "Save Pipeline As...", self)
        self.action_save_as.setToolTip("Save the pipeline with a new name")
        self.action_save_as.triggered.connect(self._save_pipeline_as)
        self.toolbar.addAction(self.action_save_as)

        self.toolbar.addSeparator()

        self.action_execute = QAction(QIcon(":/icons/play.png"), "Execute Pipeline", self)
        self.action_execute.setToolTip("Execute the current pipeline")
        self.action_execute.triggered.connect(self._execute_pipeline)
        self.toolbar.addAction(self.action_execute)

        layout.addWidget(self.toolbar)

    def _init_graph(self):
        """Initialize the node graph."""
        # Create the node graph
        self.graph = NodeGraph()

        # set up context menu for the node graph.
        BASE_PATH = Path(__file__).parent.resolve()
        hotkey_path = Path(BASE_PATH, '', 'hotkeys.json')
        self.graph.set_context_menu_from_file(hotkey_path, 'graph')

        # Register all custom nodes
        self.graph.register_nodes(
            [
                # Base nodes
                DatasetInputNode,
                DatasetOutputNode,
                ViewerNode,
                # Transform nodes
                FilterNode,
                AggregateNode,
                MergeNode,
                BinningNode,
                # Analysis nodes
                StatisticsNode,
                CorrelationNode,
                TTestNode,
                ANOVANode,
            ]
        )

        # Get the graph widget and add it to the layout
        self.graph_widget = self.graph.widget
        self.layout().addWidget(self.graph_widget)

        # Configure graph appearance
        self.graph_widget.setMinimumSize(400, 300)

    def _new_pipeline(self):
        """Create a new pipeline."""
        if self.graph.all_nodes():
            reply = QMessageBox.question(
                self,
                "New Pipeline",
                "This will clear the current pipeline. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return

        self.graph.clear_session()
        self._current_file = None

    def _open_pipeline(self):
        """Open an existing pipeline from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Pipeline", "", "Pipeline Files (*.pipeline);;JSON Files (*.json)"
        )
        if file_path:
            try:
                self.graph.load_session(file_path)
                self._current_file = file_path
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open pipeline: {str(e)}")

    def _save_pipeline(self):
        """Save the current pipeline."""
        if self._current_file:
            self._save_to_file(self._current_file)
        else:
            self._save_pipeline_as()

    def _save_pipeline_as(self):
        """Save the current pipeline with a new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Pipeline", "", "Pipeline Files (*.pipeline);;JSON Files (*.json)"
        )
        if file_path:
            self._save_to_file(file_path)
            self._current_file = file_path

    def _save_to_file(self, file_path: str):
        """Save the pipeline to a file."""
        try:
            self.graph.save_session(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save pipeline: {str(e)}")

    def _execute_pipeline(self):
        """Execute the current pipeline."""
        try:
            # Get all nodes in topological order
            nodes = self._get_execution_order()

            if not nodes:
                QMessageBox.information(self, "Pipeline", "Pipeline is empty. Add nodes to execute.")
                return

            # Execute nodes in order
            node_outputs = {}
            for node in nodes:
                # Get inputs from connected nodes
                inputs = []
                for input_port in node.input_ports():
                    connected_ports = input_port.connected_ports()
                    if connected_ports:
                        # Get the output from the connected node
                        connected_node = connected_ports[0].node()
                        if connected_node.id in node_outputs:
                            inputs.append(node_outputs[connected_node.id])
                        else:
                            inputs.append(None)
                    else:
                        inputs.append(None)

                # Execute the node
                if hasattr(node, "process"):
                    result = node.process(*inputs) if inputs else node.process(None)
                elif hasattr(node, "get_dataset"):
                    result = node.get_dataset()
                else:
                    result = None

                # Store the output
                node_outputs[node.id] = result

            # Emit signal with results
            self.pipeline_executed.emit(node_outputs)

            QMessageBox.information(self, "Pipeline", "Pipeline executed successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to execute pipeline: {str(e)}")

    def _get_execution_order(self):
        """Get nodes in topological execution order."""
        # Simple topological sort
        all_nodes = self.graph.all_nodes()
        if not all_nodes:
            return []

        # Build dependency graph
        in_degree = {node.id: 0 for node in all_nodes}
        adj_list = {node.id: [] for node in all_nodes}

        for node in all_nodes:
            for output_port in node.output_ports():
                for connected_port in output_port.connected_ports():
                    connected_node = connected_port.node()
                    adj_list[node.id].append(connected_node)
                    in_degree[connected_node.id] += 1

        # Topological sort using Kahn's algorithm
        queue = [node for node in all_nodes if in_degree[node.id] == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            if node.id in adj_list:
                for neighbor in adj_list[node.id]:
                    in_degree[neighbor.id] -= 1
                    if in_degree[neighbor.id] == 0:
                        queue.append(neighbor)

        return result

    def get_graph(self):
        """Get the node graph instance."""
        return self.graph
