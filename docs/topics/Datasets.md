# Datasets

**Data processing in the Dataset Widget**

Several tools for editing and preprocessing a selected dataset are available in the header of the Dataset widget. Those include **adjusting** a dataset in the Adjust Dataset window, **removing** a dataset from the Dataset widget, creating a copy (**cloning**) of a dataset and **merging** of datasets.

![Figure: Dataset widget](Dataset widget.png)


## Adjust

The _Adjust Dataset_ window offers multipe tools for editing a dataset and selecting time phases and animals of interest. To open the _Adjust Dataset_ window, select the respective dataset from the dataset list (selected dataset highlighted in blue) and and click **Adjust** in the _Dataset_ header.

![Figure: Adjust button in the header of the dataset widget](Adjust button in the header of the dataset widget.png)

![Figure: Adjust dataset window](Adjust dataset window.png)

To select and activate a tool for editing the dataset, tick the checkbox of the respective tool. Available operations are:

- **Rename**: The dataset can be renamed by entering a new dataset name in the text field underneath.

![Figure: Rename dataset](Rename dataset.png)

- **Apply resampling**: A new sample interval can be defined by typing in a new time interval using the format ‘hh:mm:ss’ or by using the arrows on the right.

![Figure: Apply resampling](Apply resampling.png)

> **Note**: New sample intervals cannot be shorter than the original sample interval during the measurement.
{style = 'note'}

- **Apply time shift**: The time stamps of an experiment can be shifted forward (into the future) by selecting ‘+’ (plus) or backwards (into the past) by selecting ‘-‘ (minus). The time shift can be defined as a custom number of days and/or hours, minutes and seconds.

![Figure: Apply time shift](Apply time shift.png)

> **Note**: Adjusting the time will directly change the time stamps in the raw data table used by TSE Analytics and thereby manipulate your data and results artificially. Please only use this option if you have a particular reason to do so, e.g. if the time stamp in the original data file does not match the actual date or time of the experiment.
{style = 'note'}

- **Trim time**: The date and time of the start and the end of a dataset can be changed here to shorten the time span covered by the dataset. Thereby, data from the beginning and the end of an experiment can be excluded.

![Figure: Trim time](Trim time.png)

> **Note**: The start time cannot be a time before the actual start of the experiment and the end time cannot be a time after the actual end of the experiment.
{style = 'note'}

The example below shows time trimming via the exclusion of a time phase at the beginning of an experiment (changing the start time).

![Figure: Example for trimming before (left) abd after (right) the exclusion of a time phase at the beginning of the experiment](Example for trimming before (left) abd after (right) the exclusion of a time phase at the beginning of the experiment.png)

- **Exclude time**: A custom time phase (at the beginning, the end or in the middle of an experiment) can be excluded by defining the start and the end time of the time phase that should be excluded.

![Figure: Exclude time](Exclude time.png)

> **Note**: It is not possible to enter a start time for the excluded time phase that lies before the beginning of the experiment or after the end of the excluded time phase. The end time for the excluded time phase cannot be a date or time after the end of the experiment or before the start time of the excluded time phase.
{style = 'note'}

- **Exclude animals**: Animals which should be permanently excluded from the dataset together with all associated data can be selected from the animals list. Selected animals are highlighted in blue.

![Figure: Exclude animals (animals to be excluded highlighted in blue](Exclude animals (animals to be excluded highlighted in blue.png)

To apply changes specified in the _Adjust Dataset_ window to the selected dataset, click **OK**.

> **Warning**: Changes regarding the trimming or exclusion of time phases as well as exclusion of animals cannot be undone once thay have been applied (by clicking **OK**). It is recommended to create a clone of a dataset before making adjustments as a backup.
{style='warning'}

> **Note**: All changes made via the _Adjust Dataset_ window will only be applied to the dataset within TSE Analytics but do not affect the original dataset stored outside of TSE Analytics.
{style='note'}


## Remove

To remove a dataset, select the respective dataset from the dataset list (selected dataset highlighted in blue) and click **Remove** in the header of the _Dataset_ widget.
Click **Yes** in the popup window to confirm that the dataset should be removed.

![Figure: Removing a dataset](Removing a dataset.png)

> **Warning**: *Remove* will remove the chosen dataset including all changes, analysis results and reports permanently from the currently active workspace. Removed datasets cannot be restored.
{style='warning'}

>**Note:** *Remove* does not affect the original dataset stored outside of TSE analytics.
{style='note'}


## Clone

To create a copy of a dataset, select the respective dataset from the dataset list (selected dataset highlighted in blue) and click **Clone** in the header of the _Dataset_ widget. The name of the dataset clone can be changed in the pop-up window and is applied upon clicking **OK**. The default name for a dataset clone is ‘Clone of \[name of original dataset]’.

![Figure: Cloning a dataset](Cloning a dataset.png)

>**Note:** Cloning a dataset will apply all changes which have been applied to the original dataset also to the newly created clone. This affects the exclusion of animals and times, adjusting time, animal selection, factors, time binning settings, outlier detections settings, report, and analysis settings.
{style='note'}


## Merge

Two or more datasets can be merged by selecting the respective datasets in the _Dataset_ widget using the **tick boxes** on the left-hand side of the dataset list. To open the _Merge_ _Datasets_ dialogue window, click **Merge** in the header of the _Dataset_ widget.

> **Note**: The **Merge** button will only be active if two or more datasets are selected via tick boxes in the _Dataset_ widget.
{style='note'}

![Figure: Merging two or more datasets selected via tick boxes](Merging two or more datasets selected via tick boxes.png)

![Figure: Options for merging in the Merge Datasets dialogue window](Options for merging in the Merge Datasets dialogue window.png)

In this dialogue window, datasets can be adjusted individually via the **Adjust** button next to a dataset’s name to prepare and match all selected datasets for merging. Clicking **Adjust** opens the _Adjust Dataset_ window with the options to rename a dataset, apply resampling, apply time shift, trim time, exclude time and exclude animals for each dataset individually. Tools to adjust a dataset can be activated by checking the respective tick box.

![Figure: Adjust Dataset window for merging](Adjust Dataset window for merging.png)

- **Apply resampling** allows to manually change (increase) the duration of sampling intervals to match sampling intervals of multiple datasets for merging.

>**Note:** It is not possible to decrease the original sampling interval. Therefore, sampling interval needs to be adjusted to match with the dataset with the longest sampling interval.
{style='note'}

- **Apply time shift** can be used to shift the time stamps of an experiment forward (into the future) by selecting ‘+’ (plus) or backwards (into the past) by selecting ‘-’ (minus). The time shift can be defined as a custom number of days and/or hours, minutes and seconds.
-
- **Trim time** allows to shorten a dataset by adjusting the start and end time, and thereby matching the time frames and duration of individual experiments for merging.

>**Note**: The start time cannot be a time point before the original start time or after the entered end time. In the same way, the end time cannot be a time point before the entered start time or after the original end of the experiment.
{style='note'}

- **Exclude time** offers the possibility to exclude a customized time phase with a defined start and end time from the start, end or middle of a dataset to match the time frames of single datasets for merging.

> **Note**: It is not possible to enter a start time for the excluded time phase that lies before the beginning of the experiment or after the end of the excluded time phase. The end time for the excluded time phase cannot be a date or time after the end of the experiment or before the start time of the excluded time phase.
{style='note'}

- **Exclude animals** can be used to permanently remove selected animals from a dataset (animals selected to be removed are highlighted in blue). To apply changes defined in the _Adjust Dataset_ window to a dataset for merging, click **OK**.

>**Warning**: Changes regarding the trimming or exclusion of time phases as well as exclusion of animals cannot be undone once thay have been applied (by clicking **OK**).
{style='warning'}

>**Note**: Any changes applied to a dataset during the merging process will not affect the original dataset.
{style='note'}

In addition to adjusting datasets individually, settings for merging can be selected on the right-hand side of the _Merge Datasets_ dialogue window.

The name of the merged dataset can be entered in the upper right corner under **Merged dataset name** (the default name for merged datasets is the name of the first selected dataset plus the suffix “(merged)”.

Merging can be performed using either the “Continuous” or “Overlap” mode, which can be selected under **Merging Mode**.

![Figure: Merging mode](Merging mode.png)

- “**Continuous**” mode:

Datasets are merged under consideration of the absolute time data stamps (date and time of the experiment) and are displayed one after each other if experiments have been performed after each other.

- “**Overlap**” mode:

Datasets are merged under consideration of relative stamps, i.e. time delta since the start of the experiment, and aligned according to their time bins. Datasets are displayed within the same time frame.

> **Note**: If *Overlap* mode is selected, the option ‘Add run number as suffix in animal names’ is available and can be activated by ticking the check box. Activating this option during merging is necessary, if animal names of the individual datasets are identical.
{style='note'}

In addition, datasets can be merged as a single run (no differentiation between individual datasets after merging) or as individual runs (possibility to split merged dataset by run to distinguish between individual datasets during analysis). To merge datasets as a single run, the check box **Merge as a single run** needs to be ticked.

After adjusting settings in the _Merge Dataset_ dialogue window, click **OK** to create a merged dataset.

> **Warning**: Settings for merging and adjusting individual datasets cannot be changed anymore, once the merged dataset has been created. Please ensure all adjustments and settings have been chosen correctly before clicking OK.
{style='warning'}

> **Note**: Datasets can only be merged if the variables lists are identical.
> This applies to the individual variables contained in a dataset as well as variable settings specified in the _Variables_ widget (aggregation mode and selection of variables for outlier detection).
> In case of discrepancies between variable settings, aggregation modes and selection of variables for outlier detection can be reset to default by clicking **Reset** in the header of the _Variables_ widget.
{style='note'}
