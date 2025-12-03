from dataclasses import dataclass
from io import BytesIO

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.figure import Figure
from pyqttoast import ToastPreset
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QToolBar, QVBoxLayout, QWidget
from scipy.stats import chi2

from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.data.shared import Animal
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_h_spacer_widget, get_html_image_from_figure
from tse_analytics.views.general.pdf.pdf_widget import PdfWidget
from tse_analytics.views.misc.animal_selector import AnimalSelector
from tse_analytics.views.misc.MplCanvas import MplCanvas


@dataclass
class TransitionsWidgetSettings:
    selected_animal: str = None


class TransitionsWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: TransitionsWidgetSettings = settings.value(self.__class__.__name__, TransitionsWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Transitions"

        self.datatable = datatable

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        toolbar.addSeparator()

        toolbar.addWidget(QLabel("Animal:"))
        self.animalSelector = AnimalSelector(toolbar)
        self.animalSelector.set_data(self.datatable.dataset, selected_animal=self._settings.selected_animal)
        toolbar.addWidget(self.animalSelector)

        # Insert toolbar to the widget
        self._layout.addWidget(toolbar)

        self.canvas = MplCanvas(self)
        self._layout.addWidget(self.canvas)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)
        toolbar.addAction("Generate PDF").triggered.connect(self._generate_pdf)

        self.pdf_widget: PdfWidget | None = None

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            TransitionsWidgetSettings(
                self.animalSelector.currentText(),
            ),
        )

    def _update(self):
        animal = self.animalSelector.get_selected_animal()
        columns = ["Timedelta", "Animal", "Corner"]
        df = self.datatable.active_df[columns]

        self.canvas.clear(False)
        axs = self.canvas.figure.subplots(2, 2)

        self._process_animal(
            df,
            animal,
            0.05,
            axs,
            self.canvas.figure,
        )

        self.canvas.draw()

    def _process_animal(
        self,
        df: pd.DataFrame,
        animal: Animal,
        alpha: float,
        axs: Axes,
        fig: Figure,
    ) -> None:
        df = df[df["Animal"] == animal.id].copy()
        if df.empty:
            make_toast(
                self,
                self.title,
                "No visits were recorded for this animal.",
                duration=2000,
                preset=ToastPreset.INFORMATION,
                show_duration_bar=True,
            ).show()
            return

        df.reset_index(drop=True, inplace=True)

        # Sort by timestamp to get the sequence of visits
        df.sort_values("Timedelta", inplace=True)

        # Create pairs of consecutive corners to analyze transitions
        df["NextCorner"] = df["Corner"].shift(-1)

        # Remove the last row as it doesn't have a next corner
        df = df.dropna(subset=["NextCorner"])

        # Convert corner numbers to integers if they aren't already
        df["NextCorner"] = df["NextCorner"].astype(int)

        # Create a transition matrix
        observed_matrix = pd.crosstab(df["Corner"], df["NextCorner"])

        # Calculate expected transition matrix
        # Expected counts = (row sum * column sum) / total
        row_sums = observed_matrix.sum(axis=1)
        col_sums = observed_matrix.sum(axis=0)
        total = observed_matrix.values.sum()

        expected = np.outer(row_sums, col_sums) / total
        expected_matrix = pd.DataFrame(expected, index=observed_matrix.index, columns=observed_matrix.columns)

        # Chi-square test for each cell
        chi_square = (observed_matrix - expected_matrix) ** 2 / expected_matrix

        # Calculate p-values
        p_values = pd.DataFrame(
            chi2.sf(chi_square.values, df=1),  # df=1 for each cell
            index=observed_matrix.index,
            columns=observed_matrix.columns,
        )

        # Highlight significant transitions
        # Create a mask for significant transitions (p < alpha)
        significant = p_values < alpha

        # Create a ratio matrix (observed/expected)
        ratio = observed_matrix / expected
        # Replace inf values with NaN
        ratio = ratio.replace([np.inf, -np.inf], np.nan)

        sns.heatmap(
            observed_matrix,
            annot=True,
            fmt="d",
            cmap="YlGnBu",
            linewidth=0.5,
            ax=axs[0, 0],
        )
        axs[0, 0].set(
            xlabel="To Corner",
            ylabel="From Corner",
            title="Observed transitions",
        )

        sns.heatmap(
            expected_matrix,
            annot=True,
            fmt=".1f",
            cmap="YlGnBu",
            linewidth=0.5,
            ax=axs[0, 1],
        )
        axs[0, 1].set(
            xlabel="To Corner",
            ylabel="From Corner",
            title="Expected transitions",
        )

        sns.heatmap(
            chi_square,
            annot=True,
            fmt=".2f",
            cmap="Reds",
            linewidth=0.5,
            ax=axs[1, 0],
        )
        axs[1, 0].set(
            xlabel="To Corner",
            ylabel="From Corner",
            title="Chi-Square Values",
        )

        # Plot the ratio with asterisks for significant transitions
        sns.heatmap(
            ratio,
            annot=significant.map(lambda x: "**" if x else ""),
            fmt="",
            cmap="RdBu_r",
            linewidth=0.5,
            center=1.0,
            ax=axs[1, 1],
        )
        axs[1, 1].set(
            xlabel="To Corner",
            ylabel="From Corner",
            title=f"Observed/Expected Ratio (** = p < {alpha})",
        )

        fig.suptitle(f"Chi-Square Analysis of Corner Transitions. Animal: {animal.id}")

        fig.tight_layout()

    def _add_report(self):
        manager.add_report(
            Report(
                self.datatable.dataset,
                self.title,
                get_html_image_from_figure(self.canvas.figure),
            )
        )

    def _generate_pdf(self):
        columns = ["Timedelta", "Animal", "Corner"]
        df = self.datatable.active_df[columns]

        pdf_bytes = BytesIO()

        with PdfPages(pdf_bytes) as pdf_pages:
            for animal in self.datatable.dataset.animals.values():
                if animal.enabled:
                    fig, axs = plt.subplots(2, 2, figsize=(9, 8))

                    self._process_animal(
                        df,
                        animal,
                        0.05,
                        axs,
                        fig,
                    )

                    # Add page to PDF file
                    pdf_pages.savefig(fig)
                    plt.close(fig)

        self.pdf_widget = PdfWidget(pdf_bytes)
        self.pdf_widget.show()
