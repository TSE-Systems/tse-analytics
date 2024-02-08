class CaloDetailsGasSettings:
    def __init__(
        self,
        gas_name: str,
        start_offset: int,
        end_offset: int,
        bounds: tuple[tuple[float, float, float], tuple[float, float, float]],
        ref_bounds: tuple[tuple[float, float, float], tuple[float, float, float]],
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
        co2_settings: CaloDetailsGasSettings,
    ):
        self.iterations = iterations
        self.prediction_offset = prediction_offset
        self.flow = flow
        self.o2_settings = o2_settings
        self.co2_settings = co2_settings


def get_default_settings():
    settings = CaloDetailsSettings(
        10000,
        50,
        0.5,
        CaloDetailsGasSettings(
            "O2",
            20,
            30,
            ((-3.75e12, -9.0, 0), (2.389e12, 0, 25)),
            ((-3.75e12, -9.0, 0), (2.389e12, 0, 25)),
        ),
        CaloDetailsGasSettings(
            "CO2", 20, 30, ((-3.75e12, -9.0, 0), (2.389e12, 0, 1)), ((-1.381e12, -8.806, 0), (2.525e12, 0, 0.1))
        ),
    )
    return settings
