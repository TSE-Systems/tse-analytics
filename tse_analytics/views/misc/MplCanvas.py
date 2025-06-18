from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):
    """
    A Matplotlib canvas for embedding plots in Qt applications.

    This class provides a canvas for matplotlib figures that can be integrated
    into Qt applications. It inherits from FigureCanvasQTAgg which handles the
    integration between matplotlib and Qt.
    """

    def __init__(self, parent=None, width=6.4, height=4.8, dpi=100):
        """
        Initialize the MplCanvas widget.

        Args:
            parent: The parent widget. Default is None.
            width: Width of the figure in inches. Default is 6.4.
            height: Height of the figure in inches. Default is 4.8.
            dpi: Dots per inch (resolution) of the figure. Default is 100.
        """
        fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(fig)
        self.setParent(parent)

    def clear(self, redraw=True):
        """
        Clear the figure, removing all axes, texts, lines, etc.

        Args:
            redraw: If True, redraw the canvas after clearing. Default is True.
        """
        self.figure.clear()
        if redraw:
            self.draw()
