import logging
from datetime import timedelta

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from tse_analytics.views.calo_details.calo_details_fitting_result import CaloDetailsFittingResult
from tse_analytics.views.calo_details.calo_details_settings import CaloDetailsSettings
from tse_analytics.views.calo_details.fitting_params import FittingParams


def calo_details_calculation_task(params: FittingParams):
    result = process_box(params)
    return result


def process_box(
    params: FittingParams,
) -> CaloDetailsFittingResult:
    # Calo Details Sample time [sec]
    sample_time = params.details_df.iloc[1].at["DateTime"] - params.details_df.iloc[0].at["DateTime"]

    bin_numbers = sorted(params.details_df["Bin"].unique().tolist())
    ref_bin_numbers = sorted(params.ref_details_df["Bin"].unique().tolist())

    # if len(ref_bin_numbers) > len(bin_numbers):
    #     print(ref_bin_numbers[-1])
    #     df_ref_box = df_ref_box.loc[df_ref_box["Bin"] != ref_bin_numbers[-1]]

    details_df = params.details_df.loc[params.details_df["Bin"] != bin_numbers[-1]]
    ref_details_df = params.ref_details_df.loc[params.ref_details_df["Bin"] != ref_bin_numbers[-1]]

    # details_df = params.details_df
    # ref_details_df = params.ref_details_df

    df_predicted_measurements = calculate_predicted_measurements(
        details_df,
        sample_time,
        params.calo_details_settings,
        False
    )

    df_ref_predicted_measurements = calculate_predicted_measurements(
        ref_details_df,
        sample_time,
        params.calo_details_settings,
        True
    )

    predicted_rer = []
    for bin_number in range(len(df_predicted_measurements)):
        ref_bin_data = df_ref_predicted_measurements[df_ref_predicted_measurements["Bin"] == bin_number]
        ref_o2 = ref_bin_data.iloc[0]['O2']
        ref_co2 = ref_bin_data.iloc[0]['CO2']

        bin_data = df_predicted_measurements[df_predicted_measurements["Bin"] == bin_number]
        o2 = bin_data.iloc[0]['O2']
        co2 = bin_data.iloc[0]['CO2']

        predicted_rer.append(
            calculate_rer(
                ref_o2,
                o2,
                ref_co2,
                co2,
                params.calo_details_settings.flow
            )
        )

    df_predicted_measurements['RER'] = predicted_rer

    measured_rer = params.general_df['RER']
    if len(predicted_rer) > len(measured_rer):
        predicted_rer = predicted_rer[0:-1]

    # Drop last bin
    bins = params.general_df['Bin'].iloc[0:-1].tolist()
    measured_rer = measured_rer.iloc[0:-1].tolist()
    predicted_rer = predicted_rer[0:-1]
    measured_o2 = params.general_df['O2'].iloc[0:-1].tolist()
    predicted_o2 = df_predicted_measurements['O2'][0:-1].tolist()
    measured_co2 = params.general_df['CO2'].iloc[0:-1].tolist()
    predicted_co2 = df_predicted_measurements['CO2'][0:-1].tolist()

    result_df = pd.DataFrame(data={
        "Bin": bins,
        "MeasuredO2": measured_o2,
        "PredictedO2": predicted_o2,
        "MeasuredCO2": measured_co2,
        "PredictedCO2": predicted_co2,
        "MeasuredRER": measured_rer,
        "PredictedRER": predicted_rer,
    })

    logging.info(f"Done! Box: {params.calo_details_box.box}, Ref box: {params.calo_details_box.ref_box}, Sample time: {sample_time}, Number of bins: {len(bin_numbers)}, Number of ref bins: {len(ref_bin_numbers)}")

    return CaloDetailsFittingResult(
        params.calo_details_box.box,
        params,
        result_df,
    )


def curve_fitting_func(x, a, b, c):
    return a * np.power(x, b) + c


def calculate_rer(o2_ref, o2, co2_ref, co2, flow):
    dO2 = o2_ref - o2
    dCO2 = co2 - co2_ref

    n2_ref = 100.0 - (o2_ref + co2_ref)  # -0.8
    if n2_ref < 0.001:
        n2_ref = 0.001  # Division durch Null vermeiden

    V1 = n2_ref * dO2
    V2 = o2_ref * (dO2 - dCO2)

    VO2 = flow * (V1 + V2) / n2_ref
    VCO2 = flow * dCO2

    rer = VCO2 / VO2
    return rer


def calculate_fit(
    df: pd.DataFrame,
    gas_name: str,
    number_of_iterations: int,
    bounds: tuple[tuple[float, float, float], tuple[float, float, float]]
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
    return popt, pcov


def calculate_predicted_measurements(
    df: pd.DataFrame,
    sample_time: timedelta,
    calo_details_settings: CaloDetailsSettings,
    is_ref: bool
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
            co2_bounds
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
    co2_bounds: tuple[tuple[float, float, float], tuple[float, float, float]]
):
    bin_df = df[df["Bin"] == bin_number]

    training_data_o2 = bin_df.iloc[start_offset_o2:end_offset_o2]
    training_data_co2 = bin_df.iloc[start_offset_co2:end_offset_co2]

    o2_popt, _ = calculate_fit(training_data_o2, "O2", iterations, o2_bounds)
    co2_popt, _ = calculate_fit(training_data_co2, "CO2", iterations, co2_bounds)

    predicted_o2 = curve_fitting_func(prediction_offset * sample_time.total_seconds(), *o2_popt)
    predicted_co2 = curve_fitting_func(prediction_offset * sample_time.total_seconds(), *co2_popt)

    return prediction_offset, predicted_o2, predicted_co2
