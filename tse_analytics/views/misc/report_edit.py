from PySide6.QtWidgets import QTextEdit

from tse_analytics.styles.css import style_descriptive_table


class ReportEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(
            parent,
            undoRedoEnabled=False,
            readOnly=True,
            lineWrapMode=QTextEdit.LineWrapMode.NoWrap,
        )

        self.document().setDefaultStyleSheet(style_descriptive_table)

    def set_content(self, content: str) -> None:
        self.document().setHtml(content)

    def clear(self) -> None:
        self.document().clear()
