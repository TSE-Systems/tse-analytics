import timeit

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QCloseEvent, QIcon, QKeyEvent
from PySide6.QtWidgets import QDialog, QWidget
from loguru import logger

from tse_analytics.modules.phenomaster.data.meal_details import MealDetails
from tse_analytics.modules.phenomaster.data.meal_details_box import MealDetailsBox
from tse_analytics.modules.phenomaster.meal_details.meal_details_settings import get_default_settings
from tse_analytics.views.meal_details.meal_details_box_selector import MealDetailsBoxSelector
from tse_analytics.views.meal_details.meal_details_dialog_ui import Ui_MealDetailsDialog
from tse_analytics.views.meal_details.meal_details_plot_widget import MealDetailsPlotWidget
from tse_analytics.views.meal_details.meal_details_settings_widget import MealDetailsSettingsWidget
from tse_analytics.views.meal_details.meal_details_table_view import MealDetailsTableView
from tse_analytics.views.misc.toast import Toast


class MealDetailsDialog(QDialog):
    """MealDetails Dialog"""

    def __init__(self, meal_details: MealDetails, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_MealDetailsDialog()
        self.ui.setupUi(self)

        settings = QSettings()
        self.restoreGeometry(settings.value("MealDetailsDialog/Geometry"))

        self.meal_details = meal_details

        self.meal_details_table_view = MealDetailsTableView()
        self.meal_details_table_view.set_data(meal_details.raw_df)
        self.ui.tabWidget.addTab(self.meal_details_table_view, "Data")

        self.meal_details_plot_widget = MealDetailsPlotWidget()
        self.meal_details_plot_widget.set_variables(meal_details.variables)
        # self.calo_details_plot_widget.set_data(calo_details.raw_df)
        self.ui.tabWidget.addTab(self.meal_details_plot_widget, "Plot")

        self.ui.toolBox.removeItem(0)

        self.ui.toolButtonCalculate.clicked.connect(self.__run_calculate)
        self.ui.toolButtonResetSettings.clicked.connect(self.__reset_settings)

        self.meal_details_box_selector = MealDetailsBoxSelector(self.__filter_boxes)
        self.meal_details_box_selector.set_data(meal_details.dataset)
        self.ui.toolBox.addItem(self.meal_details_box_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Boxes")

        try:
            meal_details_settings = settings.value("MealDetailsSettings", get_default_settings())
        except Exception:
            meal_details_settings = get_default_settings()

        self.meal_details_settings_widget = MealDetailsSettingsWidget()
        self.meal_details_settings_widget.set_settings(meal_details_settings)
        self.meal_details_settings_widget.set_data(self.meal_details.dataset)
        self.ui.toolBox.addItem(self.meal_details_settings_widget, QIcon(":/icons/icons8-dog-tag-16.png"), "Settings")

        self.ui.splitter.setStretchFactor(0, 3)

        self.selected_boxes: list[MealDetailsBox] = []

    def __filter_boxes(self, selected_boxes: list[MealDetailsBox]):
        self.selected_boxes = selected_boxes
        self.__filter()

    def __filter(self):
        df = self.meal_details.raw_df

        if len(self.selected_boxes) > 0:
            box_numbers = [b.box for b in self.selected_boxes]
            df = df[df["Box"].isin(box_numbers)]

        self.meal_details_table_view.set_data(df)
        self.meal_details_plot_widget.set_data(df)

    def __reset_settings(self):
        meal_details_settings = get_default_settings()
        self.meal_details_settings_widget.set_settings(meal_details_settings)

    def __run_calculate(self):
        meal_details_settings = self.meal_details_settings_widget.get_meal_details_settings()
        tic = timeit.default_timer()
        logger.info(f"Processing complete: {timeit.default_timer() - tic} sec")
        Toast(text="Processing complete.", parent=self, duration=4000).show_toast()

    def hideEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("MealDetailsDialog/Geometry", self.saveGeometry())

        meal_details_settings = self.meal_details_settings_widget.get_meal_details_settings()
        # settings.setValue("MealDetailsSettings", calo_details_settings)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
