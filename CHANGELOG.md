TSE Analytics Change Log
====================================================================================================

# 1.8.1 (2026-02-20)

- Intermediate release before pipeline introduction.
- New: Migration to a unified HTML-based reporting system.
- New: Toolbox data analysis pipeline integration.
- Change: New docs based on Zensical toolchain with offline search functionality (no server needed in offline mode).
- Change: Migration of module dialog views to dockable widgets.
- Change: Adjust Dataset dialog tunings.
- Fix: Settings dialog now saves changes properly.
- Fix: resources path in .ui files.
- Fix: assign factors to generated group-housing TraffiCage datatable.
- Fix: align timedelta to the resampling resolution.
- [SW-456] Notification when a datatable is added in the GroupHousing dialog.
- [SW-465] Uniform animal sorting by AnimalId.
- [SW-466] GroupHousing heatmap plot exporting.


----------------------------------------------------------------------------------------------------
# 1.8.0 (2026-02-12)

- Intermediate release before pipeline introduction.
- New: Migration to a unified HTML-based reporting system.
- New: Toolbox data analysis pipeline integration.
- Change: New docs based on Zensical toolchain with offline search functionality (no server needed in offline mode).
- Change: Migration of module dialog views to dockable widgets.
- Change: Adjust Dataset dialog tunings.
- Fix: Settings dialog now saves changes properly.
- Fix: resources path in .ui files.
- Fix: assign factors to generated group-housing TraffiCage datatable.
- Fix: align timedelta to the resampling resolution.
- [SW-456] Notification when a datatable is added in the GroupHousing dialog.
- [SW-465] Uniform animal sorting by AnimalId.
- [SW-466] GroupHousing heatmap plot exporting.


----------------------------------------------------------------------------------------------------
# 1.7.1 (2025-12-11)

- Fix: drinkfeed_bin table data analysis.


----------------------------------------------------------------------------------------------------
# 1.7.0 (2025-12-03)

- New: Persistent reports repository (per dataset). Multiple reports are supported.
- Change: support for the new drinkfeed_bin table format (group-housing systems).


----------------------------------------------------------------------------------------------------
# 1.6.1 (2025-11-25)

- New: TraffiCage overlapping records detection.
- Fix: Fast plots Timestamp conversion to POSIX format.
- Change: Refactoring of the DrinkFeed interval bar plot.


----------------------------------------------------------------------------------------------------
# 1.6.0 (2025-11-14)

- New: Group housing data compatibility (PhenoMaster module).
- New: TraffiCage datatable processing.
- New: Persistent toolbox widgets settings.
- New: Fast Plot and Advanced Plot toolbox widgets.
- New: Customizable factor level colors.
- Change: PySide6-QtAds updated to version 4.4.1
- Change: Improved ANOVA/ANCOVA toolbox widgets.
- Change: ActiMot calculations parallelization.
- Fix: Repeated data merging without the "Bin" column.
- Fix: Resampling interval checks are improved.


----------------------------------------------------------------------------------------------------
# 1.5.3 (2025-08-26)

- New: Custom variables originated from expressions.
- New: Support for IntelliMaze Actor extension.
- New: Support for IntelliMaze IntelliCage extension.
- Fix: Variable names refactoring to avoid conflicts with predefined QWidget properties.
- Fix: Missing error bars in Total grouping mode.


----------------------------------------------------------------------------------------------------
# 1.5.2 (2025-06-23)

- Fix: Support the latest IntelliCage Animals.txt formats (broken CSV headers).
- Fix: Support the latest IntelliCage Visits.txt format (explicit licks information).


----------------------------------------------------------------------------------------------------
# 1.5.1 (2025-06-17)

- New: Support for IntelliMaze 6.x data format.
- New: IntelliMaze merged CSV export.
- Change: Group-by implementation for factors and Total mode.
- Fix: CSV import options persistence.


----------------------------------------------------------------------------------------------------
# 1.5.0 (2025-05-13)

- New: Data import for IntelliCage v1/v2 data formats.
- New: Circadian activity analysis: actogram and Lomb-Scargle periodogram tools.
- New: IntelliCage place preference analysis tool.
- New: IntelliCage corner transition analysis tool.
- New: Persistent color per animal management.
- New: Offline/online documentation integration.
- New: Custom animal properties.
- New: Variables management.
- New: Datatables management.
- New: Factor's levels extraction from animal properties.
- Change: UI refactoring around the new toolbox widgets concept.
- Change: Streamlining of required data fields (Animal/Run/Bin/etc.).
- Fix: Crashing plot when animal data are missing.
- Fix: Report widget data source.
- Fix: Proper datatables deserialization.


----------------------------------------------------------------------------------------------------
# 1.0.1 (2025-02-06)

- Change: Resolution of time ticks in the timeline plot.


----------------------------------------------------------------------------------------------------
# 1.0.0 (2024-12-19)

- First public release.
- Change: Reports can be modified without adding Report widget.


----------------------------------------------------------------------------------------------------
# 0.13.0 (2024-12-18)

- New: New QSS stylesheet generation and initialization.
- New: TSE Light color scheme.
- New: User selectable application UI styles.
- Change: Data normalization for PCA and tSNE analysis.
- Change: Streamlined startup implementation.
- Change: Migration to Python 3.13
- Change: Updated documentation draft.


----------------------------------------------------------------------------------------------------
# 0.12.3 (2024-11-27)

- Fix: Proper closing of already closed dataset widgets when dataset is removed.


----------------------------------------------------------------------------------------------------
# 0.12.2 (2024-11-22)

- Fix: wrong PCA/tSNE axes assignment.


----------------------------------------------------------------------------------------------------
# 0.12.1 (2024-11-22)

- Fix: Data plot region bounds properly set after binning.


----------------------------------------------------------------------------------------------------
# 0.12.0 (2024-11-20)

- New: New dockable UI for central area widgets. Multiple tabs of the same type can be opened for different or same datasets.
- Change: Split some widgets into the more specific types.


----------------------------------------------------------------------------------------------------
# 0.11.3 (2024-11-14)

- New: New manual draft integration.
- Fix: Data plot update when switching between datasets.


----------------------------------------------------------------------------------------------------
# 0.11.2 (2024-10-30)

- Change: Enable regression analysis for Split by Animal mode.
- Fix: Some visual tweaks.


----------------------------------------------------------------------------------------------------
# 0.11.0 (2024-10-25)

- New: WIP: Integration of the new TSE dataset format.
- New: Local animal selection in Timeseries widget.
- Change: Replace Plotly with Seaborn/Matplotlib (i.e. Dimensionality widget).
- Change: Hide unused elements for Autocorrelation in time series analysis.
- Change: Disable time series analysis when binning is active.
- Change: Visual tweaks for multiple plots.


----------------------------------------------------------------------------------------------------
# 0.10.4 (2024-10-15)

- New: Option to generate new animal names with run number suffix when merging datasets in overlap mode.
- Change: Disable pairwise-tests for three-way (and higher) ANOVA. See: https://pingouin-stats.org/build/html/generated/pingouin.pairwise_tests.html
- Fix: Sanitize variable names for N-way ANOVA (comma, bracket, and colon are not allowed in column names).


----------------------------------------------------------------------------------------------------
# 0.10.3 (2024-10-14)

- New: Calculation of T90, T95 and T99 for O2/CO2 gases.
- New: Option to reset aggregation operations and outlier setting in "Variables" panel.
- Change: Enable running repeated measures ANOVA even when factors are not defined.
- Change: Option for p value adjustment (pairwise comparison for repeated measures ANOVA).
- Fix: Warning to select a proper factor for "Split by Factor" mode in Data Table view.


----------------------------------------------------------------------------------------------------
# 0.10.2 (2024-10-10)

- New: Predefined variables parameters.
- Change: Redesigned binning/splitting (individual aggregation per variable).
- Fix: Unique IDs for cloned datasets.
- Fix: Reset "Animal" categorical column after exclusion of animals from the dataset.
- Fix: Recalculation of Timedelta/Bin columns after datasets adjustments.
- Fix: Correct list of available tables when importing TSE datasets.
- Fix: Fixed display of standard errors / standard deviation in data plot.


----------------------------------------------------------------------------------------------------
# 0.10.1 (2024-10-07)

- Change: Migration to Python 3.12.7 and Qt 6.7.3.
- Change: Binning and outliers settings are now parts of datasets instead of the global singleton.
- Change: Import settings for TSE data format.
- Change: Improved metadata merging.
- Fix: Correct index reset after dataset adjustments.
- Fix: Wrong aggregation calculation for some combinations of binning/splitting modes.
- Fix: QTBUG-125149: Misplaced popup menu for reparented combo box. See: https://github.com/mborgerson/pyside6_qtads/issues/35


----------------------------------------------------------------------------------------------------
# 0.10.0 (2024-10-03)

- New: Aggregation operations per variable.
- New: Outliers detection enabled on per-variable level.
- New: New notification subsystem.
- Change: Optional pairwise tests for repeated measures / mixed ANOVA.
- Change: Outliers detection UI combined in Variables widget.
- Change: Datasets widget toolbar UI.
- Fix: Split modes in Table data view were only working with active binning.
- Fix: Adding plot to report in Bivariate widget.


----------------------------------------------------------------------------------------------------
# 0.9.4 (2024-09-25)

- New: Multi-factor selection in ANOVA/ANCOVA widget.
- New: Sphericity test for repeated/mixed ANOVA.
- Change: Redesigned post-hoc tests for different ANOVA/ANCOVA modes.
- Change: panda's copy_on_write mode is disabled for the time being.
- Fix: Missing labels of X axis in the data plot.


----------------------------------------------------------------------------------------------------
# 0.9.3 (2024-09-20)

- Fix: Histogram in "Run" split mode.


----------------------------------------------------------------------------------------------------
# 0.9.2 (2024-09-18)

- New: Warnings when removing datasets or quitting the application.
- New: Toolbar introduced in "Datasets" widget.
- Change: "Tools" menu item removed from the main menu.
- Change: Refactored "Adjust Dataset" dialog UI and workflow.
- Change: Refactored "About" widget.
- Fix: Empty factor name in Bivariate widget.
- Fix : Reset index and reassign Timedelta and Bin values after dataset adjustments.


----------------------------------------------------------------------------------------------------
# 0.9.1 (2024-09-16)

- New: Calculation of T90 in CaloData dialog window.
- New: Introduction of UUID for datasets in order to implement multiple views per dataset.
- Change: Migration from Delphi-formatted timestamps (float64) to POSIX (int64).
- Change: Got rid of animal selection by clicking (now the only selection is via check-boxes).
- Change: Keep only "Animal" column as categorical.
- Change: Binning optimizations and fixes. Now binning aggregation can apply different operations per column.
- Fix: Double toggle events on radio buttons.
- Fix: "Total" split mode with active binning.
- Fix: Dunder prefix refactoring, cleanup and optimizations.


----------------------------------------------------------------------------------------------------
# 0.9.0 (2024-08-08)

- New: Continuous and overlapping merging modes.
- New: Initial implementation of new dataset import format (*.tse).
- Change: Migration to "Timedelta" instead of "DateTime" across the board for handling experiment time.
- Change: New TimePhase implementation based on "Timedelta" instead of "DateTime".
- Fix: Missing variables types in CSV importer.
- Fix: Support for old(er) PM versions: V3.6.0
- Fix: Double toggle events on radio buttons.
- Fix: "Total" split mode with active binning.
- Fix: Dunder prefix refactoring, cleanup and optimizations.


----------------------------------------------------------------------------------------------------
# 0.8.2 (2024-07-29)

- New: New UI and workflow for CSV import.
- Change: Licensing functionality removed.


----------------------------------------------------------------------------------------------------
# 0.8.1 (2024-07-09)

- New: Refactoring of animal IDs as strings.
- New: Renaming of animals.
- New: Advanced report editor.
- New: Persistent reports across datasets.
- New: Descriptive statistics view.
- Change: Redesigned Timeseries widget.
- Fix: See: https://github.com/pyinstaller/pyinstaller/pull/8622


----------------------------------------------------------------------------------------------------
# 0.7.1 (2024-06-24)

- Change: Different versions of TSE Analytics can be installed side by side.
- Fix: "Drink" column treatment in meal analysis.
