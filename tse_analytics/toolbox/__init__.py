"""Import all toolbox widget modules to trigger their ``@toolbox_plugin`` registrations.

This module is the single place that drives plugin discovery.  It is imported
by :class:`ToolboxButton` at construction time so the registry is populated
before the menus are built.
"""

# Data
import tse_analytics.toolbox.data_table.data_table_widget  # noqa: F401
import tse_analytics.toolbox.fast_data_plot.fast_data_plot_widget  # noqa: F401
import tse_analytics.toolbox.data_plot.data_plot_widget  # noqa: F401

# Exploration
import tse_analytics.toolbox.histogram.histogram_widget  # noqa: F401
import tse_analytics.toolbox.distribution.distribution_widget  # noqa: F401
import tse_analytics.toolbox.normality.normality_widget  # noqa: F401

# Bivariate
import tse_analytics.toolbox.correlation.correlation_widget  # noqa: F401
import tse_analytics.toolbox.regression.regression_widget  # noqa: F401

# ANOVA
import tse_analytics.toolbox.one_way_anova.one_way_anova_widget  # noqa: F401
import tse_analytics.toolbox.n_way_anova.n_way_anova_widget  # noqa: F401
import tse_analytics.toolbox.rm_anova.rm_anova_widget  # noqa: F401
import tse_analytics.toolbox.mixed_anova.mixed_anova_widget  # noqa: F401
import tse_analytics.toolbox.ancova.ancova_widget  # noqa: F401

# Factor Analysis
import tse_analytics.toolbox.correlation_matrix.correlation_matrix_widget  # noqa: F401
import tse_analytics.toolbox.matrixplot.matrixplot_widget  # noqa: F401
import tse_analytics.toolbox.pca.pca_widget  # noqa: F401
import tse_analytics.toolbox.tsne.tsne_widget  # noqa: F401
import tse_analytics.toolbox.mds.mds_widget  # noqa: F401

# Circadian Analysis
import tse_analytics.toolbox.actogram.actogram_widget  # noqa: F401
import tse_analytics.toolbox.periodogram.periodogram_widget  # noqa: F401

# Time Series
import tse_analytics.toolbox.timeseries_decomposition.timeseries_decomposition_widget  # noqa: F401
import tse_analytics.toolbox.timeseries_autocorrelation.timeseries_autocorrelation_widget  # noqa: F401

# IntelliCage
import tse_analytics.modules.intellicage.toolbox.transitions.transitions_widget  # noqa: F401
import tse_analytics.modules.intellicage.toolbox.place_preference.place_preference_widget  # noqa: F401
