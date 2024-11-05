# Bivariate widget

To analyze the relationship between two variables, **Correlation** and **Regression** analysis can be performed in the **Bivariate** widget of TSE Analytics.
- Two variables of interest can be selected from the dropdown menus **“X”** and **“Y”** for **Correlation** analysis or **“Covariate”** and **“Response”** for **Regression** analysis on the top of the control panel in the Bivariate window. 
- The type of analysis (**Correlation** or **Regression**) can be selected under **Analysis**. 
- Different **Split Modes** (**Total**, **By Animal**, **By Run**, **By Factor**) can be applied to correlation and regression analysis. 

To show plots and analysis results and to apply changes in the settings, click **Update** in the control panel. 
Both plots and analysis results displayed are added to the report upon clicking **Add to Report**.

![bivariate-widget.png](bivariate-widget.png)

>**Warning:** Only animals selected in the Animal list are considered for the calculation of correlation and regression analysis in the Bivariate widget. Changes regarding the selection of animals are only applied after clicking **Update**.
{style = 'warning'}

The plot appearance can be edited by using the tools available in the **plot menu** at the bottom of the control panel. 

![plot-menu.png](plot-menu.png)

From left to right:
- **Home button** (‘House’): Reset the orientation of the plot in its frame.	Undo/Redo (‘Arrows’ left/right): Undo and redo actions regarding the orientation of the graph in its frame (moving and zooming)
- **Pan** (‘Arrow cross’):  Grab and move the graph within the frame of the plot
- **Zoom** (‘Magnifying glass’): Select an area of the plot to zoom in/ enlarge the selected area.
- **Subplots** (‘Slider bars’): Adjust the dimensions of frame borders and spacings between graphs 
- **Customize** (‘Graph’): Define title, axis range, label and scale, and legend. Adjust style, size and color of curve.
- **Save** (‘Memory disc’): Save image on the hard drive.

> **Note:** Any changes in graph appearance made through the plot menu are applied immediately, without clicking Update.
{style = 'note'}

Except from adding results to the report, TSE Analytics does not offer a dedicated export function for bivariate analysis (correlation and regression) tables. However, results can be saved outside of TSE Analytics via “copy and paste”. All analysis results can be selected by clicking on the data table and pressing **Strg + A (Ctrl + A)** on the keyboard or by right-clicking on the analysis window and selecting **Select All**. Selected content can then be copied to the clipboard using **Strg + C (Ctrl + C)** or by right-clicking on the analysis window again and selecting **Copy**. Content copied to the clipboard can then be pasted **(Strg + V / Ctrl + V)** and saved outside of TSE Analytics.

![copy-paste.png](copy-paste.png)


# Correlation Analysis

**Correlation** analysis in TSE Analytics can be performed to determine the degree to which two selected variables X and Y are linearly related using the Pearson correlation coefficient. 
Results of a correlation analysis performed in TSE Analytics are displayed as a scatter plot for all data pairs included in the analysis, individual density plots or histograms (for split mode ‘Total’) for each variable, the Pearson correlation coefficient together with associated statistical parameters, as well as t test statistics comparing X and Y variable.

**Correlation analysis plots:**

Data pairs for each time bin are depicted as dots in the **scatter plot** and are dependent on the selected split mode and time binning settings.
-	Split mode **‘Total’** uses the mean data values of all animals per time bin.
-	Split mode **‘By Animal’** does not calculate means but uses individual data points for each animal per time bin. 
-	Split mode **‘By Run’** uses the mean data values of each run per time bin.
-	Split mode **‘By Factor’** uses the mean data value of each group of the selected factor per time bin.

**Histograms/ Density plots** represent the frequency of values separately for each variable (parallel to the respective axis) under consideration of the selected split mode and time binning settings.

> **Note:** Histograms will only be used in split mode ‘Total’. If data is split into smaller subsets (By Animal/ By Run/ By Factor), separate density curves per subset of data are shown.
{style = 'note'}

To adjust the appearance of a plot, use the **‘Customize’** tool (‘Graph’ symbol) in the plot menu and select the respective plot from the drop-down menu (**“[Variable X] – [Variable Y]”** for scatter plot and **“[Variable X] – Count/Density”** or **“Count/Density – [Variable Y]”** for density plots/ histograms). 

- The title, as well as range, label and scale of axis and generation of an automatic legend of the individual plots can be defined in the **Axes tab** of the Customize tool.
- In the case of multiple animals, runs or groups (for split modes By Animal, By Run or By Factor, respectively), the appearance of each data subset can be adjusted individually in the **Curves tab** of the ‘Customize’ tool by selecting the respective subset form the upper
dropdown menu.

![customize-correlation-plot.png](customize-correlation-plot.png)
![customize-correlation-plot-2.png](customize-correlation-plot-2.png)
![customize-correlation-plot-3.png](customize-correlation-plot-3.png)

**Correlation analysis results table:**

Correlation analysis results are calculated based on the (mean) data values per time bin depending on the respective split mode.

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


# Regression Analysis

Linear regression analysis (**“Regression”**) can be performed in TSE Analytics to investigate the relationship between an independent variable (**Covariate**) and a dependent variable (**Response**).
Results of a regression analysis performed in TSE Analytics are displayed as a regression plot and linear regression results in the GLM (Generalized Linear Model) table.

**Regression analysis plot:**

The regression plot combines a scatter plot of mean data values per time bin with a regression line and confidence band based on the plotted data values. The calculation of mean data values and plot appearance are dependent on the selected split mode:
-	Split mode **‘Total’** uses the mean data values of all animals per time bin. 
-	Split mode **‘By Run’** uses the mean data values of each run per time bin. Individual regression plots for each subset of data (runs) are displayed in one graph.
-	Split mode **‘By Factor’** uses the mean data value of each group of the selected factor per time bin. Individual regression plots for each subset of data (groups of the selected factor) are displayed in one graph.

The title, as well as range, label and scale of axis and generation of an automatic legend can be defined in the **Axes** tab of the ‘Customize’ tool (‘Graph’ symbol) in the plot menu. The appearance of regression lines can be adjusted in the **Curves** tab of the ‘Customize’ tool, whereby each label represents one data subset.

![customize-regression-plot.png](customize-regression-plot.png)
![customize-regression-plot-2.png](customize-regression-plot-2.png)

**Regression analysis results table:**

The GLM (Generalized Linear Model) table shows the statistical results of the linear regression, under consideration of the selected split mode and time binning settings:

Results include (from left to right):
- names: Name of the independent variable
- coef: Regression coefficients
- se: Standard errors
- T: T-values
- pval: p-values
- r2: Coefficient of determination (R2)
- adj_r2: Adjusted R2
- CI[2.5%]: Lower confidence intervals
- CI[97.5%]: Upper confidence intervals

If split mode ‘By Run’ or ‘By Factor’ is selected, a separate results table is displayed for each subset of data (for each run or group) in accordance with individual regression lines for each subset of data in the regression plot.

> **Note:** An intercept is added as a constant term to the model, to limit the bias and to force the residual mean to equal zero (see Pingouin library documentation: https://pingouin-stats.org/build/html/generated/pingouin.linear_regression.html). The GLM table always contains a row for the intercept as its first entry including a coefficient and a p-value, however, these values are rarely meaningful.
{style = 'note'}

