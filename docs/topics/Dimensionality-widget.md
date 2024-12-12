# Dimensionality

The _Dimensionality_ widget offers multiple options for the generation of high-dimensional analysis plots considering multiple variables of interest.

![Figure: Dimensionality widget](Dimensionality widget.png)

Variables, analysis mode and split mode for high-dimensional analysis can be selected from the control panel in the _Dimensionality_ widget:

![Figure: Dimensionality window](Dimensionality window.png)

In the **Variables** list of the control panel, at least two variables must be selected for matrix plots and at least three variables for PCA or tSNE. 

The **Analysis** modes available are generation of matrix plots, principal component analysis (PCA) plots, and t-distributed stochastic neighbor embedding (t-SNE).
These dimensionality plots are scatter plots showing single animal or mean data (according to split mode) per time bin (each dot represents one time bin) depending on time binning settings.

[//]: # (TODO: More Explanation axis of PCA and tSNE plots)

Different **Split Modes** (Total, By Animal, By Run, By Factor) can be applied to all analysis.

- Split mode ‘**Total**’ uses the mean data values of all animals per time bin.
- Split mode ‘**By Animal**’ does not calculate means but uses individual data points for each animal per time bin.
- Split mode ‘**By Run**’ uses the mean data values of each run per time bin.
- Split mode ‘**By Factor**’ uses the mean data value of each group of the selected factor per time bin.

[//]: # (TODO: Explanation of the split mode is right? need Anton help check...)

![Figure: Split mode and Update](Split mode and Update.png)

Clicking **Update** in the control panel is necessary to display analysis results or to apply changes in the analysis settings.

> **Warning**: Only animals selected in the _Animal_ list are considered for the calculation and display of plots in the _Dimensionality_ widget.
> Changes regarding the selection of animals are only applied after clicking **Update**.
{style = 'warning'}

The plot appearance can be edited by using the tools available in the **plot menu** at the bottom of the control panel.

![Figure: Plot menu](Plot menu.png)

From left to right:
- **Home** button (‘House’): Reset the orientation of the plot in its frame.
- **Undo/Redo** (‘Arrows’ left/right): Undo and redo actions regarding the orientation of the graph in its frame (moving and zooming).
- **Pan** (‘Arrow cross’): Grab and move the graph within the frame of the plot.
- **Zoom** (‘Magnifying glass’): Select an area of the plot to zoom in/ enlarge the selected area.
- **Subplots** (‘Slider bars’): Adjust the dimensions of frame borders and spacings between graphs (in the case of multiple plots).
- **Customize** (‘Graph’):
    - Define title, axis range, label and scale, and legend.
    - Adjust style, size and coloring of data points.
- **Save** (‘Memory disc’): Save image on the hard drive.

> **Note**: Any changes in graph appearance made through the plot menu are applied immediately, without clicking Update.
{style='note'}

![Figure: Dimensionality widget with control panel](Dimensionality widget with control panel.png)

Dimensionality plots can be exported via the **Save** button (‘Memory disk’ symbol) in the plot menu at the bottom of the control panel or added to the report by clicking **Add to Report**.
