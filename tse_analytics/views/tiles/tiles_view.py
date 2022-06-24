from PySide6.QtWidgets import QWidget
from pyqtgraph import GraphicsView, GraphicsLayout
from tse_datatools.data.animal import Animal

from tse_analytics.views.tiles.tile_view import TileView


class TilesView(GraphicsView):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.layout = GraphicsLayout()
        self.setCentralItem(self.layout)

        self.tiles: dict[str, TileView] = {}

    def clear(self):
        self.layout.clear()
        self.tiles.clear()

    def get_cell(self, i: int):
        l = len(self.tiles.keys())
        if l > 9:
            rows = (0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3)
            cols = (0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3)
        elif l > 4:
            rows = (0, 0, 0, 1, 1, 1, 2, 2, 2)
            cols = (0, 1, 2, 0, 1, 2, 0, 1, 2)
        else:
            rows = (0, 0, 1, 1)
            cols = (0, 1, 0, 1)
        return rows[i], cols[i]

    def set_data(self, items: list[Animal]):
        self.clear()
        # if len(items) > 0:
        #     for item in items:
        #         tile = TileView(self.layout, item)
        #         self.tiles[item.channel.metal] = tile
        #
        #     first_tile = self.tiles[list(self.tiles.keys())[0]]
        #     for i, tile in enumerate(self.tiles.values()):
        #         if first_tile is not tile:
        #             tile.linkView(ViewBox.XAxis, first_tile)
        #             tile.linkView(ViewBox.YAxis, first_tile)
        #         cell = self.get_cell(i)
        #         self.layout.addItem(tile, cell[0], cell[1])

    def fit_all_tiles(self):
        for name, tile in self.tiles.items():
            tile.autoRange()
