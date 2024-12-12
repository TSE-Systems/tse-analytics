# Getting Started

Main window of TSE Analytics is a host of multiple dockable widgets. Users may resize, move and organize the layout
of the main application window up to their liking. Users can hide/show some widgets by using **View** section
in the main menu.

The layout is saved when you quit the application.

> **Note**: Default layout can be restored by clicking **View | Reset Layout** menu command.
{style='note'}

![Figure: main window](main.png)

## Data structure

All data in the application are organized in the following manner:

```
├── Workspace
│   ├── Dataset 1
│   │   ├── Metadata 1
│   │   ├── Animals set 1
│   │   ├── Variables set 1
│   │   ├── Factors set 1
│   │   ├── Settings 1
│   ├── Dataset 2
│   │   ├── Metadata 2
│   │   ├── Animals set 2
│   │   ├── Variables set 2
│   │   ├── Factors set 2
│   │   ├── Settings 2
│   ├── Dataset ...
│   │   ├── Metadata ...
│   │   ├── Animals set ...
│   │   ├── Variables set ...
│   │   ├── Factors set ...
│   │   ├── Settings ...
```

Top level data structure is a *Workspace*. It can contain one or many datasets.

Each *dataset* represents a single imported CSV data file from TSE PhenoMaster software.
All relevant metadata extracted during import procedure (e.g., sampling time, animals and variables lists, etc.).
Each dataset contains a set of its own settings. After initial import, dataset is assigned an experiment *Run* number **1** by default.

To import dataset, please click **File | Import Dataset** command. As soon as data from CSV file are imported,
you will see a new entry in the *Datasets* widget. By selecting a specific entry in this widget, one can switch freely
between different datasets:

![Figure: datasets](datasets.png)

> **Note**: Only one dataset can be active at the time in the workspace!
{style='note'}

When dataset is selected, all other widgets will be updated accordingly: for example, **Info**, **Animals**,
**Variables** and **Factors** widgets will show information relevant to the active (currently selected) dataset.

Let's have a look at selection widgets.


## Data analysis pipeline

Almost all widgets (with some exceptions mentioned later) work with the preprocessed data that passed through the
internal data analysis pipeline.

1. Raw data first goes into *Animal Filter* pipe operator. This unit obtains data only for the selected set
   of animals. Animals can be selected in **Animals** widget.
2. The Second step is the outliers removal in the *Outliers* pipe operator. This unit can be activated/deactivated in the
   **Outliers** widget (see details below).
3. The Last step in the preprocessing data pipeline is *time binning* operation.

> **Note**: If you observe some strange results during your analysis, please check that proper animals are selected in **Animals** widget!
{style='note'}
