# Correlation

**Correlation** analysis in TSE Analytics can be performed to determine the degree to which two selected variables X and Y are linearly related using the Pearson correlation coefficient.
Results of a correlation analysis performed in TSE Analytics are displayed as a scatter plot for all data pairs included in the analysis, individual density plots or histograms (for split mode ‘Total’) for each variable, the Pearson correlation coefficient together with associated statistical parameters, as well as t test statistics comparing X and Y variable.

![Figure: Correlation window](Correlation window.png)

## Correlation plots

Data pairs for each time bin are depicted as dots in the **scatter plot** and are dependent on the selected split mode and time binning settings.

![Figure: Variable and split mode in correlation window](Variable and split mode in correlation window.png)

- Split mode **Total** uses the mean data values of all animals per time bin.
-	Split mode **By Animal** does not calculate means but uses individual data points for each animal per time bin.
-	Split mode **By Run** uses the mean data values of each run per time bin.
-	Split mode **By Factor** uses the mean data value of each group of the selected factor per time bin.

**Histograms/ Density plots** represent the frequency of values separately for each variable (parallel to the respective axis) under consideration of the selected split mode and time binning settings.

> **Note**: Histograms will only be used in split mode Total.
> If data is split into smaller subsets (By Animal/Run/Factor), separate density curves per subset of data are shown.
{style = 'note'}

To adjust the appearance of a plot, use the **‘Customize’** tool (‘Graph’ symbol) in the plot menu and select the respective plot from the drop-down menu (**“[Variable X] – [Variable Y]”** for scatter plot and **“[Variable X] – Count/Density”** or **“Count/Density – [Variable Y]”** for density plots/ histograms).

- The title, as well as range, label and scale of axis and generation of an automatic legend of the individual plots can be defined in the **Axes tab** of the Customize tool.
- In the case of multiple animals, runs or groups (for split modes By Animal, By Run or By Factor, respectively), the appearance of each data subset can be adjusted individually in the **Curves tab** of the ‘Customize’ tool by selecting the respective subset form the upper
  dropdown menu.

![Figure: Plot selection of the Customize tool for correlation analysis](Plot selection of the Customize tool for correlation analysis.png)

![*Figure: Axes tab of the Customize tool for correlation analysis](Axes tab of the Customize tool for correlation analysis.png)

![Figure: Curves tab of the Customize tool for correlation analysis](Curves tab of the Customize tool for correlation analysis.png)

## Correlation results table

Correlation analysis results are calculated based on the (mean) data values per time bin depending on the respective split mode.

![Figure: Correlation analysis resulta table](Correlation analysis resulta table.png)

The **Pearson correlation** coefficient table indicates (from left to right):

-	X: Selected X variable
-	Y: Selected Y variable
-	method: Method of correlation analysis (pearson)
-	alternative: Tail of the test (two-sided)
-	n: Sample size (number of data pairs)
-	r: Correlation coefficient
-	CI95%: 95% parametric confidence intervals
-	p-unc: Uncorrected p-value
-	BF10: Bayes factor of the alternative hypothesis
-	power: Achieved power of the test (= 1 - type II error)

The **T test statistics** comparing the X and Y variable include (from left to right):

- T: T-value
- dof: Degrees of freedom
- alternative: Tail of the test (two-sided)
- p-val: p-value
- CI95%: Confidence intervals of the difference in means
- cohen-d: Cohen d effect size
- BF10: Bayes factor of the alternative hypothesis
- power: Achieved power of the test (= 1 - type II error)
