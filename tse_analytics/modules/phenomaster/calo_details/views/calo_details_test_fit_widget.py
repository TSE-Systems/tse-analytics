import pandas as pd
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QDialog, QFileDialog, QWidget

from tse_analytics.modules.phenomaster.calo_details.calo_details_processor import calculate_fit_v2, curve_fitting_func
from tse_analytics.modules.phenomaster.calo_details.views.calo_details_settings_widget import CaloDetailsSettingsWidget
from tse_analytics.modules.phenomaster.calo_details.views.calo_details_test_fit_widget_ui import Ui_CaloDetailsTestFitWidget


class CaloDetailsTestFitWidget(QWidget):
    def __init__(self, settings_widget: CaloDetailsSettingsWidget, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_CaloDetailsTestFitWidget()
        self.ui.setupUi(self)

        self.ui.toolButtonFit.clicked.connect(self.__test_fit)

        action = QAction("O2", self)
        action.triggered.connect(self.__export_o2)
        self.ui.toolButtonExport.addAction(action)
        action = QAction("CO2", self)
        action.triggered.connect(self.__export_co2)
        self.ui.toolButtonExport.addAction(action)

        self.ui.horizontalLayout.insertWidget(
            self.ui.horizontalLayout.count() - 1, NavigationToolbar2QT(self.ui.canvas, self)
        )

        self.settings_widget = settings_widget
        self.df: pd.DataFrame | None = None

    def set_data(self, df: pd.DataFrame):
        self.df = df

    def __export_o2(self):
        self.__export_test_bin("O2")

    def __export_co2(self):
        self.__export_test_bin("CO2")

    def __export_test_bin(self, gas_name: str):
        if self.df is None:
            return

        calo_details_settings = self.settings_widget.get_calo_details_settings()

        training_data = (
            self.df.iloc[calo_details_settings.o2_settings.start_offset : calo_details_settings.o2_settings.end_offset]
            if gas_name == "O2"
            else self.df.iloc[
                calo_details_settings.co2_settings.start_offset : calo_details_settings.co2_settings.end_offset
            ]
        )
        training_data = training_data[["Offset", gas_name]]

        dialog = QFileDialog(self)
        dialog.setDefaultSuffix(".csv")
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setWindowTitle("Export to CSV")
        dialog.setNameFilter("CSV Files (*.csv)")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            training_data.to_csv(dialog.selectedFiles()[0], sep=";", index=False, header=False)

    def __test_fit(self):
        if self.df is None:
            return

        calo_details_settings = self.settings_widget.get_calo_details_settings()

        training_data_o2 = self.df.iloc[
            calo_details_settings.o2_settings.start_offset : calo_details_settings.o2_settings.end_offset
        ]
        o2_a, o2_b, o2_c = calculate_fit_v2(
            training_data_o2, "O2", calo_details_settings.iterations, calo_details_settings.o2_settings.bounds
        )

        predicted_input_o2 = self.df["Offset"].iloc[
            calo_details_settings.o2_settings.start_offset : calo_details_settings.prediction_offset
        ]
        predicted_output_o2 = curve_fitting_func(self.df["Offset"], o2_a, o2_b, o2_c)
        predicted_output_o2 = predicted_output_o2.iloc[
            calo_details_settings.o2_settings.start_offset : calo_details_settings.prediction_offset
        ]

        training_data_co2 = self.df.iloc[
            calo_details_settings.co2_settings.start_offset : calo_details_settings.co2_settings.end_offset
        ]
        co2_a, co2_b, co2_c = calculate_fit_v2(
            training_data_co2, "CO2", calo_details_settings.iterations, calo_details_settings.co2_settings.bounds
        )

        predicted_input_co2 = self.df["Offset"].iloc[
            calo_details_settings.co2_settings.start_offset : calo_details_settings.prediction_offset
        ]
        predicted_output_co2 = curve_fitting_func(self.df["Offset"], co2_a, co2_b, co2_c)
        predicted_output_co2 = predicted_output_co2.iloc[
            calo_details_settings.co2_settings.start_offset : calo_details_settings.prediction_offset
        ]

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.subplots(2)

        self.df.plot(
            x="Offset",
            y="O2",
            kind="line",
            title="O2",
            ax=ax[0],
            label="Measured",
        )
        ax[0].plot(predicted_input_o2, predicted_output_o2, "r-", label="Predicted")

        self.df.plot(
            x="Offset",
            y="CO2",
            kind="line",
            title="CO2",
            ax=ax[1],
            label="Measured",
        )
        ax[1].plot(predicted_input_co2, predicted_output_co2, "r-", label="Predicted")

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
