# TSE Analytics


## Main Window

Main window of TSE Analytics is a host of multiple dockable widgets. Users may resize, move and organize the layout
of the main application window up to their liking. Users can hide/show some widgets by using **View** section
in the main menu.

The layout is saved when you quit application.

> Default layout may be restored by clicking **View - Reset Layout** menu item.

![vvf](../docs/main.png)


## Data organization in TSE Analytics

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
