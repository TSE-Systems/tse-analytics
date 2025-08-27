from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QToolButton, QMenu, QWidget

from tse_analytics.core import manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.layouts.layout_manager import LayoutManager
from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset
from tse_analytics.modules.intellicage.views.toolbox.place_preference.place_preference_widget import (
    PlacePreferenceWidget,
)
from tse_analytics.modules.intellicage.views.toolbox.transitions.transitions_widget import TransitionsWidget
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset
from tse_analytics.toolbox.actogram.actogram_widget import ActogramWidget
from tse_analytics.toolbox.ancova.ancova_widget import AncovaWidget
from tse_analytics.toolbox.correlation.correlation_widget import CorrelationWidget
from tse_analytics.toolbox.distribution.distribution_widget import DistributionWidget
from tse_analytics.toolbox.histogram.histogram_widget import HistogramWidget
from tse_analytics.toolbox.matrixplot.matrixplot_widget import MatrixPlotWidget
from tse_analytics.toolbox.mixed_anova.mixed_anova_widget import MixedAnovaWidget
from tse_analytics.toolbox.n_way_anova.n_way_anova_widget import NWayAnovaWidget
from tse_analytics.toolbox.normality.normality_widget import NormalityWidget
from tse_analytics.toolbox.one_way_anova.one_way_anova_widget import OneWayAnovaWidget
from tse_analytics.toolbox.pca.pca_widget import PcaWidget
from tse_analytics.toolbox.periodogram.periodogram_widget import PeriodogramWidget
from tse_analytics.toolbox.regression.regression_widget import RegressionWidget
from tse_analytics.toolbox.reports.reports_widget import ReportsWidget
from tse_analytics.toolbox.rm_anova.rm_anova_widget import RMAnovaWidget
from tse_analytics.toolbox.timeseries_autocorrelation.timeseries_autocorrelation_widget import (
    TimeseriesAutocorrelationWidget,
)
from tse_analytics.toolbox.timeseries_decomposition.timeseries_decomposition_widget import (
    TimeseriesDecompositionWidget,
)
from tse_analytics.toolbox.tsne.tsne_widget import TsneWidget
from tse_analytics.toolbox.data_plot.data_plot_widget import DataPlotWidget
from tse_analytics.toolbox.data_table.data_table_widget import DataTableWidget


class ToolboxButton(QToolButton):
    """A button that provides access to various analysis tools.

    This button creates a dropdown menu with different categories of analysis tools
    that can be applied to the selected dataset and datatable.

    Attributes:
        menu: The main dropdown menu containing all tool categories.
        intellicage_menu: Submenu for IntelliCage-specific tools.
        intellicage_transitions_action: Action for the Transitions analysis tool.
        intellicage_place_preference_action: Action for the Place Preference analysis tool.
    """

    def __init__(self, parent: QWidget):
        """Initialize the toolbox button.

        Args:
            parent: The parent widget.
        """
        super().__init__(parent)

        self.setText("Toolbox")
        self.setIcon(QIcon(":/icons/icons8-toolbox-16.png"))
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setEnabled(False)

        self.menu = QMenu("ToolboxMenu", self)
        data_menu = self.menu.addMenu("Data")
        data_menu.addAction(QIcon(":/icons/table.png"), "Table").triggered.connect(self._add_data_table_widget)
        data_menu.addAction(QIcon(":/icons/plot.png"), "Plot").triggered.connect(self._add_data_plot_widget)

        exploration_menu = self.menu.addMenu("Exploration")
        exploration_menu.addAction(QIcon(":/icons/exploration.png"), "Histogram").triggered.connect(
            self._add_histogram_widget
        )
        exploration_menu.addAction(QIcon(":/icons/exploration.png"), "Distribution").triggered.connect(
            self._add_distribution_widget
        )
        exploration_menu.addAction(QIcon(":/icons/exploration.png"), "Normality").triggered.connect(
            self._add_normality_widget
        )

        bivariate_menu = self.menu.addMenu("Bivariate")
        bivariate_menu.addAction(QIcon(":/icons/bivariate.png"), "Correlation").triggered.connect(
            self._add_correlation_widget
        )
        bivariate_menu.addAction(QIcon(":/icons/bivariate.png"), "Regression").triggered.connect(
            self._add_regression_widget
        )

        anova_menu = self.menu.addMenu("ANOVA")
        anova_menu.addAction(QIcon(":/icons/anova.png"), "One-way ANOVA").triggered.connect(
            self._add_one_way_anova_widget
        )
        anova_menu.addAction(QIcon(":/icons/anova.png"), "N-way ANOVA").triggered.connect(self._add_n_way_anova_widget)
        anova_menu.addAction(QIcon(":/icons/anova.png"), "Repeated Measures ANOVA").triggered.connect(
            self._add_rm_anova_widget
        )
        anova_menu.addAction(QIcon(":/icons/anova.png"), "Mixed-design ANOVA").triggered.connect(
            self._add_mixed_anova_widget
        )
        anova_menu.addAction(QIcon(":/icons/anova.png"), "ANCOVA").triggered.connect(self._add_ancova_widget)

        dimensionality_menu = self.menu.addMenu("Dimensionality")
        dimensionality_menu.addAction(QIcon(":/icons/dimensionality.png"), "Matrix Plot").triggered.connect(
            self._add_matrixplot_widget
        )
        dimensionality_menu.addAction(QIcon(":/icons/dimensionality.png"), "PCA").triggered.connect(
            self._add_pca_widget
        )
        dimensionality_menu.addAction(QIcon(":/icons/dimensionality.png"), "tSNE").triggered.connect(
            self._add_tsne_widget
        )

        utils_menu = self.menu.addMenu("Time Series")
        utils_menu.addAction(QIcon(":/icons/timeseries.png"), "Decomposition").triggered.connect(
            self._add_timeseries_decomposition_widget
        )
        utils_menu.addAction(QIcon(":/icons/timeseries.png"), "Autocorrelation").triggered.connect(
            self._add_timeseries_autocorrelation_widget
        )

        circadian_menu = self.menu.addMenu("Circadian Analysis")
        circadian_menu.addAction(QIcon(":/icons/icons8-barcode-16.png"), "Actogram").triggered.connect(
            self._add_actogram_widget
        )
        circadian_menu.addAction(
            QIcon(":/icons/icons8-normal-distribution-histogram-16.png"), "Periodogram"
        ).triggered.connect(self._add_periodogram_widget)

        utils_menu = self.menu.addMenu("Utils")
        utils_menu.addAction(QIcon(":/icons/report.png"), "Report").triggered.connect(self._add_report_widget)

        self.intellicage_menu = self.menu.addMenu("IntelliCage")
        self.intellicage_transitions_action = self.intellicage_menu.addAction(
            QIcon(":/icons/icons8-transition-both-directions-16.png"), "Transitions"
        )
        self.intellicage_transitions_action.triggered.connect(self._add_transitions_widget)
        self.intellicage_place_preference_action = self.intellicage_menu.addAction(
            QIcon(":/icons/icons8-corner-16.png"), "Place Preference"
        )
        self.intellicage_place_preference_action.triggered.connect(self._add_place_preference_widget)

        self.setMenu(self.menu)

    def set_state(self, state: bool) -> None:
        """Enable or disable the toolbox button.

        Args:
            state: True to enable the button, False to disable it.
        """
        self.setEnabled(state)

    def set_enabled_actions(self, dataset: Dataset, datatable: Datatable | None) -> None:
        """Enable or disable specific actions based on the selected dataset and datatable.

        This method controls which analysis tools are available based on the type of dataset
        and datatable that are currently selected.

        Args:
            dataset: The currently selected dataset.
            datatable: The currently selected datatable, or None if no datatable is selected.
        """
        if isinstance(dataset, IntelliCageDataset) or isinstance(dataset, IntelliMazeDataset):
            self.intellicage_menu.setEnabled(True)
            self.intellicage_transitions_action.setEnabled(datatable is not None and datatable.name == "Visits")
            self.intellicage_place_preference_action.setEnabled(datatable is not None and datatable.name == "Visits")
        else:
            self.intellicage_menu.setEnabled(False)

    def _add_data_table_widget(self):
        """Add a data table widget to the central area.

        Gets the currently selected datatable and creates a DataTableWidget
        to display its contents in tabular form.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = DataTableWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"Table - {datatable.dataset.name}", QIcon(":/icons/table.png")
        )

    def _add_data_plot_widget(self):
        """Add a data plot widget to the central area.

        Gets the currently selected datatable and creates a DataPlotWidget
        to visualize its contents.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = DataPlotWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"Plot - {datatable.dataset.name}", QIcon(":/icons/plot.png")
        )

    def _add_histogram_widget(self):
        """Add a histogram widget to the central area.

        Gets the currently selected datatable and creates a HistogramWidget
        to visualize the distribution of data using histograms.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = HistogramWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"{widget.title} - {datatable.dataset.name}", QIcon(":/icons/exploration.png")
        )

    def _add_distribution_widget(self):
        """Add a distribution widget to the central area.

        Gets the currently selected datatable and creates a DistributionWidget
        to visualize the probability distribution of data.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = DistributionWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"{widget.title} - {datatable.dataset.name}", QIcon(":/icons/exploration.png")
        )

    def _add_normality_widget(self):
        """Add a normality test widget to the central area.

        Gets the currently selected datatable and creates a NormalityWidget
        to test and visualize whether the data follows a normal distribution.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = NormalityWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"{widget.title} - {datatable.dataset.name}", QIcon(":/icons/exploration.png")
        )

    def _add_correlation_widget(self):
        """Add a correlation analysis widget to the central area.

        Gets the currently selected datatable and creates a CorrelationWidget
        to analyze and visualize correlations between variables.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = CorrelationWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"{widget.title} - {datatable.dataset.name}", QIcon(":/icons/bivariate.png")
        )

    def _add_regression_widget(self):
        """Add a regression analysis widget to the central area.

        Gets the currently selected datatable and creates a RegressionWidget
        to perform and visualize regression analysis between variables.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = RegressionWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"{widget.title} - {datatable.dataset.name}", QIcon(":/icons/bivariate.png")
        )

    def _add_one_way_anova_widget(self):
        """Add a one-way ANOVA widget to the central area.

        Gets the currently selected datatable and creates a OneWayAnovaWidget
        to perform one-way analysis of variance.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = OneWayAnovaWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"{widget.title} - {datatable.dataset.name}", QIcon(":/icons/anova.png")
        )

    def _add_n_way_anova_widget(self):
        """Add an N-way ANOVA widget to the central area.

        Gets the currently selected datatable and creates a NWayAnovaWidget
        to perform multi-factor analysis of variance.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = NWayAnovaWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"{widget.title} - {datatable.dataset.name}", QIcon(":/icons/anova.png")
        )

    def _add_rm_anova_widget(self):
        """Add a repeated measures ANOVA widget to the central area.

        Gets the currently selected datatable and creates a RMAnovaWidget
        to perform repeated measures analysis of variance.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = RMAnovaWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"{widget.title} - {datatable.dataset.name}", QIcon(":/icons/anova.png")
        )

    def _add_mixed_anova_widget(self):
        """Add a mixed-design ANOVA widget to the central area.

        Gets the currently selected datatable and creates a MixedAnovaWidget
        to perform mixed between-within subjects analysis of variance.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = MixedAnovaWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"{widget.title} - {datatable.dataset.name}", QIcon(":/icons/anova.png")
        )

    def _add_ancova_widget(self):
        """Add an ANCOVA widget to the central area.

        Gets the currently selected datatable and creates an AncovaWidget
        to perform analysis of covariance.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = AncovaWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"{widget.title} - {datatable.dataset.name}", QIcon(":/icons/anova.png")
        )

    def _add_matrixplot_widget(self):
        """Add a matrix plot widget to the central area.

        Gets the currently selected datatable and creates a MatrixPlotWidget
        to visualize relationships between multiple variables in a matrix format.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = MatrixPlotWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"{widget.title} - {datatable.dataset.name}", QIcon(":/icons/dimensionality.png")
        )

    def _add_pca_widget(self):
        """Add a PCA widget to the central area.

        Gets the currently selected datatable and creates a PcaWidget
        to perform and visualize Principal Component Analysis.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = PcaWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"{widget.title} - {datatable.dataset.name}", QIcon(":/icons/dimensionality.png")
        )

    def _add_tsne_widget(self):
        """Add a t-SNE widget to the central area.

        Gets the currently selected datatable and creates a TsneWidget
        to perform and visualize t-Distributed Stochastic Neighbor Embedding.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = TsneWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"{widget.title} - {datatable.dataset.name}", QIcon(":/icons/dimensionality.png")
        )

    def _add_timeseries_decomposition_widget(self):
        """Add a time series decomposition widget to the central area.

        Gets the currently selected datatable and creates a TimeseriesDecompositionWidget
        to decompose time series data into trend, seasonal, and residual components.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = TimeseriesDecompositionWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"{widget.title} - {datatable.dataset.name}", QIcon(":/icons/timeseries.png")
        )

    def _add_timeseries_autocorrelation_widget(self) -> None:
        """Add a time series autocorrelation widget to the central area.

        Gets the currently selected datatable and creates a TimeseriesAutocorrelationWidget
        to analyze and visualize autocorrelation in time series data.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = TimeseriesAutocorrelationWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset, widget, f"{widget.title} - {datatable.dataset.name}", QIcon(":/icons/timeseries.png")
        )

    def _add_actogram_widget(self) -> None:
        """Add an actogram widget to the central area.

        Gets the currently selected datatable and creates an ActogramWidget
        to visualize activity patterns over time in a double-plotted format.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = ActogramWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset,
            widget,
            f"{widget.title} - {datatable.dataset.name}",
            QIcon(":/icons/icons8-barcode-16.png"),
        )

    def _add_periodogram_widget(self) -> None:
        """Add a periodogram widget to the central area.

        Gets the currently selected datatable and creates a PeriodogramWidget
        to analyze and visualize periodic patterns in time series data.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = PeriodogramWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset,
            widget,
            f"{widget.title} - {datatable.dataset.name}",
            QIcon(":/icons/icons8-normal-distribution-histogram-16.png"),
        )

    def _add_transitions_widget(self) -> None:
        """Add a transitions widget to the central area.

        Gets the currently selected datatable and creates a TransitionsWidget
        to analyze and visualize transitions between different locations in IntelliCage data.
        This widget is specific to IntelliCage datasets.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = TransitionsWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset,
            widget,
            f"{widget.title} - {datatable.dataset.name}",
            QIcon(":/icons/icons8-transition-both-directions-16.png"),
        )

    def _add_place_preference_widget(self) -> None:
        """Add a place preference widget to the central area.

        Gets the currently selected datatable and creates a PlacePreferenceWidget
        to analyze and visualize place preference behavior in IntelliCage data.
        This widget is specific to IntelliCage datasets.
        """
        datatable = manager.get_selected_datatable()
        if datatable is None:
            return
        widget = PlacePreferenceWidget(datatable)
        LayoutManager.add_widget_to_central_area(
            datatable.dataset,
            widget,
            f"{widget.title} - {datatable.dataset.name}",
            QIcon(":/icons/icons8-corner-16.png"),
        )

    def _add_report_widget(self) -> None:
        """Add a reports widget to the central area.

        Gets the currently selected dataset and creates a ReportsWidget
        to generate and display reports summarizing the dataset.
        """
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = ReportsWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"Report - {dataset.name}", QIcon(":/icons/report.png")
        )
