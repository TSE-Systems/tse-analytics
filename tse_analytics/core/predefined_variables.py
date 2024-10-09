from tse_analytics.core.data.shared import Variable, Aggregation


predefined_variables = {
    "ActiT": Variable("ActiT", "count", "Activity counts (counts per antenna change)", "uint64", Aggregation.SUM, False),
    "CO2": Variable("CO2", "%", "CO2 concentration", "float64", Aggregation.MEAN, False),
    "CO2L": Variable("CO2L", "ppm", "Ambient CO2 (actual value)", "float64", Aggregation.MEAN, False),
    "CenA": Variable("CenA", "count", "Total X and Y beam interruptions for central ambulatory movement", "uint64", Aggregation.SUM, False),
    "CenF": Variable("CenF", "count", "Total X and Y beam interruptions for central fine movement", "uint64", Aggregation.SUM, False),
    "CenT": Variable("CenT", "count", "Sum of total X beam interruptions and total Y beam interruptions in center zone (CenT = CenA + CenF)", "uint64", Aggregation.SUM, False),
    "ColTemp": Variable("ColTemp", "K", "Illumination color temperature (actual value)", "float64", Aggregation.MEAN, False),
    "DistD": Variable("DistD", "cm", "Distance traveled in the horizontal plane (XY) (differential)", "float64", Aggregation.SUM, False),
    "DistK": Variable("DistK", "cm", "Distance traveled in the horizontal plane (XY) (cumulative)", "float64", Aggregation.MAX, False),
    "Drink": Variable("Drink", "ml", "Drink consumption (differential)", "float64", Aggregation.SUM, False),
    "DrinkC": Variable("DrinkC", "ml", "Drink consumption (cumulative)", "float64", Aggregation.MAX, False),
    "Feed": Variable("Feed", "g", "Food consumption (differential)", "float64", Aggregation.SUM, False),
    "FeedC": Variable("FeedC", "g", "Food consumption (cumulative)", "float64", Aggregation.MAX, False),
    "Flow": Variable("Flow", "l/min", "Flow", "float64", Aggregation.MEAN, False),
    "H(1)": Variable("H(1)", "kcal/h/kg", "Heat production, normalized to total body weight", "float64", Aggregation.MEAN, False),
    "H(2)": Variable("H(2)", "kcal/h/kg", "Heat production, normalized to approximate lean body mass (75 % of bodyweight) for allometric scaling", "float64", Aggregation.MEAN, False),
    "H(3)": Variable("H(3)", "kcal/h", "Heat production, uncorrected values", "float64", Aggregation.MEAN, False),
    "HeartRate": Variable("HeartRate", "bpm", "Heart beats per minute", "float64", Aggregation.MEAN, False),
    "Hum": Variable("Hum", "%", "Relative humidity", "float64", Aggregation.MEAN, False),
    "HumC": Variable("HumC", "%", "Humidity climate chamber (actual value)", "float64", Aggregation.MEAN, False),
    "HumL": Variable("HumL", "%", "Ambient humidity (actual value)", "float64", Aggregation.MEAN, False),
    "Left": Variable("Left", "count", "Number of wheel rotations to the left", "float64", Aggregation.SUM, False),
    "LightC": Variable("LightC", "%", "Illumination intensity (actual value)", "float64", Aggregation.MEAN, False),
    "LightL": Variable("LightL", "lx", "Ambient brightness (actual value)", "float64", Aggregation.MEAN, False),
    "MotionL": Variable("MotionL", "s", "Motion detector for monitoring staff presence (summed up over time)", "float64", Aggregation.MAX, False),
    "NoiseL": Variable("NoiseL", "a.u.", "Noise level (actual value)", "float64", Aggregation.MEAN, False),
    "O2": Variable("O2", "%", "O2 concentration", "float64", Aggregation.MEAN, False),
    "PerA": Variable("PerA", "count", "Total X and Y beam interruptions for peripheral ambulatory movement", "uint64", Aggregation.SUM, False),
    "PerF": Variable("PerF", "count", "Total X and Y beam interruptions for peripheral fine movement", "uint64", Aggregation.SUM, False),
    "PerT": Variable("PerT", "count", "Sum of total X beam interruptions and total Y beam interruptions in periphery (PerT = PerA + PerF)", "uint64", Aggregation.SUM, False),
    "Press": Variable("Press", "hPa", "Air pressure", "float64", Aggregation.MEAN, False),
    "PressL": Variable("PressL", "Pa", "Ambient air pressure (actual value)", "float64", Aggregation.MEAN, False),
    "RER": Variable("RER", "a.u.", "Respiratory exchange rate", "float64", Aggregation.MEAN, False),
    "Ref.CO2": Variable("Ref.CO2", "%", "CO2 concentration in reference box", "float64", Aggregation.MEAN, False),
    "Ref.O2": Variable("Ref.O2", "%", "O2 concentration in reference box", "float64", Aggregation.MEAN, False),
    "Right": Variable("Right", "count", "Number of wheel rotations to the right", "float64", Aggregation.SUM, False),
    "S.Flow": Variable("S.Flow", "l/min", "Sample flow", "float64", Aggregation.MEAN, False),
    "Speed": Variable("Speed", "cm/s", "Average speed", "float64", Aggregation.MEAN, False),
    "SpeedM": Variable("SpeedM", "m/s", "Average running speed (distance covered per second)", "float64", Aggregation.MEAN, False),
    "TD": Variable("TD", "°C", "Reference value dew point (climate chamber only)", "float64", Aggregation.MEAN, False),
    "Temp": Variable("Temp", "°C", "Temperature", "float64", Aggregation.MEAN, False),
    "TempC": Variable("TempC", "°C", "Temperature climate chamber (actual value)", "float64", Aggregation.MEAN, False),
    "TempL": Variable("TempL", "°C", "Ambient temperature (actual value)", "float64", Aggregation.MEAN, False),
    "TempT": Variable("TempT", "°C", "Body temperature", "float64", Aggregation.MEAN, False),
    "VCO2(1)": Variable("VCO2(1)", "ml/h/kg", "CO2 production (V = volume), normalized to total body weight", "float64", Aggregation.MEAN, False),
    "VCO2(2)": Variable("VCO2(2)", "ml/h/kg", "CO2 production (V = volume), normalized to approximate lean body mass (75 % of bodyweight) for allometric scaling", "float64", Aggregation.MEAN, False),
    "VCO2(3)": Variable("VCO2(3)", "ml/h", "CO2 production (V = volume), uncorrected values", "float64", Aggregation.MEAN, False),
    "VO2(1)": Variable("VO2(1)", "ml/h/kg", "O2 consumption (V = volume), normalized to total body weight", "float64", Aggregation.MEAN, False),
    "VO2(2)": Variable("VO2(2)", "ml/h/kg", "O2 consumption (V = volume), normalized to approximate lean body mass (75 % of bodyweight) for allometric scaling", "float64", Aggregation.MEAN, False),
    "VO2(3)": Variable("VO2(3)", "ml/h", "O2 consumption (V = volume), uncorrected values", "float64", Aggregation.MEAN, False),
    "Weight": Variable("Weight", "g", "Body weight (absolute data)", "float64", Aggregation.MEAN, False),
    "XA": Variable("XA", "count", "X beam interruptions for ambulatory movement", "uint64", Aggregation.SUM, False),
    "XF": Variable("XF", "count", "X beam interruptions for fine movement", "uint64", Aggregation.SUM, False),
    "XT": Variable("XT", "count", "Total X beam interruptions (XT = XA + XF)", "uint64", Aggregation.SUM, False),
    "XT+YT": Variable("XT+YT", "count", "Sum of total X beam interruptions and total Y beam interruptions", "uint64", Aggregation.SUM, False),
    "YA": Variable("YA", "count", "Y beam interruptions for ambulatory movement", "uint64", Aggregation.SUM, False),
    "YF": Variable("YF", "count", "Y beam interruptions for fine movement", "uint64", Aggregation.SUM, False),
    "YT": Variable("YT", "count", "Total Y beam interruptions (YT = YA + YF)", "uint64", Aggregation.SUM, False),
    "Z": Variable("Z", "count", "Total Z beam interruptions", "uint64", Aggregation.SUM, False),
    "dCO2": Variable("dCO2", "%", "Difference in CO2 concentration between reference box and test box", "float64", Aggregation.MEAN, False),
    "dO2": Variable("dO2", "%", "Difference in O2 concentration between reference box and test box", "float64", Aggregation.MEAN, False),
}


def assign_predefined_values(variables: dict[str, Variable]) -> dict[str, Variable]:
    for variable_name, variable in variables.items():
        if variable_name in predefined_variables:
            predefined_variable = predefined_variables[variable_name]
            variable.unit = predefined_variable.unit
            variable.description = predefined_variable.description
            variable.aggregation = predefined_variable.aggregation
    return variables