from datetime import timedelta

import numpy as np
import pandas as pd
from lmfit import Parameters, minimize
from scipy.optimize import curve_fit

from tse_datatools.calo_details.calo_details_settings import CaloDetailsSettings


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


def calculate_fit(
    df: pd.DataFrame,
    gas_name: str,
    number_of_iterations: int,
    bounds: tuple[tuple[float, float, float], tuple[float, float, float]],
):
    xdata = df["Offset"]
    ydata = df[gas_name]

    popt, pcov = curve_fit(
        curve_fitting_func,
        method="trf",
        xdata=xdata,
        ydata=ydata,
        bounds=bounds,
        max_nfev=number_of_iterations,
    )
    return popt[0], popt[1], popt[2]


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

    for idx, bin in enumerate(bins):
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
