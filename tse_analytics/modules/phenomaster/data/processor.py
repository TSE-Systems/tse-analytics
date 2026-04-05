import pandas as pd

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.modules.phenomaster.extensions.calo.fitting_result import FittingResult


def append_fitting_results(
    dataset: Dataset,
    fitting_results: dict[int, FittingResult],
) -> None:
    """
    Append calorimetry fitting results to the dataset.

    This method adds predicted values from calorimetry fitting results to the main
    datatable. It creates new variables for predicted values if they don't exist,
    and updates the dataset with the fitting results.

    Args:
        fitting_results (dict[int, FittingResult]): Dictionary mapping box numbers
            to calorimetry fitting results
    """
    if len(fitting_results) > 0:
        main_datatable = dataset.datatables["Main"]
        df = main_datatable.df
        df["O2-p"] = pd.NA
        df["CO2-p"] = pd.NA
        df["VO2-p"] = pd.NA
        df["VCO2-p"] = pd.NA
        df["RER-p"] = pd.NA
        df["EE-p"] = pd.NA
        for result in fitting_results.values():
            for _index, row in result.df.iterrows():
                bin_number = row["Bin"]

                # TODO: TODO: check int -> str conversion for general table!
                df.loc[
                    df[(df["Box"] == result.box_number) & (df["Bin"] == bin_number)].index[0],
                    ["O2-p", "CO2-p", "VO2-p", "VCO2-p", "RER-p", "EE-p"],
                ] = [row["O2-p"], row["CO2-p"], row["VO2-p"], row["VCO2-p"], row["RER-p"], row["EE-p"]]

        if "O2-p" not in main_datatable.variables:
            main_datatable.variables["O2-p"] = Variable(
                "O2-p", "[%]", "Predicted O2", "float64", Aggregation.MEAN, False
            )
        if "CO2-p" not in main_datatable.variables:
            main_datatable.variables["CO2-p"] = Variable(
                "CO2-p", "[%]", "Predicted CO2", "float64", Aggregation.MEAN, False
            )
        if "VO2-p" not in main_datatable.variables:
            main_datatable.variables["VO2-p"] = Variable(
                "VO2-p", "[ml/h]", "Predicted VO2", "float64", Aggregation.MEAN, False
            )
        if "VCO2-p" not in main_datatable.variables:
            main_datatable.variables["VCO2-p"] = Variable(
                "VCO2-p", "[ml/h]", "Predicted VCO2", "float64", Aggregation.MEAN, False
            )
        if "RER-p" not in main_datatable.variables:
            main_datatable.variables["RER-p"] = Variable(
                "RER-p", "", "Predicted RER", "float64", Aggregation.MEAN, False
            )
        if "EE-p" not in main_datatable.variables:
            main_datatable.variables["EE-p"] = Variable(
                "EE-p", "[kcal/h]", "Predicted energy expenditure", "float64", Aggregation.MEAN, False
            )
