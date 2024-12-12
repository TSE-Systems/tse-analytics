# Export Dataset

TSE Analytics offers multiple options for data export depending on the data format and the user’s preferences.

## Export of Data table

The data table of the active dataset including all variables can be exported using text (.csv) or Excel (.xlsx) format via **File | Export to CSV** or **File | Export to Excel** in the software header.
After setting the file destination and file name in the File Explorer, the data table is stored at the selected destination by clicking **Save**. 

![Figure: Options for data table export](Options for data table export.png)

This data export option will save the current version of the active data table under consideration of changes that have been made using TSE Analytics. Changes considered for the exported data table include merging of datasets, exclusion of animals and animal selection in the animals list via checkboxes, exclusion of time phases and adjustment of time, editing of animal information or factors, time binning and removal of outliers.

> **Warning**: Variable selection and Split Mode selection in the Table control panel do not affect the content of the exported data table, but only the way data is displayed in the Table widget.
> The exported data table always contains all variables extracted from the PhenoMaster file and data for individual animals (as for Split Mode “By Animal”).
>
> Similarly, sorting of data entries in the Table widget will change the order of data entries displayed under Table, but will not affect the exported data table.
{style='warning'}

##  Export of Raw Data Plots

Data plots created in the _Plot_ widget can be exported by **right-clicking** on the plot window and selecting **Export** from the menu.

In the _Export_ window which opens subsequently, one can choose which item of the plot should be exported (selected item framed in yellow), select the export format (CSV of original plot data; image file format such as _.png, .tif, .jpg_; Matplotlib Window; Scalable Vector Graphics) and adjust additional export parameters depending on the export format. By clicking **Copy**, image files and scalable vector graphics can be copied to the clipboard, while **Export** allows to select file destination and name, specifiy the data format and save the file by clicking **Save** in the _Save As_ window.

![Figure: Export of raw data plot](Export of raw data plot.png)

## Export of Data from the Exploration, Bivariate, Dimensionality and Timeseries Widgets

Export of analysis results and graphs works in the same way for the _Exploration_ widget (histograms, violin plots, box plots and normal probability plots), _Bivariate_ widget (correlation and regression analysis) and the _Timeseries_ widget. 

Each widget contains a plot menu in the bottom right corner of the control panel including a **Save button** (‘Memory card’ symbol).
By clicking the **Save** **button**, a _File Explorer_ window opens, in which file destination, file name and format can be selected.
Clicking **Save** will store the graphic file at the selected location.

![Figure: Export of exploration, bivariate and timeseries data](Export of exploration, bivariate and timeseries data.png)

## Export of AN(C)OVA Results and Bivariate Analysis Tables

TSE Analytics does not offer a dedicated export function for AN(C)OVA or bivariate analysis (correlation and regression) result tables so far.
However, results can be saved outside of TSE Analytics via copy and paste.
All analysis results can be selected by clicking on the data table and pressing <shortcut>Ctrl+A</shortcut> on the keyboard or by **right-clicking** on the analysis window and selecting **Select All**.
Selected content can then be copied to the clipboard using <shortcut>Ctrl+C</shortcut> or by right-clicking on the analysis window again and selecting **Copy**.
Content copied to the clipboard can then be pasted and saved outside of TSE Analytics.

![Figure: Export of AN(C)OVA and bivariate analysis results using "Copy and Paste"](Export of AN(C)OVA and bivariate analysis results using "Copy and Paste".png)

## Export of Data via Report

In addition to specific export options which vary between different analysis and plots, all results can be saved within a workspace and outside of TSE Analytics using the **Add Widget | Utils | Report** widget. 

- Result tables and graphs can be added to the Report by clicking Add to Report at the bottom of the control panel of the respective widget. 

![Figure: Adding to report](Adding to report.png)

- In addition, the Report works as a text editor and allows to add customized text to analysis results. 

![Figure: Editing report](Editing report.png)

Each dataset has an individual report and all reports are saved within a workspace in TSE Analytics when saving the workspace. 

The Report menu offers several tools for editing the report and text elements (from left to right):

- Undo/Redo
- Cut/ Copy/ Paste
- Selection of text font
- Selection of text size
- Text style: Bold/ Italic/ Underline
- Content alignment: Left/ Center/ Right/ Justify

![Figure: Editing toolbar](Editing toolbar.png)

Each dataset has an individual report and all reports are saved within a workspace in TSE Analytics when saving the workspace.

Reports can also be saved outside of TSE Analytics as an .html file by clicking on the **Save** button (‘Memory disk’ symbol) in the Report menu.

![Figure: Saving report](Saving report.png)

Reports can also be printed by clicking on the **Print** button (‘Printer’ symbol) in the Report menu.
If **Microsoft Print to PDF** is selected under **Printer** in the printing settings, reports can thereby also be saved as .pdf files.

![Figure: Printing report](Printing report.png)

All entries of an existing report are cleared by clicking the **New Report** button (‘Sheet’ symbol) on the left of the report menu.

![Figure: Creating new report](Creating new report.png)

> **Warning**: This action cannot be undone! Clicking **New Report** will definitively delete all previous content from the report.
{style = 'warning'}
