# Plot

Line and scatter plots (if no binning or binning using time phases is applied) or bar plots (for time binning using light/dark cycles or time phases) can be generated using the **Plot** widget. 

![Figure: Plot widget](Plot widget.png)

> **Warning**: Only animals selected in the Animal list are considered for the calculation of plots in the Plot widget
{style = 'warning'}

Variable selection, split modes and plot settings can be adjusted using the control panel on the right-hand side of the plot.

![Figure: Plot window with control panel](Plot window with control panel.png)

The **Variable** to be plotted is selected from the dropdown menu in the upper right corner within the Plot widget. 

Various **Split Modes** can be selected:
- **Total**: The mean over all data entries is plotted.
- **By Animal**: A plot for each animal is generated individually.
- **By Run**: The mean over all data entries assigned to a run is plotted, resulting in individual plots for each run.

>**Note**: Split modes “Total” and “Run” produce the same results if only one individual dataset (i.e. one run) is analyzed. In case of merged datasets (not merged as a single run), this split mode allows to compare the plots of the individual datasets (i.e. individual runs) used for merging.
{style = 'note'}

- **By Factor**: The mean over all data entries assigned to a factor group is plotted, resulting in individual plots for each group. The respective factor of interest can be selected from the “By factor” dropdown menu.

Errors for each mean value plotted are shown, if the **Display Errors** checkbox is ticked. Errors can be displayed as “Standard deviation” or “Standard error” (see selection underneath “Display Error”). No errors are displayed, if split mode ‘By animal’ is selected, if a factor group only contains one animal (for split mode ‘By factor’) or if only one animal is selected from the animal list independent of split mode.

For **line and scatter plots** (only if no time binning is applied or time binning using time intervals is applied):
- To change the plot style from line to scatter plot, the **Scatter plot** tick box must be checked.
- For line and scatter plots, two data plots are displayed. The large upper window is the main plot window and all settings specified in the control panel will be applied to this plot. The smaller plot at the bottom is always displayed as a line plot without error bars and serves as an overview over the whole plot. When the upper plot is used for zooming or enlarging an area of interest, a blue rectangle in the smaller plot at the bottom indicates the sector of the whole plot that is currently displayed in the upper window.
- The layout of both plots can be reset to their initial state by clicking **“A”** in the bottom left corner of each plot. The reset button (**“A”**) is only visible when hovering over the respective plot with the mouse cursor. 

![Figure: Line and scatter plots](Line and scatter plots.png)

Right-clicking on the plot opens a submenu for plot modifications. Here, further adjustments regarding the plot appearance (e.g. axis, grid, transparency, etc.) can be made.****

![Figure: Plot modification menu](plot-data-view-options.png)

The plot displayed can be exported by selecting **Export** and adjusting export options in the Export window. Alternatively, the current plot can be added to the report by clicking **Add to Report** in the control panel and will be saved together with the currently active workspace.