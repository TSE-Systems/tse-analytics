# Exploration widget

TSE Analytics offers multiple graphical tools to perform exploratory and distribution analysis in the **Exploration** widget, including histograms, violin- and boxplots, as well as normal probability plots. Plots can be generated using different split modes (total, by animal, by run, by factor) under consideration of time binning settings and outlier detection settings. 

> **Warning:** Only animals selected in the Animal list are considered for the calculation and display  of plots in the Exploration widget. Changes regarding the selection of animals are only applied after clicking **Update**.
{style = 'warning'}

All plot settings can be adjusted using the control panel at the right-hand side of the Exploration widget.

![exploration-widget.png](exploration-widget.png)

The respective variable to be plotted can be selected from the **Variable** drop-down menu on the top. The type of plot (**Histogram, Distribution, Normality**) can be chosen under **Plot**. If the plot type Distribution has been selected, two plot options are available: **violin** and **boxplot** (see **Distribution as**). 

Various **Split modes** are available for all plot types:
- **Total**: All data entries for the respective variable are considered for plotting.
- **By Animal**: A plot for each animal is generated individually.
- **By Run**: A plot for data from each run is generated separately.
>Note: Split modes “Total” and “Run” produce the same results if only one individual dataset (i.e. one run) is analyzed. In case of merged datasets (not merged as a single run), this split mode allows to compare the plots of the individual datasets (i.e. individual runs) used for merging.
{style = 'note'}
- **By Factor**: A plot for each group of the selected factor is generated. The respective factor of interest can be selected from the “By factor” dropdown menu.

To show plots and to apply any changes of settings to the plots displayed, click **Update** in the control panel (graphs won’t update automatically).

The plot appearance can be edited by using the tools available in the **plot menu** at the bottom of the control panel. 

![plot-menu.png](plot-menu.png)

- **Home button** (‘House’): Reset the orientation of the plot in its frame.
- **Undo/Redo** (‘Arrows’ left/right): Undo and redo actions regarding the orientation of the graph in its frame (moving and zooming).
- **Pan** (‘Arrow cross’):  Grab and move the graph within the frame of the plot.
- **Zoom** (‘Magnifying glass’): Select an area of the plot to zoom in/ enlarge the selected area.
- **Subplots** (‘Slider bars’): Adjust the dimensions of frame borders and spacings between graphs (in the case of multiple plots).
- **Customize** (‘Graph’):
Define title, axis range, label and scale, and legend. Adjust style, size and color of curves (applies only to some elements within normality plots and violin plots).
- **Save** (‘Memory disc’): Save image on the hard drive.

> **Note:** Any changes in graph appearance made through the plot menu are applied immediately, without clicking Update.
{style = 'note'}

In addition to saving a plot on the hard drive via the plot menu, the graph displayed can be added to the report by clicking **Add to Report** and will be saved together with the currently active workspace.

# Histogram

Histograms can be generated in TSE Analytics by selecting **Plot type ‘Histogram’** in the Exploration widget.

![histogram-plot-selector.png](histogram-plot-selector.png)

- The x-axis of a histogram plot represents the range of data values included in the plot. The y-axis indicates the number of datapoints falling into a defined range of values, referred to as ‘bin’. 
- Bins are represented by columns in the histogram plot. The column width shows the range of values covered by a bin, while the height of each bin indicates the number of datapoints assigned to a bin.
- The default number of ten bins used in TSE Analytics is fixed and cannot be adjusted. The width of bins is calculated automatically, based on the total range of values displayed in the current plot divided by ten. 

> **Note:** Less than ten columns are displayed in the histogram overview if the number of values assigned to a bin is very small or zero. Columns for small numbers of values appear when zooming into the respective area of the plot (Zoom in (‘Magnifying glass’) in the plot menu) at the bottom of the control panel.  No column is displayed if the number of values assigned to a bin is zero.
{style = 'note'}

![histogram-plot.png](histogram-plot.png)

# Violin plots

Violin plots can be generated in TSE Analytics by selecting 
- **Plot type ‘Distribution’**  
- and **Distribution as ‘Boxplot’** in the Exploration widget. 

![violin-plot-selector.png](violin-plot-selector.png)

Violin plots represent the distribution of a selected dataset by combining density curves (blue) and box plots (dark grey). 
- The width of each density curve indicates the approximate frequency of data points. 
- The overlaid box plot (dark grey) shows the interquartile range (IQR), i.e. the range from the first to the third quartile (rectangle), together with the median (white dot).
- The adjacent whiskers indicate the range of 1.5 times the IQR (1.5*IQR) with whiskers ranging from the first/ third quartile to the smallest/ largest data point within 1.5*IQR.
- The lower and upper end of the violin plot represent the minimum and maximum value. 

![violin-plot.png](violin-plot.png)

The appearance of the boxplot shown within the density plot can be customized by using the Curves tab implemented in the Figure options window access via the **‘Customize’** tool (‘Graph’ symbol) in the plot menu. Here, the style, width and color of lines can be adjusted, and markers can be added or customized.

![plot-customization.png](plot-customization.png)

The part of the box plot to be customized can be selected from the dropdown menu at the top of the Curves tab:
- _child1: Boxplot whiskers
- _child2: Interquartile range (IQR)
- _child3: Median


# Boxplots

Box plots can be generated in TSE Analytics by selecting 
- **Plot type ‘Distribution’**
- and **Distribution as ‘Boxplot’** in the Exploration widget.

![boxplot-selector.png](boxplot-selector.png)

Boxplots represent the distribution of a selected dataset including:
- the box ranging from the first to the third quartile, indicating the interquartile range (IQR) 
- the median
- whiskers ranging from the first/ third quartile to the lowest/ highest value within the range of 1.5*IQR
- values outside of the range of 1.5*IQR displayed as circles

![box-plot.png](box-plot.png)


# Normal Probability Plots (Normality Plots)

Normal probability plots (normality plots) can be generated in the Exploration widget by selecting the **Plot type ‘Normality’** to test for normal distribution of data sets. 

![normality-plot-selector.png](normality-plot-selector.png)

Normal probability plots are scatter plot in which, for each value of the dataset, the actual quantiles of the sample data (ordered quantiles) on the y-axis are plotted against the theoretical quantiles of the respective normal distribution on the x-axis (blue dot). An alignment of the plot with the 45° line (y=x) indicates a normal distribution of the sample data.

In addition, normality plots contain a ‘best-fit’ line resulting from linear regression analysis of all data points included in the plot, together with the confidence band and the coefficient of determination R2.

![qq-plot.png](qq-plot.png)

The appearance of the 45° line, regression line and confidence band of the normality plot can be customized by using the Curves tab implemented in the Figure options window accessed via the **‘Customize’** tool (‘Graph’ symbol) in the plot menu. Here, the style, width and color of lines can be adjusted, and markers can be added or customized.

![plot-customization-2.png](plot-customization-2.png)

The lines to be customized can be selected from the dropdown menu at the top of the Curves tab:
- _child1: 45° line
- _child2: Regression line
- _child4: Upper bound of the confidence band
- _child5: Lower bound of the confidence band
