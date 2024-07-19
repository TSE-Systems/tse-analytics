import os
import uuid

from PySide6.QtGui import QFont, QImage, QTextDocument
from PySide6.QtWidgets import QTextEdit

IMAGE_EXTENSIONS = [".jpg", ".png", ".bmp"]


class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFormatting(QTextEdit.AutoFormattingFlag.AutoAll)
        # Initialize default font size.
        font = QFont("Times", 12)
        self.setFont(font)
        # We need to repeat the size to init the current format.
        self.setFontPointSize(12)

    def canInsertFromMimeData(self, source):
        if source.hasImage():
            return True
        else:
            return super().canInsertFromMimeData(source)

    def insertFromMimeData(self, source):
        cursor = self.textCursor()
        document = self.document()

        if source.hasUrls():
            for u in source.urls():
                file_ext = os.path.splitext(str(u.toLocalFile()))[1].lower()
                if u.isLocalFile() and file_ext in IMAGE_EXTENSIONS:
                    image = QImage(u.toLocalFile())
                    document.addResource(QTextDocument.ResourceType.ImageResource, u, image)
                    cursor.insertImage(u.toLocalFile())

                else:
                    # If we hit a non-image or non-local URL break the loop and fall out
                    # to the super call & let Qt handle it
                    break

            else:
                # If all were valid images, finish here.
                return

        elif source.hasImage():
            image = source.imageData()
            image_id = uuid.uuid4().hex
            document.addResource(QTextDocument.ResourceType.ImageResource, image_id, image)
            cursor.insertImage(image_id)
            return

        super().insertFromMimeData(source)
