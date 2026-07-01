from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QTextEdit


class ReportEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(
            parent,
            undoRedoEnabled=False,
            readOnly=True,
            lineWrapMode=QTextEdit.LineWrapMode.NoWrap,
        )

        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont)
        font.setPointSize(10)
        self.document().setDefaultFont(font)
        # self.document().setDefaultStyleSheet(style_descriptive_table)

    def set_content(self, content: str) -> None:
        self.document().setHtml(content)

    def clear(self) -> None:
        self.document().clear()
