class CaloDetailsGasSettings:
    def __init__(
        self,
        gas_name: str,
        start_offset: int,
        end_offset: int,
        bounds: tuple[tuple[float, float, float], tuple[float, float, float]],
        ref_bounds: tuple[tuple[float, float, float], tuple[float, float, float]]
    ):
        self.gas_name = gas_name
        self.start_offset = start_offset
        self.end_offset = end_offset
        self.bounds = bounds
        self.ref_bounds = ref_bounds


class CaloDetailsSettings:
    def __init__(
        self,
        iterations: int,
        prediction_offset: int,
        flow: float,
        o2_settings: CaloDetailsGasSettings,
        co2_settings: CaloDetailsGasSettings
    ):
        self.iterations = iterations
        self.prediction_offset = prediction_offset
        self.flow = flow
        self.o2_settings = o2_settings
        self.co2_settings = co2_settings
