# TSE Analytics

## Overview

What does TSE Analytics offer?
:
1. **Integrated Data Handling**: TSE Analytics is designed to manage large and complex data sets like PhenoMaster data. It seamlessly integrates data processing, visualization, and statistical analysis, making it a powerful tool for researchers.
2. **Flexible Data Customization**: The software allows users to tailor data structures to their specific needs. You can exclude outliers, define time frames, merge multiple data sets, and create new grouping factors quickly and easily.
3. **Dynamic Visualization**: With TSE Analytics, you can visualize data in real-time using the plot function. This feature lets you quickly screen and compare data across different groups, individual animals, or specific time periods.
4. **Comprehensive Statistical Analysis**: The software includes a broad range of statistical tools, from basic options like histograms and box plots to advanced analyses such as various forms of ANOVA, ANCOVA, principal component analysis, and time series analysis.
5. **User-Friendly and Efficient**: TSE Analytics stands out for its ease of use and extensive analytical capabilities. It enables researchers to process and analyze their data efficiently, making it an invaluable tool for scientific research.


Being a modular toolkit by design, TSE Analytics hosts many data analysis and visualisation capabilities, which can be easily expanded in the future:

- Working with multiple data sets simultaneously with the option to merge individual data sets and to save the whole workspace for later use
- Automatic extraction of meaningful metadata from the raw data (i.e. animal information, factors, variables sets)
- Applying different data processing parameters on per data set level (e.g. different sampling times, exclusion of animals)
- User-defined grouping of data with multiple grouping modes (i.e. animals, factors or runs) for further analysis
- Flexible time binning by time intervals, automatic handling of light/dark cycles or manual configuration of time phases 
(for instance, "fasting", "pre-feeding", "sleeping", etc.)
- Outliers detection with or without removal of data entries
- Visualisation of raw data on the timeline grouped by animals, factors or time bins.
- Exploratory data analysis and visualisation including histograms, distribution and normality analysis.
- Calculation of correlations between variables, including linear regression analysis.
- Several forms of ANOVA (One-way, N-way, repeated measures, mixed design) and ANCOVA.
- Dimensionality reduction by means of PCA or tSNE
- Export of the pre-processed data for external downstream analysis


## Data analysis pipeline

Almost all widgets work with the preprocessed data that passed through the internal data analysis pipeline.
1. Raw data first goes into *Animal Filter* pipe operator. This unit obtains data only for the selected set of animals. **Animals** can be selected in Animals widget.
2. Second step is the outliers removal in the *Outliers* pipe operator. This unit can be activated/deactivated in the **Outliers** widget (see details below).
3. Last step in the preprocessing data pipeline is *time binning* operation.

>**Note:** If you observe some unexpected results during your analysis, please check animal selection in **Animals** widget and time binning options in **Binning** widget!
>
{style="warning"}

