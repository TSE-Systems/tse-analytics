import numpy as np
import pandas as pd

from tse_analytics.core.data.binning import BinningMode, BinningSettings, TimeIntervalsBinningSettings
from tse_analytics.core.data.outliers import OutliersMode, OutliersSettings
from tse_analytics.core.data.pipeline.animal_filter_pipe_operator import filter_animals
from tse_analytics.core.data.pipeline.outliers_pipe_operator import process_outliers
from tse_analytics.core.data.pipeline.time_cycles_binning_pipe_operator import process_time_cycles_binning
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.pipeline.time_phases_binning_pipe_operator import process_time_phases_binning
from tse_analytics.core.data.shared import Aggregation, Animal, SplitMode, Variable
from tse_analytics.core.messaging.messages import BinningMessage, DataChangedMessage, DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.modules.phenomaster.calo_details.calo_details_fitting_result import CaloDetailsFittingResult
from tse_analytics.modules.phenomaster.calo_details.data.calo_details import CaloDetails
from tse_analytics.modules.phenomaster.data.dataset import Dataset


class DataHub:
    def __init__(self, messenger: Messenger):
        self.messenger = messenger

        self.selected_dataset: Dataset | None = None

    def clear(self) -> None:
        self.selected_dataset = None
        self.messenger.broadcast(DatasetChangedMessage(self, None))

    def apply_binning(self, binning_settings: BinningSettings) -> None:
        if self.selected_dataset is None:
            return
        self.selected_dataset.binning_settings = binning_settings
        self.messenger.broadcast(BinningMessage(self, self.selected_dataset, binning_settings))

    def apply_outliers(self, settings: OutliersSettings) -> None:
        if self.selected_dataset is None:
            return
        self.selected_dataset.outliers_settings = settings
        self._broadcast_data_changed()

    def set_selected_dataset(self, dataset: Dataset) -> None:
        self.selected_dataset = dataset
        self.messenger.broadcast(DatasetChangedMessage(self, self.selected_dataset))

    def rename_animal(self, old_id: str, animal: Animal) -> None:
        self.selected_dataset.rename_animal(old_id, animal)
        self.messenger.broadcast(DatasetChangedMessage(self, self.selected_dataset))

    def set_selected_animals(self) -> None:
        self._broadcast_data_changed()

    def set_binning_operation(self) -> None:
        self._broadcast_data_changed()

    def _broadcast_data_changed(self) -> None:
        self.messenger.broadcast(DataChangedMessage(self, self.selected_dataset))

    def export_to_excel(self, path: str) -> None:
        if self.selected_dataset is not None:
            with pd.ExcelWriter(path) as writer:
                self.get_current_df().to_excel(writer, sheet_name="Data")

    def export_to_csv(self, path: str) -> None:
        if self.selected_dataset is not None:
            self.get_current_df().to_csv(path, sep=";", index=False)

    def append_fitting_results(
        self,
        calo_details: CaloDetails,
        fitting_results: dict[int, CaloDetailsFittingResult],
    ) -> None:
        if calo_details is not None and len(fitting_results) > 0:
            dataset = calo_details.dataset
            active_df = dataset.original_df
            active_df["O2-p"] = np.nan
            active_df["CO2-p"] = np.nan
            active_df["VO2(3)-p"] = np.nan
            active_df["VCO2(3)-p"] = np.nan
            active_df["RER-p"] = np.nan
            active_df["H(3)-p"] = np.nan
            for result in fitting_results.values():
                for _index, row in result.df.iterrows():
                    bin_number = row["Bin"]

                    # TODO: TODO: check int -> str conversion for general table!
                    active_df.loc[
                        active_df[(active_df["Box"] == result.box_number) & (active_df["Bin"] == bin_number)].index[0],
                        ["O2-p", "CO2-p", "VO2(3)-p", "VCO2(3)-p", "RER-p", "H(3)-p"],
                    ] = [row["O2-p"], row["CO2-p"], row["VO2(3)-p"], row["VCO2(3)-p"], row["RER-p"], row["H(3)-p"]]

            if "O2-p" not in dataset.variables:
                dataset.variables["O2-p"] = Variable("O2-p", "[%]", "Predicted O2", "float64", Aggregation.MEAN, False)
            if "CO2-p" not in dataset.variables:
                dataset.variables["CO2-p"] = Variable(
                    "CO2-p", "[%]", "Predicted CO2", "float64", Aggregation.MEAN, False
                )
            if "VO2(3)-p" not in dataset.variables:
                dataset.variables["VO2(3)-p"] = Variable(
                    "VO2(3)-p", "[ml/h]", "Predicted VO2(3)", "float64", Aggregation.MEAN, False
                )
            if "VCO2(3)-p" not in dataset.variables:
                dataset.variables["VCO2(3)-p"] = Variable(
                    "VCO2(3)-p", "[ml/h]", "Predicted VCO2(3)", "float64", Aggregation.MEAN, False
                )
            if "RER-p" not in dataset.variables:
                dataset.variables["RER-p"] = Variable("RER-p", "", "Predicted RER", "float64", Aggregation.MEAN, False)
            if "H(3)-p" not in dataset.variables:
                dataset.variables["H(3)-p"] = Variable(
                    "H(3)-p", "[kcal/h]", "Predicted H(3)", "float64", Aggregation.MEAN, False
                )
            dataset.refresh_active_df()
            self.set_selected_dataset(dataset)

    def _preprocess_df(
        self,
        df: pd.DataFrame,
        variables: [str, Variable],
    ) -> pd.DataFrame:
        # Filter animals
        df = filter_animals(df, self.selected_dataset.animals)

        # Outliers removal
        if self.selected_dataset.outliers_settings.mode == OutliersMode.REMOVE:
            df = process_outliers(df, self.selected_dataset.outliers_settings, variables)

        return df

    def _process_splitting(
        self,
        df: pd.DataFrame,
        split_mode: SplitMode,
        variables: dict[str, Variable],
        selected_factor_name: str,
        calculate_errors: str | None = None,
    ) -> pd.DataFrame:
        match split_mode:
            case SplitMode.ANIMAL:
                # No processing!
                return df
            case SplitMode.FACTOR:
                by = ["Bin", selected_factor_name]
            case SplitMode.RUN:
                by = ["Bin", "Run"]
            case _:  # Total split mode
                by = ["Bin"]

        agg = {}

        if "DateTime" in df.columns:
            agg["DateTime"] = "first"

        if "Timedelta" in df.columns:
            agg["Timedelta"] = "first"

        # TODO: use means only when aggregating in split modes!
        for variable in variables.values():
            agg[variable.name] = "mean"

        # Calculate error for timeline plot
        if calculate_errors is not None:
            var_name = list(variables.values())[0].name
            df["Error"] = df[var_name]
            agg["Error"] = calculate_errors

        if len(agg) == 0:
            return df

        result = df.groupby(by, dropna=False, observed=False).aggregate(agg)
        # result.sort_values(by, inplace=True)
        result.reset_index(inplace=True)
        return result

    def get_current_df(
        self,
        variables: dict[str, Variable] | None = None,
        split_mode=SplitMode.ANIMAL,
        selected_factor_name: str | None = None,
        dropna=False,
    ) -> pd.DataFrame:
        if variables is not None:
            default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]
            factor_columns = list(self.selected_dataset.factors)
            variable_columns = list(variables)
            result = self.selected_dataset.active_df[default_columns + factor_columns + variable_columns].copy()
        else:
            variables = self.selected_dataset.variables
            result = self.selected_dataset.active_df.copy()

        result = self._preprocess_df(result, variables)

        # Binning
        if self.selected_dataset.binning_settings.apply:
            match self.selected_dataset.binning_settings.mode:
                case BinningMode.INTERVALS:
                    result = process_time_interval_binning(
                        result,
                        self.selected_dataset.binning_settings.time_intervals_settings,
                        variables,
                    )
                case BinningMode.CYCLES:
                    result = process_time_cycles_binning(
                        result,
                        self.selected_dataset.binning_settings.time_cycles_settings,
                        variables,
                    )
                case BinningMode.PHASES:
                    result = process_time_phases_binning(
                        result,
                        self.selected_dataset.binning_settings.time_phases_settings,
                        variables,
                    )

        # Splitting
        result = self._process_splitting(
            result,
            split_mode,
            variables,
            selected_factor_name,
        )

        # TODO: should or should not?
        if dropna:
            result.dropna(inplace=True)

        return result

    def get_data_table_df(
        self,
        variables: dict[str, Variable],
        split_mode: SplitMode,
        selected_factor_name: str,
    ) -> pd.DataFrame:
        default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]
        factor_columns = list(self.selected_dataset.factors)
        variable_columns = list(variables)
        result = self.selected_dataset.active_df[default_columns + factor_columns + variable_columns].copy()

        result = self._preprocess_df(result, variables)

        # Binning
        if self.selected_dataset.binning_settings.apply:
            match self.selected_dataset.binning_settings.mode:
                case BinningMode.INTERVALS:
                    result = process_time_interval_binning(
                        result,
                        self.selected_dataset.binning_settings.time_intervals_settings,
                        variables,
                    )
                case BinningMode.CYCLES:
                    result = process_time_cycles_binning(
                        result,
                        self.selected_dataset.binning_settings.time_cycles_settings,
                        variables,
                    )
                case BinningMode.PHASES:
                    result = process_time_phases_binning(
                        result,
                        self.selected_dataset.binning_settings.time_phases_settings,
                        variables,
                    )

        # Splitting
        result = self._process_splitting(
            result,
            split_mode,
            variables,
            selected_factor_name,
        )

        return result

    def get_timeline_plot_df(
        self,
        variable: Variable,
        split_mode: SplitMode,
        selected_factor_name: str,
        calculate_errors: str | None,
    ) -> pd.DataFrame:
        default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]
        factor_columns = list(self.selected_dataset.factors)
        result = self.selected_dataset.active_df[default_columns + factor_columns + [variable.name]].copy()

        variables = {variable.name: variable}

        result = self._preprocess_df(result, variables)

        # Binning
        if self.selected_dataset.binning_settings.apply:
            # if split_mode == SplitMode.ANIMAL:
            #     calculate_errors = None
            result = process_time_interval_binning(
                result,
                self.selected_dataset.binning_settings.time_intervals_settings,
                variables,
                calculate_errors,
            )

        # Splitting
        result = self._process_splitting(
            result,
            split_mode,
            variables,
            selected_factor_name,
            calculate_errors,
        )

        return result

    def get_bar_plot_df(
        self,
        variable: Variable,
    ) -> pd.DataFrame:
        default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin", variable.name]
        factor_columns = list(self.selected_dataset.factors)
        result = self.selected_dataset.active_df[default_columns + factor_columns].copy()

        variables = {variable.name: variable}

        result = self._preprocess_df(result, variables)

        match self.selected_dataset.binning_settings.mode:
            case BinningMode.CYCLES:
                result = process_time_cycles_binning(
                    result,
                    self.selected_dataset.binning_settings.time_cycles_settings,
                    variables,
                )
            case BinningMode.PHASES:
                result = process_time_phases_binning(
                    result,
                    self.selected_dataset.binning_settings.time_phases_settings,
                    variables,
                )

        return result

    def get_anova_df(
        self,
        variables: dict[str, Variable],
    ) -> pd.DataFrame:
        default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]
        factor_columns = list(self.selected_dataset.factors)
        variable_columns = list(variables)
        result = self.selected_dataset.active_df[default_columns + factor_columns + variable_columns].copy()

        result = self._preprocess_df(result, variables)

        # Binning
        result = process_time_interval_binning(
            result,
            TimeIntervalsBinningSettings("day", 365),
            variables,
        )

        # TODO: should or should not?
        result.dropna(inplace=True)

        return result

    def get_timeseries_df(
        self,
        animal: Animal,
        variable: Variable,
    ) -> pd.DataFrame:
        columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", variable.name]
        df = self.selected_dataset.active_df[columns].copy()
        df = df[df["Animal"] == animal.id]
        df.reset_index(drop=True, inplace=True)

        variables = {variable.name: variable}

        result = self._preprocess_df(df, variables)

        # Binning
        if self.selected_dataset.binning_settings.apply:
            result = process_time_interval_binning(
                result,
                self.selected_dataset.binning_settings.time_intervals_settings,
                variables,
            )

        return result
