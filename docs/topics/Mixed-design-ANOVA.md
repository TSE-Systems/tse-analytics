# Mixed-design ANOVA

Mixed-design ANOVA can be used to determine the effects of within-subject factors (see repeated measure ANOVA) and between-subject factors (see one-way and N-way ANOVA) as well as their interactions on a dependent variable. 

In TSE Analytics, (two-way) mixed-design ANOVA is performed using the within-subject factor “time bin” (depending on the selected time binning settings) and one between-subject factor as determined in the factors list.
To perform mixed-design ANOVA, select the respective data set from the *Add widget* and choose **Mixed-design ANOVA** as the analysis **Mode** in the AN(C)OVA control panel. 

![Figure: Mixed-design ANVOVA widget](Mixed-design ANVOVA widget.png)

**Apply (Time) Binning** using the binning mode which defines the repeated measures, i.e. bins, of interest.
Select a between-subject factor from the **Factors** list and choose a variable from the **Dependent Variable** list.
If needed, a **P-values adjustment** method and **Effect size type** can be selected from the respective dropdown menu.
Analysis results are calculated according to the selected settings by clicking **Update**.

> **Note**: Mixed-design ANOVA can only be performed if **Time Binning** is applied.
{style = 'note'}

Analysis result tables for repeated measures ANOVA include:

![Figure: Sphericity test table](Sphericity test table.png)

**Sphericity test:**

- Sphericity: True, if data has the sphericity property.
- W: Test statistic
- Chi-square: Chi-square statistic
- DOF: Degrees of freedom
- p-value: p-value

![Figure: Mixed-design ANOVA table](Mixed-design ANOVA table.png)

**Mixed-design ANOVA:**

- Source: Names of the factors or interaction
- SS: Sum of squares
- DF1: Degrees of freedom (numerator)
- DF2: Degrees of freedom (denominator)
- MS: Mean squares
- F: F-value
- p-unc: Uncorrected p-value
- np2: Partial eta-squared effect sizes
- eps: Greenhouse-Geisser epsilon factor (= index of sphericity)

![Figure: Pairwise post-hoc tests table](Pairwise post-hoc tests table.png)

**Pairwise post-hoc tests:**

- Contrast: Factors or interaction
- A: Name of first measurement
- B: Name of second measurement
- mean(A): Mean of the second measurement
- std(A): Standard deviation of the second measurement
- mean(B): Mean of the second measurement
- std(B): Standard deviation of the second factor group
- Paired: Indicates whether the two measurements are paired or independent
- Parametric: Indicates if parametric tests were used
- T: T statistic
- dof: Degrees of freedom (only if parametric=True)
- alternative: Tail of the test
- p-unc: Uncorrected p-values
- p-corr: Corrected p-values
- p-adjust: p-values correction method
- BF10: Bayes Factor
- effect size type: Effect size as defined in “Effect size type” dropdown menu

> **Note**: Pairwise comparisons can only be calculated within time bins (comparing between-subject factors within individual time bins, but not comparing time bins within factor groups).
{style='note'}

> **Warning**: The time needed to calculate pairwise comparison results for mixed-design ANOVA increases with the number of time bins.
> In case of binning by time intervals, calculation of ANOVA results might take several minutes depending on the computer’s computing power.
> Therefore, when performing mixed-design ANOVA using time binning by time intervals, users can choose whether pairwise comparisons should be performed in a pop-up window.
{style = 'warning'}

![Figure: Pop-up window to decide on pairwise comparisons for mixed measures ANOVA for binning by time intervals](perform-pairwise-tests-dialog.png)
