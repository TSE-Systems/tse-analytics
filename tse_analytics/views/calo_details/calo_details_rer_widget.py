from typing import Optional

import pandas as pd
from PySide6.QtWidgets import QWidget
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT

from tse_analytics.views.calo_details.calo_details_fitting_result import CaloDetailsFittingResult
from tse_analytics.views.calo_details.calo_details_rer_widget_ui import Ui_CaloDetailsRerWidget


class CaloDetailsRerWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.ui = Ui_CaloDetailsRerWidget()
        self.ui.setupUi(self)

        self.ui.horizontalLayout.insertWidget(self.ui.horizontalLayout.count(), NavigationToolbar2QT(self.ui.canvas, self))

        self.fitting_result: Optional[CaloDetailsFittingResult] = None

    def set_data(self, fitting_result: CaloDetailsFittingResult):
        self.fitting_result = fitting_result

        if self.fitting_result is None:
            return

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        self.fitting_result.rer_df.plot(
            x="Bin",
            y="Measured",
            kind="line",
            title=f"RER [Box {self.fitting_result.box_number}]",
            label='Measured',
            ax=ax,
        )
        self.fitting_result.rer_df.plot(
            x="Bin",
            y="Predicted",
            kind="line",
            label='Predicted',
            ax=ax,
        )
        # ax.plot(
        #     self.fitting_result.rer_df["Bin"],
        #     self.fitting_result.rer_df["Predicted"],
        #     'r-',
        #     label='Predicted'
        # )

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
