from pyqtgraph import ViewBox, mkPen


class TileView(ViewBox):
    def __init__(self, parent, image_item: any):
        super().__init__(parent, border=mkPen("d", width=1), lockAspect=True, name=image_item.channel.metal, invertY=True)
        self.addItem(image_item, ignoreBounds=False)
