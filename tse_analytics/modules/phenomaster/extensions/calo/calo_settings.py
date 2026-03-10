from dataclasses import dataclass


@dataclass
class CaloGasSettings:
    gas_name: str
    start_offset: int
    end_offset: int
    bounds: tuple[tuple[float, float, float], tuple[float, float, float]]
    ref_bounds: tuple[tuple[float, float, float], tuple[float, float, float]]


class CaloSettings:
    def __init__(
        self,
        iterations: int,
        prediction_offset: int,
        flow: float,
        o2_settings: CaloGasSettings,
        co2_settings: CaloGasSettings,
    ):
        self.iterations = iterations
        self.prediction_offset = prediction_offset
        self.flow = flow
        self.o2_settings = o2_settings
        self.co2_settings = co2_settings

    @staticmethod
    def get_default():
        settings = CaloSettings(
            10000,
            50,
            0.5,
            CaloGasSettings(
                "O2",
                20,
                30,
                ((-3.75e12, -9.0, 0), (2.389e12, 0, 25)),
                ((-3.75e12, -9.0, 0), (2.389e12, 0, 25)),
            ),
            CaloGasSettings(
                "CO2", 20, 30, ((-3.75e12, -9.0, 0), (2.389e12, 0, 1)), ((-1.381e12, -8.806, 0), (2.525e12, 0, 0.1))
            ),
        )
        return settings
