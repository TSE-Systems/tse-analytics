import os
import uuid

from PySide6.QtGui import QFont, QImage, QTextDocument
from PySide6.QtWidgets import QTextEdit

IMAGE_EXTENSIONS = [".jpg", ".png", ".bmp"]


class CustomTextEdit(QTextEdit):
    """
    A custom text editor with enhanced image handling capabilities.

    This class extends QTextEdit to provide support for inserting images
    from various sources including clipboard, drag-and-drop, and local files.
    It handles common image formats like JPG, PNG, and BMP.
    """

    def __init__(self, parent=None):
        super().__init__(
            parent,
            undoRedoEnabled=True,
            readOnly=False,
            lineWrapMode=QTextEdit.LineWrapMode.NoWrap,
            autoFormatting=QTextEdit.AutoFormattingFlag.AutoAll,
        )

        self.document().setDefaultFont(QFont("Segoe UI", 10))
        # self.document().setDefaultStyleSheet(style_descriptive_table)

    def canInsertFromMimeData(self, source):
        """
        Check if the mime data can be inserted into the text edit.

        Overrides the parent method to add support for image data.

        Args:
            source: The QMimeData object to check.

        Returns:
            True if the data can be inserted, False otherwise.
        """
        if source.hasImage():
            return True
        else:
            return super().canInsertFromMimeData(source)

    def insertFromMimeData(self, source):
        """
        Insert content from mime data into the text edit.

        Overrides the parent method to add support for inserting images from:
        - Local image files (via URLs)
        - Clipboard image data

        Args:
            source: The QMimeData object containing the data to insert.
        """
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
