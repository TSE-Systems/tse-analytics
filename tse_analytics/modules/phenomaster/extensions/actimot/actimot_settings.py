class ActimotSettings:
    def __init__(
        self,
        use_smooting: bool,
        smoothing_window_size: int | None,
        smoothing_polynomial_order: int,
    ):
        self.use_smooting = use_smooting
        self.smoothing_window_size = smoothing_window_size
        self.smoothing_polynomial_order = smoothing_polynomial_order

    @staticmethod
    def get_default():
        settings = ActimotSettings(
            use_smooting=False,
            smoothing_window_size=None,
            smoothing_polynomial_order=3,
        )
        return settings
