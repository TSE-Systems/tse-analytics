from pathlib import Path

from NodeGraphQt import NodesPaletteWidget, NodesTreeWidget
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog, QMessageBox, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import manager
from tse_analytics.pipeline import PipelineNodeGraph
from tse_analytics.pipeline.nodes import (
    BoxCoxNode,
    CheckboxNode,
    ConditionNode,
    DatatableInputNode,
    DescriptiveStatsNode,
    IfElseNode,
    NormalityTestNode,
    OneWayAnovaNode,
    ReportNode,
    ResampleNode,
)
from tse_analytics.views.general.pipeline.hotkeys import hotkeys


class PipelineEditorWidget(QWidget):
    """Widget for creating and editing data analysis pipelines."""

    pipeline_executed = Signal(object)  # Emits result when pipeline is executed

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._init_graph()
        self._current_file = None

        self.nodes_palette = NodesPaletteWidget(parent=parent, node_graph=self.graph)
        self.nodes_palette.setWindowFlags(Qt.WindowType.Tool)

        self.nodes_tree = NodesTreeWidget(parent=self, node_graph=self.graph)
        self.nodes_tree.setWindowFlags(Qt.WindowType.Tool)

    def _init_ui(self):
        """Initialize the user interface."""
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        # Create toolbar
        self.toolbar = QToolBar(
            "Pipeline Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        # Add toolbar actions
        self.action_new = self.toolbar.addAction(QIcon(":/icons/icons8-file-16.png"), "New")
        self.action_new.setToolTip("Create a new pipeline")
        self.action_new.triggered.connect(self._new_pipeline)

        self.action_open = self.toolbar.addAction(QIcon(":/icons/icons8-opened-folder-16.png"), "Open")
        self.action_open.setToolTip("Open an existing pipeline")
        self.action_open.triggered.connect(self._open_pipeline)

        self.action_save = self.toolbar.addAction(QIcon(":/icons/icons8-save-16.png"), "Save")
        self.action_save.setToolTip("Save the current pipeline")
        self.action_save.triggered.connect(self._save_pipeline)

        self.action_save_as = self.toolbar.addAction(QIcon(":/icons/icons8-save-as-16.png"), "Save As...")
        self.action_save_as.setToolTip("Save the pipeline with a new name")
        self.action_save_as.triggered.connect(self._save_pipeline_as)

        self.toolbar.addSeparator()

        self.action_nodes_palette = self.toolbar.addAction(QIcon(":/icons/icons8-themes-16.png"), "Palette")
        self.action_nodes_palette.setToolTip("Show nodes palette widget")
        self.action_nodes_palette.triggered.connect(self._show_nodes_palette)

        self.action_nodes_tree = self.toolbar.addAction(QIcon(":/icons/icons8-folder-tree-16.png"), "Tree")
        self.action_nodes_tree.setToolTip("Show nodes tree widget")
        self.action_nodes_tree.triggered.connect(self._show_nodes_tree)

        self.toolbar.addSeparator()

        self.action_initialize = self.toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Initialize Pipeline")
        self.action_initialize.setToolTip("Initialize the current pipeline with default values")
        self.action_initialize.triggered.connect(self._initialize_pipeline)

        self.action_execute = self.toolbar.addAction(QIcon(":/icons/icons8-play-16.png"), "Execute Pipeline")
        self.action_execute.setToolTip("Execute current pipeline")
        self.action_execute.triggered.connect(self._execute_pipeline)

        self._layout.addWidget(self.toolbar)

    def _init_graph(self):
        # Create the node graph
        self.graph = PipelineNodeGraph(self)

        self.graph.set_context_menu("graph", hotkeys, str(Path(__file__).parent.resolve()))

        # Register all custom nodes
        self.graph.register_nodes([
            BoxCoxNode,
            CheckboxNode,
            ConditionNode,
            DatatableInputNode,
            DescriptiveStatsNode,
            IfElseNode,
            NormalityTestNode,
            OneWayAnovaNode,
            ReportNode,
            ResampleNode,
        ])

        # Get the graph widget and add it to the layout
        self._layout.addWidget(self.graph.widget)

        # Configure graph appearance
        # self.graph.widget.setMinimumSize(400, 300)

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
            self,
            "Save Pipeline",
            "",
            "Pipeline Files (*.pipeline);;JSON Files (*.json)",
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

    def _show_nodes_palette(self):
        if not self.nodes_palette.isVisible():
            self.nodes_palette.show()

    def _show_nodes_tree(self):
        if not self.nodes_tree.isVisible():
            self.nodes_tree.show()

    def _initialize_pipeline(self):
        if (
            QMessageBox.question(
                self,
                "Pipeline",
                "Do you want to initialize the pipeline with default values?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.No
        ):
            return

        dataset = manager.get_selected_dataset()
        if dataset is not None:
            self.graph.initialize_pipeline(dataset)

    def _execute_pipeline(self):
        """Execute the current pipeline."""
        # Get all nodes in topological order
        nodes = self.graph.get_execution_order()

        if not nodes:
            QMessageBox.information(self, "Pipeline", "Pipeline is empty. Add nodes to execute.")
            return

        # Execute nodes in order
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        node_outputs = self.graph.execute_pipeline(dataset)

        # Emit signal with results
        self.pipeline_executed.emit(node_outputs)

        QMessageBox.information(self, "Pipeline", "Pipeline executed successfully!")

        # try:
        #     # Execute nodes in order
        #     node_outputs = self.graph.execute_pipeline()
        #
        #     # Emit signal with results
        #     self.pipeline_executed.emit(node_outputs)
        #
        #     QMessageBox.information(self, "Pipeline", "Pipeline executed successfully!")
        #
        # except Exception as e:
        #     QMessageBox.critical(self, "Error", f"Failed to execute pipeline: {str(e)}")

    def get_graph(self):
        """Get the node graph instance."""
        return self.graph
