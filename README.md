# TSE Analytics

TSE Analytics is a data analysis application designed specifically to work with the data output produced by
[TSE PhenoMaster](https://www.tse-systems.com/service/phenotype/) software. It allows a simplified management of
multiple datasets, data sharing and reproducibility of experimental results in a flexible and user-friendly way.

At its core, TSE Analytics provides the following functionality:

- Working with multiple datasets simultaneously with the option to merge individual datasets
and to save the whole workspace for later use.
- Automatic extraction of meaningful metadata from the raw data (i.e. animal information, factors, variables sets)
- Applying different data processing parameters on per-dataset level (e.g. different sampling times, etc.)
- Data filtering on per-animal level, like exclusion of some animals from data processing.
- User-defined flexible time binning with multiple grouping modes: animals, factors or runs.
- Automatic handling of light/dark cycles or manual configuration of time phases
(for instance, "fasting", "pre-feeding", "sleeping", etc.)
- Outliers detection with or without removal of the data entries.
- Export of the pre-processed data for external downstream analysis.

Being modular toolkit by design, TSE Analytics hosts already many data analysis and visualisation capabilities and
can be easily expanded in the future:

- Visualisation of row data on the timeline grouped by animals, factors or time bins.
- Histograms for selected sets of variables together with distribution and normality analysis.
- Calculation of correlations between variables, including linear regression analysis.
- Several forms of ANOVA (N-way, repeated measures, mixed design) and ANCOVA.
- Dimensionality reduction by means of PCA, tSNE or UMAP.
