from datetime import timedelta

import numpy as np
import pandas as pd
from lmfit import Parameters, minimize

# from scipy.optimize import curve_fit
from loguru import logger

from tse_datatools.calo_details.calo_details_fitting_result import CaloDetailsFittingResult
from tse_datatools.calo_details.calo_details_settings import CaloDetailsSettings
from tse_datatools.calo_details.fitting_params import FittingParams


def process_box(params: FittingParams) -> CaloDetailsFittingResult:
    # Calo Details Sample time [sec]
    sample_time = params.details_df.iloc[1].at["DateTime"] - params.details_df.iloc[0].at["DateTime"]

    bin_numbers = sorted(params.details_df["Bin"].unique().tolist())
    ref_bin_numbers = sorted(params.ref_details_df["Bin"].unique().tolist())

    # if len(ref_bin_numbers) > len(bin_numbers):
    #     print(ref_bin_numbers[-1])
    #     df_ref_box = df_ref_box.loc[df_ref_box["Bin"] != ref_bin_numbers[-1]]

    df_predicted_measurements = calculate_predicted_measurements(
        params.details_df, sample_time, params.calo_details_settings, False
    )

    df_ref_predicted_measurements = calculate_predicted_measurements(
        params.ref_details_df, sample_time, params.calo_details_settings, True
    )

    predicted_rer = []
    predicted_vo2 = []
    predicted_vco2 = []
    predicted_h = []
    for bin_number in range(len(df_predicted_measurements)):
        ref_bin_data = df_ref_predicted_measurements[df_ref_predicted_measurements["Bin"] == bin_number]
        ref_o2 = ref_bin_data.iloc[0]["O2"]
        ref_co2 = ref_bin_data.iloc[0]["CO2"]

        bin_data = df_predicted_measurements[df_predicted_measurements["Bin"] == bin_number]
        o2 = bin_data.iloc[0]["O2"]
        co2 = bin_data.iloc[0]["CO2"]

        rer, vo2, vco2, h = calculate_rer(ref_o2, o2, ref_co2, co2, params.calo_details_settings.flow)

        predicted_rer.append(rer)
        predicted_vo2.append(vo2)
        predicted_vco2.append(vco2)
        predicted_h.append(h)

    # measured_rer = params.general_df['RER']
    # if len(predicted_rer) > len(measured_rer):
    #     predicted_rer = predicted_rer[0:-1]

    bins = params.general_df["Bin"].tolist()

    measured_rer = params.general_df["RER"].tolist()
    measured_o2 = params.general_df["O2"].tolist()
    measured_ref_o2 = params.general_df["Ref.O2"].tolist() if "Ref.O2" in params.general_df.columns else None
    measured_co2 = params.general_df["CO2"].tolist()
    measured_ref_co2 = params.general_df["Ref.CO2"].tolist() if "Ref.CO2" in params.general_df.columns else None
    measured_vo2 = params.general_df["VO2(3)"].tolist()
    measured_vco2 = params.general_df["VCO2(3)"].tolist()
    measured_h = params.general_df["H(3)"].tolist()

    predicted_o2 = df_predicted_measurements["O2"].tolist()
    predicted_ref_o2 = df_ref_predicted_measurements["O2"].tolist()

    predicted_co2 = df_predicted_measurements["CO2"].tolist()
    predicted_ref_co2 = df_ref_predicted_measurements["CO2"].tolist()

    result_df = pd.DataFrame(
        data={
            "Bin": bins,
            "O2": measured_o2,
            "O2-p": predicted_o2,
            "CO2": measured_co2,
            "CO2-p": predicted_co2,
            "Ref.O2": measured_ref_o2,
            "Ref.O2-p": predicted_ref_o2,
            "Ref.CO2": measured_ref_co2,
            "Ref.CO2-p": predicted_ref_co2,
            "RER": measured_rer,
            "RER-p": predicted_rer,
            "VO2(3)": measured_vo2,
            "VO2(3)-p": predicted_vo2,
            "VCO2(3)": measured_vco2,
            "VCO2(3)-p": predicted_vco2,
            "H(3)": measured_h,
            "H(3)-p": predicted_h,
        }
    )

    logger.info(
        f"Done! Box: {params.calo_details_box.box}, Ref box: {params.calo_details_box.ref_box}, Sample time: {sample_time}, Number of bins: {len(bin_numbers)}, Number of ref bins: {len(ref_bin_numbers)}"
    )

    return CaloDetailsFittingResult(
        params.calo_details_box.box,
        params,
        result_df,
    )


def curve_fitting_func(x, a, b, c):
    return a * np.power(x, b) + c


def calculate_rer(o2_ref, o2, co2_ref, co2, flow):
    do2 = o2_ref - o2
    dco2 = co2 - co2_ref

    n2_ref = 100.0 - (o2_ref + co2_ref)  # -0.8
    if n2_ref < 0.001:
        n2_ref = 0.001  # Division durch Null vermeiden

    v1 = n2_ref * do2
    v2 = o2_ref * (do2 - dco2)

    vo2 = (flow * 1000.0 * 60) * (v1 + v2) / (n2_ref * 100.0)  # ml/h (LmGlob.pas - CalculateValues
    vco2 = (flow * 1000.0 * 60) * dco2 / 100.0

    cvo2 = 3.941
    cvco2 = 1.106

    h = (cvo2 * vo2 + cvco2 * vco2) / 1000.0

    rer = vco2 / vo2
    return rer, vo2, vco2, h


# def calculate_fit(
#     df: pd.DataFrame,
#     gas_name: str,
#     number_of_iterations: int,
#     bounds: tuple[tuple[float, float, float], tuple[float, float, float]],
# ):
#     xdata = df["Offset"]
#     ydata = df[gas_name]
#
#     popt, pcov = curve_fit(
#         curve_fitting_func,
#         method="trf",
#         xdata=xdata,
#         ydata=ydata,
#         bounds=bounds,
#         max_nfev=number_of_iterations,
#     )
#     return popt[0], popt[1], popt[2]


# Define the fitting function
def power_fitting_lmfit(params, x, y):
    a = params["a"]
    b = params["b"]
    c = params["c"]
    y_fit = curve_fitting_func(x, a, b, c)
    return y_fit - y


def calculate_fit_v2(
    df: pd.DataFrame,
    gas_name: str,
    number_of_iterations: int,
    bounds: tuple[tuple[float, float, float], tuple[float, float, float]],
):
    xdata = df["Offset"]
    ydata = df[gas_name]

    # Defining the various parameters
    params = Parameters()
    params.add("a", min=bounds[0][0], max=bounds[1][0])
    params.add("b", min=bounds[0][1], max=bounds[1][1])
    params.add("c", min=0.0)

    # Calling the minimize function. Args contains the x and y data.
    fitted_params = minimize(
        power_fitting_lmfit,
        params,
        args=(
            xdata,
            ydata,
        ),
        method="leastsq",
    )

    # Getting the fitted values
    a = fitted_params.params["a"].value
    b = fitted_params.params["b"].value
    c = fitted_params.params["c"].value

    return a, b, c


def calculate_predicted_measurements(
    df: pd.DataFrame, sample_time: timedelta, calo_details_settings: CaloDetailsSettings, is_ref: bool
):
    bins = df["Bin"].unique().tolist()
    offsets = []
    o2 = []
    co2 = []

    start_offset_o2 = calo_details_settings.o2_settings.start_offset
    end_offset_o2 = calo_details_settings.o2_settings.end_offset

    start_offset_co2 = calo_details_settings.co2_settings.start_offset
    end_offset_co2 = calo_details_settings.co2_settings.end_offset

    o2_bounds = calo_details_settings.o2_settings.ref_bounds if is_ref else calo_details_settings.o2_settings.bounds
    co2_bounds = calo_details_settings.co2_settings.ref_bounds if is_ref else calo_details_settings.co2_settings.bounds

    for _idx, bin in enumerate(bins):
        predicted_bin_measurements = calculate_predicted_bin_measurements(
            bin,
            df,
            sample_time,
            calo_details_settings.prediction_offset,
            start_offset_o2,
            end_offset_o2,
            start_offset_co2,
            end_offset_co2,
            calo_details_settings.iterations,
            o2_bounds,
            co2_bounds,
        )

        offsets.append(predicted_bin_measurements[0])
        o2.append(predicted_bin_measurements[1])
        co2.append(predicted_bin_measurements[2])

    calculated_df = pd.DataFrame(data={"Offset": offsets, "Bin": bins, "O2": o2, "CO2": co2})
    return calculated_df


def calculate_predicted_bin_measurements(
    bin_number: int,
    df: pd.DataFrame,
    sample_time: timedelta,
    prediction_offset: int,
    start_offset_o2: int,
    end_offset_o2: int,
    start_offset_co2: int,
    end_offset_co2: int,
    iterations: int,
    o2_bounds: tuple[tuple[float, float, float], tuple[float, float, float]],
    co2_bounds: tuple[tuple[float, float, float], tuple[float, float, float]],
):
    bin_df = df[df["Bin"] == bin_number]

    training_data_o2 = bin_df.iloc[start_offset_o2:end_offset_o2]
    training_data_co2 = bin_df.iloc[start_offset_co2:end_offset_co2]

    o2_a, o2_b, o2_c = calculate_fit_v2(training_data_o2, "O2", iterations, o2_bounds)
    co2_a, co2_b, co2_c = calculate_fit_v2(training_data_co2, "CO2", iterations, co2_bounds)

    predicted_o2 = curve_fitting_func(prediction_offset * sample_time.total_seconds(), o2_a, o2_b, o2_c)
    predicted_co2 = curve_fitting_func(prediction_offset * sample_time.total_seconds(), co2_a, co2_b, co2_c)

    return prediction_offset, predicted_o2, predicted_co2
