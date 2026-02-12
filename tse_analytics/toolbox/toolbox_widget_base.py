"""Base class for analysis toolbox widgets.

Provides common boilerplate: layout, settings persistence, toolbar with
Update/Add Report buttons, and a ReportEdit view.
"""

from typing import Any

from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QInputDialog, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.utils import get_h_spacer_widget
from tse_analytics.views.misc.report_edit import ReportEdit


class ToolboxWidgetBase(QWidget):
    """Base class for toolbox analysis widgets.

    Subclasses must:
    - Set ``title`` as a class attribute or pass it to ``__init__``.
    - Override ``_create_toolbar_items`` to add selectors/labels to the toolbar.
    - Override ``_get_settings_value`` to return the settings dataclass for persistence.
    - Override ``_update`` to implement the analysis logic.
    """

    title: str = ""

    def __init__(
        self,
        datatable: Datatable,
        settings_type: type,
        title: str | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        if title is not None:
            self.title = title

        self.datatable = datatable

        # Connect destructor to save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings = settings.value(self.__class__.__name__, settings_type())

        # Layout
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        self.toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.update_action = self.toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update")
        self.update_action.triggered.connect(self._update)
        self.toolbar.addSeparator()

        # Subclass hook: add custom toolbar items
        self._create_toolbar_items(self.toolbar)

        # Insert toolbar to the widget
        self._layout.addWidget(self.toolbar)

        # Report view
        self.report_view = ReportEdit(self)
        self._layout.addWidget(self.report_view)

        # Spacer + Add Report button
        self.toolbar.addWidget(get_h_spacer_widget(self.toolbar))
        self.toolbar.addAction("Add Report").triggered.connect(self._add_report)

    # ------------------------------------------------------------------
    # Subclass hooks
    # ------------------------------------------------------------------

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        """Override to add custom toolbar items (selectors, labels, etc.).

        Called during ``__init__`` after the Update button and separator,
        and before the toolbar is added to the layout.
        """

    def _get_settings_value(self) -> Any:
        """Override to return the current settings dataclass instance for saving.

        Must return an instance of the settings dataclass passed to ``__init__``.
        """
        raise NotImplementedError

    def _update(self) -> None:
        """Override to implement the analysis/update logic."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Default implementations
    # ------------------------------------------------------------------

    def _add_report(self) -> None:
        """Prompt for a report name and save the current report view HTML."""
        name, ok = QInputDialog.getText(
            self,
            "Report",
            "Please enter report name:",
            text=self.title,
        )
        if ok and name:
            manager.add_report(
                Report(
                    self.datatable.dataset,
                    name,
                    self.report_view.toHtml(),
                )
            )

    def _destroyed(self) -> None:
        """Save widget settings via QSettings on destruction."""
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            self._get_settings_value(),
        )
