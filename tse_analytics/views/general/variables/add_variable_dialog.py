import pandas as pd
from PySide6.QtWidgets import QDialog, QWidget, QMessageBox

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Variable, Aggregation
from tse_analytics.views.general.variables.add_variable_dialog_ui import Ui_AddVariableDialog


class AddVariableDialog(QDialog):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_AddVariableDialog()
        self.ui.setupUi(self)

        self.datatable = datatable

        self.ui.aggregationComboBox.addItems(list(Aggregation))

        if len(self.datatable.dataset.animals) > 0:
            animal_properties = next(iter(self.datatable.dataset.animals.values())).properties
            self.ui.comboBoxAnimalProperty.addItems(list(animal_properties.keys()))

        self.ui.variableSelector.set_data(self.datatable.variables)

        self.ui.buttonBox.accepted.connect(self._accepted)

        self.ui.radioButtonOriginAnimalProperty.toggled.connect(
            lambda toggled: self._refresh_ui(True) if toggled else None
        )
        self.ui.radioButtonOriginCumulative.toggled.connect(
            lambda toggled: self._refresh_ui(False) if toggled else None
        )
        self.ui.radioButtonOriginDifferential.toggled.connect(
            lambda toggled: self._refresh_ui(False) if toggled else None
        )

    def _refresh_ui(self, show_animal_properties: bool):
        self.ui.groupBoxAnimalProperty.setEnabled(show_animal_properties)
        self.ui.groupBoxOriginVariable.setEnabled(not show_animal_properties)

    def _accepted(self) -> None:
        variable_name = self.ui.nameLineEdit.text()
        if variable_name == "":
            QMessageBox.warning(self, "Warning", "Variable name cannot be empty.")
            return

        if variable_name in self.datatable.variables:
            QMessageBox.warning(self, "Warning", "Variable name already exists.")
            return

        df = self.datatable.original_df.copy()

        if self.ui.radioButtonOriginAnimalProperty.isChecked():
            animal_property = self.ui.comboBoxAnimalProperty.currentText()

            # Add new variable column
            df[variable_name] = df["Animal"]
            values_map = {}
            for animal in self.datatable.dataset.animals.values():
                values_map[animal.id] = animal.properties[animal_property]
            df = df.replace({variable_name: values_map})

        elif self.ui.radioButtonOriginCumulative.isChecked():
            origin_variable = self.ui.variableSelector.get_selected_variable()
            df[variable_name] = df.groupby("Animal", observed=False)[origin_variable.name].transform(pd.Series.cumsum)
        elif self.ui.radioButtonOriginDifferential.isChecked():
            origin_variable = self.ui.variableSelector.get_selected_variable()
            df[variable_name] = df.groupby("Animal", observed=False)[origin_variable.name].transform(pd.Series.diff)
            # Fill NA values from the original column
            df[variable_name] = df[variable_name].fillna(df[origin_variable.name])

        try:
            # Set variable type
            df = df.astype({
                variable_name: "float64",
            })
        except ValueError:
            QMessageBox.warning(self, "Warning", "Variable type cannot be converted to float64.")
            return

        # Add new variable
        description = self.ui.descriptionLineEdit.text()
        unit = self.ui.unitLineEdit.text()
        aggregation = self.ui.aggregationComboBox.currentText()
        variable = Variable(
            name=variable_name,
            unit=unit,
            description=description,
            type="float64",
            aggregation=aggregation,
            remove_outliers=False,
        )
        self.datatable.variables[variable_name] = variable
        # Sort variables by name
        self.datatable.variables = dict(sorted(self.datatable.variables.items(), key=lambda x: x[0].lower()))

        # Update dataframes
        self.datatable.original_df = df
        self.datatable.refresh_active_df()
