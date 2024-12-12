# Variables

This widget is used to choose of one or many variables that you want to display in the **Data** widget table or
include in the downstream analysis in components that support multiple variables selection, like **Matrix** or **PCA**
widgets.

![Figure: Variables widget](variables.png)

Similarly to **Animals** widget, in order to select all variables at once, please press <shortcut>Ctrl+A</shortcut> or drag mouse over
entries you want to choose. To select/deselect individual entries, click on the entry holding <shortcut>Ctrl</shortcut> key.


## Aggregation

Different methods of calculation (**Aggregation** modes) can be used for the calculation of data values for individual time bins during binning: mean, median, sum, minimum and maximum.

![Figure: Aggregation mode](Aggregation mode.png)

These modes can be specified individually for each variable via the dropdown menu in the **Aggregation** column of the _Variables_ widget.
The most suitable aggregation mode differs between variables depending on the way data is collected and displayed during a PhenoMaster experiment.

![Figure: Resetting default aggregation mode](Resetting default aggregation mode.png)

The default aggregation mode is the recommended method of calculation. Aggregation modes for all variables can be reset to the default state by clicking **Reset** in the header of the _Variables_ widget.


## Outlier Detection

Outlier detection settings can be adjusted in the _Variables_ widget.
Here, one can choose between different modes via the dropdown menu: no outlier detection (**Outliers detection off**), highlighting outliers in the data table (**Highlight outliers**), and removing outliers from the dataset (**Remove outliers**).

![Figure: Selection of outlier detection mode in the variables tab](Selection of outlier detection mode in the variables tab.png)

The sensitivity of outlier detection can be adjusted via the coefficient (for further information about the outlier detection method used (please see below: IQR method for outlier detection).
Decreasing the coefficient will result in more values being identified as outliers, while increasing the coefficient will result in less outliers.

![Figure: Outlier detection coefficient](Outlier detection coefficient.png)

The variables to which outlier detection should be applied, need to be selected using the tick boxes in the ‘**Outliers’** column in the _Variables_ widget.
Only variables selected here will be considered for the identification of outliers.
The variable selection for outlier detection can be reset to the default (no variables selected) together with the aggregation mode selector by clicking **Reset** in the Variables widget.

> **Warning**: Selecting **Remove outliers** will not only delete outlier values but the whole row (i.e. time bin) in the data set which contains one or more values detected as outliers.
> This means that values of all variables recorded at the same time point as the outlier are removed from the dataset as well. 
>
> Therefore, it is recommended to only select the variable(s) for outlier detection which are used for subsequent analysis.
{style='warning'}

![Figure: Selecting (left) and resetting (right) of variables for outlier detection. in the Variables widget](Selecting (left) and resetting (right) of variables for outlier detection. in the Variables widget.png)


> **IQR method for outlier detection**
> - Outlier detection is performed using the interquartile range (IQR) method for outlier detecting.
> - The IQR is defined as the range between the first quartile (Q1) and the third quartile (Q3) of a given dataset (IQR = Q3 – Q1).
> The IQR method identifies outliers by multiplying the IQR with a coefficient set by the user (a coefficient of 3 is set by default in TSE Analytics).
> The resulting value (IQR \* coefficient) is used to define a new range of values used for outlier detection by extending the IQR on both sides by this calculated value.
> The borders of this new range of values are therefore defined as Q1 – IQR \* coefficient and Q3 + IQR \* coefficient.
> All data points outside of the range [Q1 – IQR * coefficient; Q3 + IQR * coefficient] are considered **outliers**.
{style='note'}
