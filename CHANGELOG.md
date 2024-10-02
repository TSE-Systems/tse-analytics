TSE Analytics Change Log
====================================================================================================

# 0.10.0 (2024-10-03)

- New    -- Aggregation operations per variable.
- New    -- Outliers detection enabled on per-variable level.
- New    -- New notification subsystem.
- Change -- Outliers detection UI combined in Variables widget.
- Change -- Datasets widget toolbar UI.
- Fix    -- Split modes in Table data view were only working with active binning.


----------------------------------------------------------------------------------------------------
# 0.9.4 (2024-09-25)

- New    -- Multi-factor selection in ANOVA/ANCOVA widget.
- New    -- Sphericity test for repeated/mixed ANOVA.
- Change -- Redesigned post-hoc tests for different ANOVA/ANCOVA modes.
- Change -- panda's copy_on_write mode is disabled for the time being.
- Fix    -- Missing labels of X axis in the data plot.


----------------------------------------------------------------------------------------------------
# 0.9.3 (2024-09-20)

- Fix    -- Histogram in "Run" split mode.


----------------------------------------------------------------------------------------------------
# 0.9.2 (2024-09-18)

- New    -- Warnings when removing datasets or quitting the application.
- New    -- Toolbar introduced in "Datasets" widget.
- Change -- "Tools" menu item removed from the main menu.
- Change -- Refactored "Adjust Dataset" dialog UI and workflow.
- Change -- Refactored "About" widget.
- Fix    -- Empty factor name in Bivariate widget.
- Fix  -- Reset index and reassign Timedelta and Bin values after dataset adjustments.


----------------------------------------------------------------------------------------------------
# 0.9.1 (2024-09-16)

- New    -- Calculation of T90 in CaloDetails dialog window.
- New    -- Introduction of UUID for datasets in order to implement multiple views per dataset.
- Change -- Migration from Delphi-formatted timestamps (float64) to POSIX (int64).
- Change -- Got rid of animal selection by clicking (now the only selection is via check-boxes).
- Change -- Keep only "Animal" column as categorical.
- Change -- Binning optimizations and fixes. Now binning aggregation can apply different operations per column.
- Fix    -- Double toggle events on radio buttons.
- Fix    -- "Total" split mode with active binning.
- Fix    -- Dunder prefix refactoring, cleanup and optimizations.


----------------------------------------------------------------------------------------------------
# 0.9.0 (2024-08-08)

- New    -- Continuous and overlapping merging modes.
- New    -- Initial implementation of new dataset import format (*.tse).
- Change -- Migration to "Timedelta" instead of "DateTime" across the board for handling experiment time.
- Change -- New TimePhase implementation based on "Timedelta" instead of "DateTime".
- Fix    -- Missing variables types in CSV importer.
- Fix    -- Support for old(er) PM versions: V3.6.0
- Fix    -- Double toggle events on radio buttons.
- Fix    -- "Total" split mode with active binning.
- Fix    -- Dunder prefix refactoring, cleanup and optimizations.


----------------------------------------------------------------------------------------------------
# 0.8.2 (2024-07-29)

- New    -- New UI and workflow for CSV import.
- Change -- Licensing functionality removed.


----------------------------------------------------------------------------------------------------
# 0.8.1 (2024-07-09)

- New    -- Refactoring of animal IDs as strings.
- New    -- Renaming of animals.
- New    -- Advanced report editor.
- New    -- Persistent reports across datasets.
- New    -- Descriptive statistics view.
- Change -- Redesigned Timeseries widget.
- Fix    -- See: https://github.com/pyinstaller/pyinstaller/pull/8622


----------------------------------------------------------------------------------------------------
# 0.7.1 (2024-06-24)

- Change -- Different versions of TSE Analytics can be installed side by side.
- Fix    -- "Drink" column treatment in meal analysis.
