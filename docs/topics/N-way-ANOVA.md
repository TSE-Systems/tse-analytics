 # N-way ANOVA

N-way ANOVA can be used to determine the effects of two or more (between-subject) factors and their interactions on a (dependent) variable. 

To perform N-way ANOVA (Two-way ANOVA, Three-way ANOVA, Four-way ANOVA, …) in TSE Analytics, select the respective data set from the *Add widget* and choose **N-way ANOVA** as the analysis **Mode** in the AN(C)OVA control panel.
Select two or more factors from the **Factors** list and choose a variable from the **Dependent Variable** list.
If needed, select a **P-values adjustment** method or adjust the **Effect size type** via the dropdown menu.
Click **Update** to calculate results and apply changes in the analysis settings.

![Figure: N-way ANOVA widget](N-way ANOVA widget.png)

Analysis result tables for N-way ANOVA include:

![Figure: Two-way ANOVA analysis results table](Two-way ANOVA analysis results table.png)

**N-way ANOVA** (Two-way ANOVA, Three-way ANOVA, …):

- Source: Factor names or interactions
- SS: Sums of squares
- DF: Degrees of freedom
- MS: Mean squares
- F: F-values
- p-unc: uncorrected p-values
- np2: Partial eta-square effect sizes

![Figure: Pairwise post-hoc tests table](Pairwise post-hoc tests table.png)

**Pairwise post-hoc tests** (only for two-way ANOVA):

- Contrast: Factor (= independent variable) or interaction
- A: Name of first measurement
- B: Name of second measurement
- mean(A): Mean of the first measurement
- std(A): Standard deviation of the first measurement
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

> **Note**: N-way ANOVA is only performed if at least one animal is assigned to each possible combination of groups.
>
> Pairwise comparisons for N-way ANOVA are only performed for two factors (Two-way ANOVA).
> The pairwise comparisons table is not displayed for N-way ANOVA with more than two factors (Three-way ANOVA, Four-way ANOVA, …)
>
> Pairwise comparisons for two-way ANOVA are only performed within the factor which is listed first in the Factors list.
> The order of factors can be reversed by clicking on ‘Name’ in the header of the factors list.
{style='note'}