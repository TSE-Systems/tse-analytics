from NodeGraphQt import BaseNode, NodeGraph, PropertiesBinWidget
from PySide6.QtCore import Qt

from tse_analytics.core.data.dataset import Dataset


class PipelineNodeGraph(NodeGraph):
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.set_background_color(255, 255, 255)
        # self.set_grid_color(223, 227, 239)

        # Properties bin widget.
        self._properties_bin = PropertiesBinWidget(node_graph=self)
        self._properties_bin.set_limit(1)
        self._properties_bin.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)

        self.node_double_clicked.connect(self.display_prop_bin)

    def _register_builtin_nodes(self):
        # See https://github.com/jchanvfx/NodeGraphQt/issues/481
        pass

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
                node.initialize(dataset)

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

    def execute_pipeline(self, dataset: Dataset) -> dict:
        """
        Execute pipeline with support for conditional branching.
        Handles if/else nodes by routing data through appropriate branches.
        """
        nodes = self.get_execution_order()
        node_outputs = {}
        port_outputs = {}  # Store outputs per port for branching

        for node in nodes:
            # Get inputs from connected nodes via specific ports
            inputs = []
            for input_port in node.input_ports():
                connected_ports = input_port.connected_ports()
                if connected_ports:
                    # Get output from connected port
                    connected_port = connected_ports[0]
                    port_key = (connected_port.node().id, connected_port.name())

                    if port_key in port_outputs:
                        inputs.append(port_outputs[port_key])
                    else:
                        # Fallback to node output
                        connected_node = connected_port.node()
                        if connected_node.id in node_outputs:
                            inputs.append(node_outputs[connected_node.id])
                        else:
                            inputs.append(None)
                else:
                    inputs.append(None)

            # Execute the node
            if hasattr(node, "process"):
                result = node.process(*inputs) if inputs else node.process(None)
            else:
                result = None

            # Store outputs
            node_outputs[node.id] = result

            # For nodes with multiple outputs (like if/else), map results to ports
            output_ports = node.output_ports()
            if isinstance(result, (tuple, list)) and len(output_ports) == len(result):
                # Map each output to its corresponding port
                for port, value in zip(output_ports, result):
                    port_key = (node.id, port.name())
                    port_outputs[port_key] = value
            elif len(output_ports) > 0:
                # Single output: assign to all ports
                for port in output_ports:
                    port_key = (node.id, port.name())
                    port_outputs[port_key] = result

        return node_outputs
