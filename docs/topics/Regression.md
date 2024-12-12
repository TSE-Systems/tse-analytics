# Regression

Linear regression analysis (**“Regression”**) can be performed in TSE Analytics to investigate the relationship between an independent variable (**Covariate**) and a dependent variable (**Response**).
Results of a regression analysis performed in TSE Analytics are displayed as a regression plot and linear regression results in the GLM (Generalized Linear Model) table.

![Figure: Regression window](Regression window.png)

## Regression plot

![Figure: Variable and split mode in regression window](Variable and split mode in regression window.png)

The regression plot combines a scatter plot of mean data values per time bin with a regression line and confidence band based on the plotted data values.
The calculation of mean data values and plot appearance are dependent on the selected split mode:

- Split mode **Total** uses the mean data values of all animals per time bin.
- Split mode **By Run** uses the mean data values of each run per time bin. Individual regression plots for each subset of data (runs) are displayed in one graph.
- Split mode **By Factor** uses the mean data value of each group of the selected factor per time bin. Individual regression plots for each subset of data (groups of the selected factor) are displayed in one graph.

The title, as well as range, label and scale of axis and generation of an automatic legend can be defined in the **Axes** tab of the ‘Customize’ tool (‘Graph’ symbol) in the plot menu.
The appearance of regression lines can be adjusted in the **Curves** tab of the ‘Customize’ tool, whereby each label represents one data subset.

![Figure: Axes tab of the Customize tool for regression analysis ](Axes tab of the Customize tool for regression analysis.png)

![Figure: Curves tab of the Customize tool for regression analysis ](Curves tab of the Customize tool for regression analysis.png)

## Regression results table

![Figure: Regression analysis results table](Regression analysis results table.png)

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

> **Note**: An intercept is added as a constant term to the model, to limit the bias and to force the residual mean to equal zero.
> The GLM table always contains a row for the intercept as its first entry including a coefficient and a p-value, however, these values are rarely meaningful.
{style = 'note'}
