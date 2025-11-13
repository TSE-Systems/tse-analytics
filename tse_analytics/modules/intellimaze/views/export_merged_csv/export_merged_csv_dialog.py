import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFileDialog, QListWidgetItem, QWidget

from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset
from tse_analytics.modules.intellimaze.views.export_merged_csv.export_merged_csv_dialog_ui import (
    Ui_ExportMergedCsvDialog,
)


class ExportMergedCsvDialog(QDialog):
    def __init__(self, dataset: IntelliMazeDataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_ExportMergedCsvDialog()
        self.ui.setupUi(self)

        self.dataset = dataset

        for extension_name in dataset.extensions_data.keys():
            item = QListWidgetItem(extension_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.ui.listWidgetExtensions.addItem(item)

        self.ui.buttonBox.accepted.connect(self._export)

    def _export(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "", "CSV Files (*.csv)")
        if filename:
            if self.ui.radioButtonDelimiterSemicolon.isChecked():
                delimiter = ";"
            elif self.ui.radioButtonDelimiterComma.isChecked():
                delimiter = ","
            else:
                delimiter = "\t"

            export_registrations = self.ui.checkBoxExportRegistrations.isChecked()
            export_variables = self.ui.checkBoxExportVariables.isChecked()

            extension_csv_data = {}
            for index in range(self.ui.listWidgetExtensions.count()):
                item = self.ui.listWidgetExtensions.item(index)
                if item.checkState() == Qt.CheckState.Checked:
                    extension_name, csv_data = self.dataset.extensions_data[item.text()].get_csv_data(
                        export_registrations,
                        export_variables,
                    )
                    if len(csv_data) > 0:
                        extension_csv_data[extension_name] = csv_data

            if self.ui.radioButtonFormatNew.isChecked():
                self._export_new_format(extension_csv_data, filename, delimiter)
            else:
                self._export_old_format(extension_csv_data, filename, delimiter)

    def _export_new_format(
        self,
        extension_csv_data: dict[str, dict[str, pd.DataFrame]],
        filename: str,
        delimiter: str,
    ) -> None:
        result_df = pd.DataFrame()

        for _, csv_data in extension_csv_data.items():
            for _, df in csv_data.items():
                result_df = pd.concat([result_df, df])

        result_df.sort_values(["DateTime"], inplace=True)

        result_df.to_csv(
            filename,
            sep=delimiter,
            index=False,
            quoting=None,
        )

    def _export_old_format(
        self,
        extension_csv_data: dict[str, dict[str, pd.DataFrame]],
        filename: str,
        delimiter: str,
    ) -> None:
        core_headers_set = {"DateTime", "DeviceType", "DeviceId", "AnimalName", "AnimalTag", "TableType"}
        headers3 = list(core_headers_set)
        commonColumnNumber = len(headers3)
        headers2 = ["" for i in range(commonColumnNumber)]
        headers1 = ["" for i in range(commonColumnNumber)]

        # Estimate number of columns
        for extension_name, csv_data in extension_csv_data.items():
            for tableName, df in csv_data.items():
                df_headers = list(set(df.columns.values.tolist()) - core_headers_set)
                headers3 = headers3 + df_headers

                subHeaders = [tableName for i in range(len(df_headers))]
                headers2 = headers2 + subHeaders

                subSubHeaders = [extension_name for i in range(len(df_headers))]
                headers1 = headers1 + subSubHeaders

        numberOfColumns = len(headers3)
        fieldsOffset = 0
        csvDataRows: list[list[str]] = []
        for _, csv_data in extension_csv_data.items():
            for _, df in csv_data.items():
                field_names = list(set(df.columns.values.tolist()) - core_headers_set)
                headerLength = len(field_names)
                preContent = ["" for i in range(fieldsOffset)]
                postContent = ["" for i in range(numberOfColumns - fieldsOffset - commonColumnNumber - headerLength)]

                for _, row in df.iterrows():
                    start = [
                        str(row["DateTime"]),
                        row["DeviceType"],
                        row["DeviceId"],
                        row["AnimalName"],
                        row["AnimalTag"],
                        row["TableType"],
                    ]
                    fields = [
                        str(row[field_name]) if row[field_name] == row[field_name] else "" for field_name in field_names
                    ]
                    csvDataRows.append(start + preContent + fields + postContent)

                fieldsOffset = fieldsOffset + headerLength

        new_list = sorted(csvDataRows, key=lambda x: x[0], reverse=False)
        lines = [f"{delimiter.join(items)}\n" for items in new_list]

        with open(filename, "w") as f:
            f.writelines([
                f"{delimiter.join(headers1)}\n",
                f"{delimiter.join(headers2)}\n",
                f"{delimiter.join(headers3)}\n",
            ])
            f.writelines(lines)
