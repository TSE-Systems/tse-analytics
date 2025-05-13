import pandas as pd
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QWidget

from tse_analytics.modules.phenomaster.submodules.calo.calo_processor import calculate_fit_v2, curve_fitting_func
from tse_analytics.modules.phenomaster.submodules.calo.views.calo_settings_widget import CaloSettingsWidget
from tse_analytics.modules.phenomaster.submodules.calo.views.calo_test_fit_widget_ui import Ui_CaloTestFitWidget


class CaloTestFitWidget(QWidget):
    def __init__(self, settings_widget: CaloSettingsWidget, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_CaloTestFitWidget()
        self.ui.setupUi(self)

        self.ui.toolButtonFit.clicked.connect(self._test_fit)

        action = QAction("O2", self)
        action.triggered.connect(self._export_o2)
        self.ui.toolButtonExport.addAction(action)
        action = QAction("CO2", self)
        action.triggered.connect(self._export_co2)
        self.ui.toolButtonExport.addAction(action)

        self.ui.horizontalLayout.insertWidget(
            self.ui.horizontalLayout.count() - 1, NavigationToolbar2QT(self.ui.canvas, self)
        )

        self.settings_widget = settings_widget
        self.df: pd.DataFrame | None = None

    def set_data(self, df: pd.DataFrame):
        self.df = df

    def _export_o2(self):
        self._export_test_bin("O2")

    def _export_co2(self):
        self._export_test_bin("CO2")

    def _export_test_bin(self, gas_name: str):
        if self.df is None:
            return

        calo_settings = self.settings_widget.get_calo_settings()

        training_data = (
            self.df.iloc[calo_settings.o2_settings.start_offset : calo_settings.o2_settings.end_offset]
            if gas_name == "O2"
            else self.df.iloc[calo_settings.co2_settings.start_offset : calo_settings.co2_settings.end_offset]
        )
        training_data = training_data[["Offset", gas_name]]

        filename, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "TrainingData", "CSV Files (*.csv)")
        if filename:
            training_data.to_csv(filename, sep=";", index=False, header=False)

    def _test_fit(self):
        if self.df is None:
            return

        calo_settings = self.settings_widget.get_calo_settings()

        training_data_o2 = self.df.iloc[calo_settings.o2_settings.start_offset : calo_settings.o2_settings.end_offset]
        o2_a, o2_b, o2_c = calculate_fit_v2(
            training_data_o2, "O2", calo_settings.iterations, calo_settings.o2_settings.bounds
        )

        predicted_input_o2 = self.df["Offset"].iloc[
            calo_settings.o2_settings.start_offset : calo_settings.prediction_offset
        ]
        predicted_output_o2 = curve_fitting_func(self.df["Offset"], o2_a, o2_b, o2_c)
        predicted_output_o2 = predicted_output_o2.iloc[
            calo_settings.o2_settings.start_offset : calo_settings.prediction_offset
        ]

        training_data_co2 = self.df.iloc[
            calo_settings.co2_settings.start_offset : calo_settings.co2_settings.end_offset
        ]
        co2_a, co2_b, co2_c = calculate_fit_v2(
            training_data_co2, "CO2", calo_settings.iterations, calo_settings.co2_settings.bounds
        )

        predicted_input_co2 = self.df["Offset"].iloc[
            calo_settings.co2_settings.start_offset : calo_settings.prediction_offset
        ]
        predicted_output_co2 = curve_fitting_func(self.df["Offset"], co2_a, co2_b, co2_c)
        predicted_output_co2 = predicted_output_co2.iloc[
            calo_settings.co2_settings.start_offset : calo_settings.prediction_offset
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

        # O2 calculations
        o2_first = self.df["O2"].iloc[0]
        o2_last = self.df["O2"].iloc[-1]
        o2_t90 = 0
        o2_t95 = 0
        o2_t99 = 0

        o2_descending = o2_last < o2_first
        if o2_descending:
            o2_y90 = (o2_first - o2_last) * 0.9
            o2_y95 = (o2_first - o2_last) * 0.95
            o2_y99 = (o2_first - o2_last) * 0.99
            for _, row in self.df.iterrows():
                if row["O2"] < o2_first - o2_y90:
                    o2_t90 = row["Offset"]
                    break
            for _, row in self.df.iterrows():
                if row["O2"] < o2_first - o2_y95:
                    o2_t95 = row["Offset"]
                    break
            for _, row in self.df.iterrows():
                if row["O2"] < o2_first - o2_y99:
                    o2_t99 = row["Offset"]
                    break
        else:
            o2_y90 = (o2_last - o2_first) * 0.9
            o2_y95 = (o2_last - o2_first) * 0.95
            o2_y99 = (o2_last - o2_first) * 0.99
            for _, row in self.df.iterrows():
                if row["O2"] > o2_first + o2_y90:
                    o2_t90 = row["Offset"]
                    break
            for _, row in self.df.iterrows():
                if row["O2"] > o2_first + o2_y95:
                    o2_t95 = row["Offset"]
                    break
            for _, row in self.df.iterrows():
                if row["O2"] > o2_first + o2_y99:
                    o2_t99 = row["Offset"]
                    break

        # CO2 calculations
        co2_first = self.df["CO2"].iloc[0]
        co2_last = self.df["CO2"].iloc[-1]
        co2_t90 = 0
        co2_t95 = 0
        co2_t99 = 0

        co2_descending = co2_last < co2_first
        if co2_descending:
            co2_y90 = (co2_first - co2_last) * 0.9
            co2_y95 = (co2_first - co2_last) * 0.95
            co2_y99 = (co2_first - co2_last) * 0.99
            for _, row in self.df.iterrows():
                if row["CO2"] < co2_first - co2_y90:
                    co2_t90 = row["Offset"]
                    break
            for _, row in self.df.iterrows():
                if row["CO2"] < co2_first - co2_y95:
                    co2_t95 = row["Offset"]
                    break
            for _, row in self.df.iterrows():
                if row["CO2"] < co2_first - co2_y99:
                    co2_t99 = row["Offset"]
                    break
        else:
            co2_y90 = (co2_last - co2_first) * 0.9
            co2_y95 = (co2_last - co2_first) * 0.95
            co2_y99 = (co2_last - co2_first) * 0.99
            for _, row in self.df.iterrows():
                if row["CO2"] > co2_first + co2_y90:
                    co2_t90 = row["Offset"]
                    break
            for _, row in self.df.iterrows():
                if row["CO2"] > co2_first + co2_y95:
                    co2_t95 = row["Offset"]
                    break
            for _, row in self.df.iterrows():
                if row["CO2"] > co2_first + co2_y99:
                    co2_t99 = row["Offset"]
                    break

        self.ui.labelT90.setText(
            f"T90 [O2: {o2_t90}, CO2: {co2_t90}]; T95 [O2: {o2_t95}, CO2: {co2_t95}]; T99 [O2: {o2_t99}, CO2: {co2_t99}]"
        )

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
