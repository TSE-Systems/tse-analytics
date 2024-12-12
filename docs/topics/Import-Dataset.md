# Import Dataset

## Export data from PhenoMaster software

TSE Analytics only supports TSE Dataset files (.tse), which are experimental date files exported from PhenoMaster Specific Software Version.

[//]: # (TODO: Explanation and screenshots on how to export datafiles from phenomaster and which specific version from PhenoMaster)

## Import Data into TSE Analytics

Datasets exported from PhenoMaster Software as described above (file ending * **.tse**)can be imported into TSE Analytics via **File | Import Dataset** in the header or via the Import Dataset button.
The * **.tse** dataset exported from the PhenoMaster software can then be selected in the File Explorer and is loaded into TSE Analytics upon clicking **Open**.

![Figure: Import dataset](Import dataset.png)

After successful import, the dataset will appear in the Dataset widget. The dataset will only be displayed if the Dataset widget is activated (indicated by checked tick box) under **View**.

![Figure: Activation of Dataset](Activation of Dataset.png)

**Multiple datasets** can be imported into TSE Analytics one after the other, but not simultaneously.
Each dataset that has been loaded into TSE Analytics becomes part of the current Workspace and contains a set of individual settings. 

All relevant metadata, such as sampling intervals, animal information and variables list are extracted automatically during import individually for each dataset. 

There is no limit to the number of datasets that can be loaded into a workspace. 

A dataset can be selected for data processing and analysis by clicking on the respective dataset in the Dataset widget.
The active dataset is then highlighted in blue, and all other widgets will be updated accordingly. 

![Figure: Multiple datasets selection](Multiple datasets selection.png)

> **Note**: Only one dataset can be active (highlighted in blue) at one time in the workspace.
{style='note'}
