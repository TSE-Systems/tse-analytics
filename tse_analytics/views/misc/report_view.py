from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView

html_template = """
<html>
<head>
<style type="text/css">
    body {{
        font-family: Segoe UI;
        font-size: 9pt;
    }}
    table {{
        font-size: 10pt;
        border-collapse: collapse;
        border: 1px solid silver;
        margin-bottom: 20px;
    }}
    caption {{
        font-size: 12pt;
        font-weight: bold;
    }}
    th {{
        padding: 5px;
        background: #dfebea;
    }}
    td {{
        padding: 5px;
    }}
    .horizontal-container {{
        display: flex;
        justify-content: space-between;
        margin: 20px;
    }}
</style>
</head>
<body>

{content}

</body>
</html>
"""


class ReportView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        # self.settings().setAttribute(self.settings().WebAttribute.PluginsEnabled, True)
        # self.settings().setAttribute(self.settings().WebAttribute.PdfViewerEnabled, True)

    def set_content(self, content: str) -> None:
        html = html_template.format(
            content=content,
        )
        self.setHtml(html)

    def clear(self) -> None:
        self.setHtml("")
