import pandas as pd

from tse_datatools.calo_details.calo_details_fitting_result import CaloDetailsFittingResult
from tse_datatools.calo_details.calo_details_processor import calculate_predicted_measurements, calculate_rer
from tse_datatools.calo_details.fitting_params import FittingParams


class CaloDetailsWorker:
    _logger = None

    @staticmethod
    def set_logger(logger_):
        CaloDetailsWorker._logger = logger_

    def process_box(self, params: FittingParams) -> CaloDetailsFittingResult:
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

        self._logger.info(
            f"Done! Box: {params.calo_details_box.box}, Ref box: {params.calo_details_box.ref_box}, Sample time: {sample_time}, Number of bins: {len(bin_numbers)}, Number of ref bins: {len(ref_bin_numbers)}"
        )

        return CaloDetailsFittingResult(
            params.calo_details_box.box,
            params,
            result_df,
        )
