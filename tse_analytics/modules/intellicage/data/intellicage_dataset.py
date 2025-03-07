import pandas as pd

from tse_analytics.core.data.binning import BinningMode, TimeIntervalsBinningSettings
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.outliers import OutliersMode
from tse_analytics.core.data.pipeline.animal_filter_pipe_operator import filter_animals
from tse_analytics.core.data.pipeline.outliers_pipe_operator import process_outliers
from tse_analytics.core.data.pipeline.time_cycles_binning_pipe_operator import process_time_cycles_binning
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.pipeline.time_phases_binning_pipe_operator import process_time_phases_binning
from tse_analytics.core.data.shared import Animal, SplitMode, Variable
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.core.models.extension_tree_item import ExtensionTreeItem
from tse_analytics.modules.intellicage.data.intellicage_data import IntelliCageData


class IntelliCageDataset(Dataset):
    def __init__(
        self,
        name: str,
        path: str,
        meta: dict | list[dict],
        animals: dict[str, Animal],
    ):
        super().__init__(
            name,
            path,
            meta,
            animals,
            {},
            pd.DataFrame(),
            None,
        )

        self.intellicage_data: IntelliCageData | None = None

    @property
    def experiment_started(self) -> pd.Timestamp:
        return pd.to_datetime(self.meta["experiment"]["StartLocalTimeString"])

    @property
    def experiment_stopped(self) -> pd.Timestamp:
        return pd.to_datetime(self.meta["experiment"]["EndLocalTimeString"])

    def _preprocess_df(
        self,
        df: pd.DataFrame,
        variables: [str, Variable],
    ) -> pd.DataFrame:
        # Filter animals
        df = filter_animals(df, self.animals)

        # Outliers removal
        if self.outliers_settings.mode == OutliersMode.REMOVE:
            df = process_outliers(df, self.outliers_settings, variables)

        return df

    def get_current_df(
        self,
        variables: dict[str, Variable] | None = None,
        split_mode=SplitMode.ANIMAL,
        selected_factor_name: str | None = None,
        dropna=False,
    ) -> pd.DataFrame:
        if variables is not None:
            default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run"]
            factor_columns = list(self.factors)
            variable_columns = list(variables)
            result = self.active_df[default_columns + factor_columns + variable_columns].copy()
        else:
            variables = self.variables
            result = self.active_df.copy()

        result = self._preprocess_df(result, variables)

        # Binning
        if self.binning_settings.apply:
            match self.binning_settings.mode:
                case BinningMode.INTERVALS:
                    result = process_time_interval_binning(
                        result,
                        self.binning_settings.time_intervals_settings,
                        variables,
                    )
                case BinningMode.CYCLES:
                    result = process_time_cycles_binning(
                        result,
                        self.binning_settings.time_cycles_settings,
                        variables,
                    )
                case BinningMode.PHASES:
                    result = process_time_phases_binning(
                        result,
                        self.binning_settings.time_phases_settings,
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
        default_columns = ["DateTime", "Timedelta", "Run", "Animal", "Box"]
        factor_columns = list(self.factors)
        variable_columns = list(variables)
        result = self.active_df[default_columns + factor_columns + variable_columns].copy()

        result = self._preprocess_df(result, variables)

        # Binning
        if self.binning_settings.apply:
            match self.binning_settings.mode:
                case BinningMode.INTERVALS:
                    result = process_time_interval_binning(
                        result,
                        self.binning_settings.time_intervals_settings,
                        variables,
                    )
                case BinningMode.CYCLES:
                    result = process_time_cycles_binning(
                        result,
                        self.binning_settings.time_cycles_settings,
                        variables,
                    )
                case BinningMode.PHASES:
                    result = process_time_phases_binning(
                        result,
                        self.binning_settings.time_phases_settings,
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
        default_columns = ["DateTime", "Timedelta", "Run", "Animal", "Box"]
        factor_columns = list(self.factors)
        result = self.active_df[default_columns + factor_columns + [variable.name]].copy()

        variables = {variable.name: variable}

        result = self._preprocess_df(result, variables)

        # Binning
        if self.binning_settings.apply:
            # if split_mode == SplitMode.ANIMAL:
            #     calculate_errors = None
            result = process_time_interval_binning(
                result,
                self.binning_settings.time_intervals_settings,
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
        factor_columns = list(self.factors)
        result = self.active_df[default_columns + factor_columns].copy()

        variables = {variable.name: variable}

        result = self._preprocess_df(result, variables)

        match self.binning_settings.mode:
            case BinningMode.CYCLES:
                result = process_time_cycles_binning(
                    result,
                    self.binning_settings.time_cycles_settings,
                    variables,
                )
            case BinningMode.PHASES:
                result = process_time_phases_binning(
                    result,
                    self.binning_settings.time_phases_settings,
                    variables,
                )

        return result

    def get_anova_df(
        self,
        variables: dict[str, Variable],
    ) -> pd.DataFrame:
        default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]
        factor_columns = list(self.factors)
        variable_columns = list(variables)
        result = self.active_df[default_columns + factor_columns + variable_columns].copy()

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

    def add_children_tree_items(self, dataset_tree_item: DatasetTreeItem) -> None:
        if self.intellicage_data is not None:
            dataset_tree_item.add_child(ExtensionTreeItem(self.intellicage_data))
