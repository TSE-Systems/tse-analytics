# Exploration

TSE Analytics offers multiple graphical tools to perform exploratory and distribution analysis in the **Exploration** widget, including histograms, violin- and boxplots, as well as normal probability plots. Plots can be generated using different split modes (total, by animal, by run, by factor) under consideration of time binning settings and outlier detection settings. 

![Exploration widget](Exploration widget.png)

> **Warning:** Only animals selected in the Animal list are considered for the calculation and display  of plots in the Exploration widget. Changes regarding the selection of animals are only applied after clicking **Update**.
{style = 'warning'}

All plot settings can be adjusted using the control panel at the right-hand side of the Exploration widget.

![Figure: Control panel in the Exploration widget](Control panel in the Exploration widget.png)

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

![Figure: Plot menu](plot-menu.png)

- **Home button** (‘House’): Reset the orientation of the plot in its frame.
- **Undo/Redo** (‘Arrows’ left/right): Undo and redo actions regarding the orientation of the graph in its frame (moving and zooming).
- **Pan** (‘Arrow cross’):  Grab and move the graph within the frame of the plot.
- **Zoom** (‘Magnifying glass’): Select an area of the plot to zoom in/ enlarge the selected area.
- **Subplots** (‘Slider bars’): Adjust the dimensions of frame borders and spacings between graphs (in the case of multiple plots).
- **Customize** (‘Graph’): Define title, axis range, label and scale, and legend. Adjust style, size and color of curves (applies only to some elements within normality plots and violin plots).
- **Save** (‘Memory disc’): Save image on the hard drive.

> **Note:** Any changes in graph appearance made through the plot menu are applied immediately, without clicking Update.
{style = 'note'}

In addition to saving a plot on the hard drive via the plot menu, the graph displayed can be added to the report by clicking **Add to Report** and will be saved together with the currently active workspace.
