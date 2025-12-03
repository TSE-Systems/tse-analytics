from NodeGraphQt import BaseNode, NodeGraph, PropertiesBinWidget
from PySide6.QtCore import Qt

from tse_analytics.core.data.dataset import Dataset


class PipelineNodeGraph(NodeGraph):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Properties bin widget.
        self._properties_bin = PropertiesBinWidget(node_graph=self)
        self._properties_bin.setWindowFlags(Qt.WindowType.Tool)

        # wire signal.
        self.node_double_clicked.connect(self.display_prop_bin)

    def display_prop_bin(self, node: BaseNode):
        """
        Function for displaying PropertiesBinWidget when a node is double-clicked
        """
        if not self._properties_bin.isVisible():
            self._properties_bin.show()

    def initialize_pipeline(self, dataset: Dataset):
        all_nodes = self.all_nodes()
        for node in all_nodes:
            if hasattr(node, "initialize"):
                node.initialize()

    def get_execution_order(self) -> list[BaseNode]:
        """
        Get nodes in topological execution order.
        """
        all_nodes = self.all_nodes()
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

    def execute_pipeline(self) -> dict:
        # Get all nodes in topological order
        nodes = self.get_execution_order()

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

        return node_outputs
