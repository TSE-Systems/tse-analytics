# One-way ANOVA


One-way ANOVA can be used to identify significant differences between the means of two or more groups of one factor.

To perform one-way ANOVA in TSE Analytics, select the respective data set from the *Add widget* and choose **One-way ANOVA** as the analysis **Mode** in the AN(C)OVA control panel.
Select one factor from the **Factors** list and choose a variable from the **Dependent Variable** list.
If needed, adjust the **Effect size type** via the dropdown menu. Click **Update** to calculate analysis results.

![Figure: One-way ANOVA widget](One-way ANOVA widget.png)

![Figure: One-way ANOVA anaysis results table](One-way ANOVA anaysis results table.png)

Analysis result tables for one-way ANOVA include:

**Univariate normality test** for normal distribution:

- W: Test statistic
- pval: p-value
- normal: True, if data is normally distributed / False if data is not normally distributed

**Homoscedasticity** (equality of variances)

- W: Test statistic
- pval: p-value
- equal_var: True, if data has equal variance / False, if data has unequal variance

In case of equal variances (equal_var = True):

**One-way classic ANOVA**

- Source: Factor names
- SS: Sums of squares
- DF: Degrees of freedom
- MS: Mean squares
- F: F-values
- p-unc: uncorrected p-values
- np2: Partial eta-square effect sizes

**Pairwise Tukey-HSD post-hoc test**

- A: Name of first measurement
- B: Name of second measurement
- mean(A): Mean of first measurement
- mean(B): Mean of second measurement
- diff: Mean difference (= mean(A) - mean(B))
- se: Standard error
- T: T-values
- p-tukey: Tukey-HSD corrected p-values
- effect size type: Effect size as defined in “Effect size type” dropdown menu

If equality of variances is not given (equal_var = False):

**One-way Welch ANOVA**

- Source: Factor names
- ddof1: Numerator degrees of freedom
- ddof2: Denominator degrees of freedom
- F: F-values
- p-unc: Uncorrected p-values
- np2: Partial eta-squared effect sizes

**Pairwise Games-Howell post-hoc test**

- A: Name of first measurement
- B: Name of second measurement
- mean(A): Mean of first measurement
- mean(B): Mean of second measurement
- diff: Mean difference (= mean(A) - mean(B))
- se: Standard error
- T: T-values
- df: Adjusted degrees of freedom
- pval: Games-Howell corrected p-values
- effect size type: Effect size as defined in “Effect size type” dropdown menu

**Multiple comparisons plot**

![Figure: Multiple comparisons plot](Multiple comparisons plot.png)

*The multiple comparisons plot* generated for one-way ANOVAs allows to graphically identify significant pairwise comparisons based on the Tukey HSD (Honestly Significant Difference) test statistic for multiple comparisons. The plot shows the means (dot) and confidence intervals (horizontal lines) of the selected variable for each factor group. Confidence intervals are calculated based on the respective Tukey’s q critical value, which is dependent on the confidence level, degrees of freedom and the number of groups. A statistically significant difference between two groups is given, if the respective confidence intervals do not overlap.

> **Note**: Graphical representation of confidence intervals is always based on the Tukey HSD test, independent of the pairwise comparison method applied to post-hoc test tables (Tukey HSD for one-way classic ANOVA and Games-Howell for one-way Welch ANOVA).
{style='note'}
