from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QToolButton, QMenu, QWidget

from tse_analytics.core import manager
from tse_analytics.core.layouts.layout_manager import LayoutManager
from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset
from tse_analytics.views.analysis.ancova.ancova_widget import AncovaWidget
from tse_analytics.views.analysis.correlation.correlation_widget import CorrelationWidget
from tse_analytics.views.analysis.distribution.distribution_widget import DistributionWidget
from tse_analytics.views.analysis.histogram.histogram_widget import HistogramWidget
from tse_analytics.views.analysis.matrixplot.matrixplot_widget import MatrixPlotWidget
from tse_analytics.views.analysis.mixed_anova.mixed_anova_widget import MixedAnovaWidget
from tse_analytics.views.analysis.n_way_anova.n_way_anova_widget import NWayAnovaWidget
from tse_analytics.views.analysis.normality.normality_widget import NormalityWidget
from tse_analytics.views.analysis.one_way_anova.one_way_anova_widget import OneWayAnovaWidget
from tse_analytics.views.analysis.pca.pca_widget import PcaWidget
from tse_analytics.views.analysis.regression.regression_widget import RegressionWidget
from tse_analytics.views.analysis.rm_anova.rm_anova_widget import RMAnovaWidget
from tse_analytics.views.analysis.timeseries_autocorrelation.timeseries_autocorrelation_widget import (
    TimeseriesAutocorrelationWidget,
)
from tse_analytics.views.analysis.timeseries_decomposition.timeseries_decomposition_widget import (
    TimeseriesDecompositionWidget,
)
from tse_analytics.views.analysis.tsne.tsne_widget import TsneWidget
from tse_analytics.views.data.data_plot_widget import DataPlotWidget
from tse_analytics.views.data.data_table_widget import DataTableWidget
from tse_analytics.views.reports.reports_widget import ReportsWidget


class AddWidgetButton(QToolButton):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setText("Add Widget")
        self.setIcon(QIcon(":/icons/icons8-database-import-16.png"))
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setEnabled(False)

        self.menu = QMenu("AddWidgetMenu", self)
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

        utils_menu = self.menu.addMenu("Utils")
        utils_menu.addAction(QIcon(":/icons/report.png"), "Report").triggered.connect(self._add_report_widget)

        self.intellicage_menu = self.menu.addMenu("IntelliCage")
        self.intellicage_menu.addAction(QIcon(":/icons/report.png"), "TEST").triggered.connect(self._add_report_widget)

        self.setMenu(self.menu)

    def set_state(self, state: bool) -> None:
        self.setEnabled(state)

    def set_dataset_menu(self, dataset) -> None:
        self.intellicage_menu.setEnabled(isinstance(dataset, IntelliCageDataset))

    def _add_data_table_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = DataTableWidget(dataset)
        LayoutManager.add_widget_to_central_area(dataset, widget, f"Table - {dataset.name}", QIcon(":/icons/table.png"))

    def _add_data_plot_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = DataPlotWidget(dataset)
        LayoutManager.add_widget_to_central_area(dataset, widget, f"Plot - {dataset.name}", QIcon(":/icons/plot.png"))

    def _add_histogram_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = HistogramWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/exploration.png")
        )

    def _add_distribution_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = DistributionWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/exploration.png")
        )

    def _add_normality_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = NormalityWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/exploration.png")
        )

    def _add_correlation_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = CorrelationWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/bivariate.png")
        )

    def _add_regression_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = RegressionWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/bivariate.png")
        )

    def _add_one_way_anova_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = OneWayAnovaWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/anova.png")
        )

    def _add_n_way_anova_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = NWayAnovaWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/anova.png")
        )

    def _add_rm_anova_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = RMAnovaWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/anova.png")
        )

    def _add_mixed_anova_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = MixedAnovaWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/anova.png")
        )

    def _add_ancova_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = AncovaWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/anova.png")
        )

    def _add_matrixplot_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = MatrixPlotWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/dimensionality.png")
        )

    def _add_pca_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = PcaWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/dimensionality.png")
        )

    def _add_tsne_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = TsneWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/dimensionality.png")
        )

    def _add_timeseries_decomposition_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = TimeseriesDecompositionWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/timeseries.png")
        )

    def _add_timeseries_autocorrelation_widget(self) -> None:
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = TimeseriesAutocorrelationWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/timeseries.png")
        )

    def _add_report_widget(self) -> None:
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = ReportsWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"Report - {dataset.name}", QIcon(":/icons/report.png")
        )
