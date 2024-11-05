# AN(C)OVA widget

The **AN(C)OVA** widget offers multiple options for the Analysis of Variances (ANOVA) including One-Way ANOVA, N-Way ANOVA, repeated measures ANOVA, mixed design ANOVA and Analysis of Covariance (ANCOVA).

Settings for AN(C)OVA calculations can be adjusted in the control panel of the AN(C)OVA widget:
- The respective analysis (One-Way ANOVA, N-Way ANOVA, repeated measures ANOVA, mixed design ANOVA, ANCOVA) can be chosen under **Mode**. 
- One factor (one-way ANOVA, mixed ANOVA, ANCOVA) or multiple factors (N-way ANOVA) can be selected from the **Factors** list. 
- The variable of interest is selected from the variables list under **Dependent Variable**. 
- For the calculation of effect sizes, the **Effect size type** can be selected from the respective dropdown menu. The available effect size types are: unbiased Cohen d, Hedges g, eta-square, odds ratio, area under the curve and common language effect size. 
- A dropdown menu to choose a method for **P-value adjustment** is available for N-way ANOVA, repeated measures ANOVA, mixed-design ANOVA and ANCOVA. Different methods for p-value adjustment include one-step Bonferroni, one-step Sidak, step-down Bonferroni, Benjamini/Hochberg FDR (false discovery rate) and Benjamini/Yekutieli FDR (false discovery rate). 

> **Note:**
>- For one-way ANOVA, p-value correction of pairwise comparisons is determined by the type of ANOVA (depending on homoscedasticity) and cannot be adjusted manually.
>- P-value adjustment is only applied in the case of more than one pairwise comparison.
{style = 'note'}

To show ANOVA results or to apply changes, click **Update** in the control panel. Result tables will not update automatically.

ANOVA results as displayed in the AN(C)OVA widget can be added to the report by clicking **Add to Report** in the control panel.

>**Warning:** Only animals selected in the Animal list are considered for the calculation of AN(C)OVA analysis results in the AN(C)OVA widget. Changes regarding the selection of animals are only applied after clicking **Update**.
{style = 'warning'}

Besides adding AN(C)OVA results to the report, TSE Analytics does not offer a dedicated export function for AN(C)OVA results. However, results can be saved outside of TSE Analytics via “copy and paste”. All analysis results can be selected by clicking on the data table and pressing **Strg + A (Ctrl + A)** on the keyboard or by **right-clicking** on the analysis window and selecting **Select All**. Selected content can then be copied to the clipboard using **Strg + C (Ctrl + C)** or by right-clicking on the analysis window again and selecting **Copy**. Content copied to the clipboard can then be pasted and saved outside of TSE Analytics.

![copy-paste.png](copy-paste.png)


# One-Way ANOVA

One-way ANOVA can be used to identify significant differences between the means of two or more groups of one factor. To perform one-way ANOVA in TSE Analytics, select the respective data set from the Dataset widget and choose **One-way ANOVA** as the analysis **Mode** in the AN(C)OVA control panel. Select one factor from the **Factors** list and choose a variable from the **Dependent Variable** list. If needed, adjust the **Effect size type** via the dropdown menu. Click **Update** to calculate analysis results.

Analysis result tables for one-way ANOVA include:

Univariate normality test for normal distribution:
-	W: Test statistic
-	pval: p-value
-	normal: True, if data is normally distributed / False if data is not normally distributed

Levene test for homoscedasticity (equality of variances)
-	W: Test statistic
-	pval: p-value
-	equal_var: True, if data has equal variance / False, if data has unequal variance

In case of equal variances (equal_var = True): 

One-way classic ANOVA
-	Source: Factor names
-	SS: Sums of squares
-	DF: Degrees of freedom
-	MS: Mean squares
-	F: F-values
-	p-unc: uncorrected p-values
-	np2: Partial eta-square effect sizes

Pairwise Tukey-HSD post-hoc test
-	A: Name of first measurement
-	B: Name of second measurement
-	mean(A): Mean of first measurement
-	mean(B): Mean of second measurement
-	diff: Mean difference (= mean(A) - mean(B))
-	se: Standard error
-	T: T-values
-	p-tukey: Tukey-HSD corrected p-values
-	effect size type: Effect size as defined in “Effect size type” dropdown menu


If equality of variances is not given (equal_var = False):

One-way Welch ANOVA
-	Source: Factor names
-	ddof1: Numerator degrees of freedom
-	ddof2: Denominator degrees of freedom
-	F: F-values
-	p-unc: Uncorrected p-values
-	np2: Partial eta-squared effect sizes

Pairwise Games-Howell post-hoc test
-	A: Name of first measurement
-	B: Name of second measurement
-	mean(A): Mean of first measurement
-	mean(B): Mean of second measurement
-	diff: Mean difference (= mean(A) - mean(B))
-	se: Standard error
-	T: T-values
-	df: Adjusted degrees of freedom 
-	pval: Games-Howell corrected p-values
-	effect size type: Effect size as defined in “Effect size type” dropdown menu



Multiple comparisons plot:

The multiple comparisons plot generated for one-way ANOVAs allows to graphically identify significant pairwise comparisons based on the Tukey HSD (Honestly Significant Difference) test statistic for multiple comparisons. The plot shows the means (dot) and confidence intervals (horizontal lines) of the selected variable for each factor group. Confidence intervals are calculated based on the respective Tukey’s q critical value, which is dependent on the confidence level, degrees of freedom and the number of groups. A statistically significant difference between two groups is given, if the respective confidence intervals do not overlap.

![tukey-pairwise-plot.png](tukey-pairwise-plot.png)

> **Note:** Graphical representation of confidence intervals is always based on the Tukey HSD test, independent of the pairwise comparison method applied to post-hoc test tables (Tukey HSD for one-way classic ANOVA and Games-Howell for one-way Welch ANOVA).
{style = 'note'}


# N-Way ANOVA

N-way ANOVA can be used to determine the effects of two or more (between-subject) factors and their interactions on a (dependent) variable. To perform N-way ANOVA (Two-way ANOVA, Three-way ANOVA, Four-way ANOVA, …) in TSE Analytics, select the respective data set from the Dataset widget and choose **N-way ANOVA** as the analysis **Mode** in the AN(C)OVA control panel. Select two or more factors from the **Factors** list and choose a variable from the **Dependent Variable** list. If needed, select a **P-values adjustment** method or adjust the **Effect size type** via the dropdown menu. Click **Update** to calculate results and apply changes in the analysis settings.

Analysis result tables for N-way ANOVA include:

N-way ANOVA (Two-way ANOVA, Three-way ANOVA, …):
-	Source: Factor names or interactions
-	SS: Sums of squares
-	DF: Degrees of freedom
-	MS: Mean squares
-	F: F-values
-	p-unc: uncorrected p-values
-	np2: Partial eta-square effect sizes

Pairwise post-hoc tests (only for two-way ANOVA):
-	Contrast: Factor (= independent variable) or interaction
-	A: Name of first measurement
-	B: Name of second measurement 
-	mean(A): Mean of the first measurement 
-	std(A): Standard deviation of the first measurement
-	mean(B): Mean of the second measurement
-	std(B): Standard deviation of the second factor group 
-	Paired: Indicates whether the two measurements are paired or independent
-	Parametric: Indicates if parametric tests were used
-	T: T statistic
-	dof: Degrees of freedom (only if parametric=True)
-	alternative: Tail of the test
-	p-unc: Uncorrected p-values
-	p-corr: Corrected p-values
-	p-adjust: p-values correction method
-	BF10: Bayes Factor
-	effect size type: Effect size as defined in “Effect size type” dropdown menu

> **Note:** 
>- N-way ANOVA is only performed if at least one animal is assigned to each possible combination of groups.  
>- Pairwise comparisons for N-way ANOVA are only performed for two factors (Two-way ANOVA). The pairwise comparisons table is not displayed for N-way ANOVA with more than two factors (Three-way ANOVA, Four-way ANOVA, …)
>- Pairwise comparisons for two-way ANOVA are only performed within the factor which is listed first in the Factors list. The order of factors can be reversed by clicking on ‘Name’ in the header of the factors list.
{style = 'note'}


# Repeated measures ANOVA

Repeated measures ANOVA is used to identify significant differences between the means of groups with the same subjects, for example for repeated measurements in the same animals at different time points. To perform repeated measures ANOVA using the within-subject factor “time bin” without additional between-subject factors, select the respective data set from the Dataset widget and choose **Repeated measures ANOVA** as the analysis **Mode** in the AN(C)OVA control panel. **Apply (Time) Binning** using the binning mode which defines the repeated measures, i.e. bins, and choose a variable from the **Dependent Variable** list. If needed, select a **P-values adjustment** method or adjust the **Effect size type** via the dropdown menu. Click **Update** to calculate analysis results and apply changes in the analysis settings.

**Note:** Repeated measures ANOVA is only be performed if **Time Binning** is applied. 

Analysis result tables for repeated measures ANOVA include:

Sphericity test:
-	Sphericity: True, if data has the sphericity property.
-	W: Test statistic
-	Chi-square: Chi-square statistic
-	DOF: Degrees of freedom
-	p-value: p-value

Repeated measures one-way ANOVA:
-	Source: Name of the within-subject factor (“Bin”) or Error
-	SS: Sums of squares
-	DF: Degrees of freedom
-	MS: Mean squares
-	F: F-value
-	p-unc: Uncorrected p-value
-	p-GG-corr: Greenhouse-Geisser corrected p-value
-	ng2: Generalized eta-square effect size
-	eps: Greenhouse-Geisser epsilon factor (= index of sphericity)
-	sphericity: Sphericity of the data (True / False)
-	W-spher: Sphericity test statistic
-	p-spher: p-value of the sphericity test

Pairwise post-hoc tests:
-	Contrast: Within-subject factor (“Bin”)
-	A: Name of first measurement
-	B: Name of second measurement
-	mean(A): Mean of the second measurement
-	std(A): Standard deviation of the second measurement
-	mean(B): Mean of the second measurement
-	std(B): Standard deviation of the second factor group
-	Paired: Indicates whether the two measurements are paired or independent
-	Parametric: Indicates if parametric tests were used
-	T: T statistic
-	dof: Degrees of freedom (only if parametric=True)
-	alternative: Tail of the test
-	p-unc: Uncorrected p-values
-	p-corr: Corrected p-values
-	p-adjust: p-values correction method
-	BF10: Bayes Factor
-	effect size type: Effect size as defined in “Effect size type” dropdown menu

> **Warning:** The time needed to calculate pairwise comparison results for repeated measures ANOVA increases with the number of time bins. In case of binning by time intervals, calculation of ANOVA results might take several minutes depending on the computer’s computing power. Therefore, when performing repeated measures ANOVA using time binning by time intervals, users can choose whether pairwise comparisons should be performed in a pop-up window.
{style = 'warning'}

![perform-pairwise-tests-dialog.png](perform-pairwise-tests-dialog.png)


# Mixed-design ANOVA

Mixed-design ANOVA can be used to determine the effects of within-subject factors (see repeated measure ANOVA) and between-subject factors (see one-way and N-way ANOVA) as well as their interactions on a dependent variable. In TSE Analytics, (two-way) mixed-design ANOVA is performed using the within-subject factor “time bin” (depending on the selected time binning settings) and one between-subject factor as determined in the factors list. To perform mixed-design ANOVA, select the respective data set from the Dataset widget and choose **Mixed-design ANOVA** as the analysis **Mode** in the AN(C)OVA control panel. **Apply (Time) Binning** using the binning mode which defines the repeated measures, i.e. bins, of interest. Select a between-subject factor from the **Factors** list and choose a variable from the **Dependent Variable** list. If needed, a **P-values adjustment** method and **Effect size type** can be selected from the respective dropdown menu. Analysis results are calculated according to the selected settings by clicking **Update**.

>**Note:** Mixed-design ANOVA can only be performed if **Time Binning** is applied. 
{style = 'note'}
>
Analysis result tables for repeated measures ANOVA include:

Sphericity test:
-	Sphericity: True, if data has the sphericity property.
-	W: Test statistic
-	Chi-square: Chi-square statistic
-	DOF: Degrees of freedom
-	p-value: p-value

Mixed-design ANOVA:
-	Source: Names of the factors or interaction
-	SS: Sum of squares
-	DF1: Degrees of freedom (numerator)
-	DF2: Degrees of freedom (denominator)
-	MS: Mean squares
-	F: F-value
-	p-unc: Uncorrected p-value
-	np2: Partial eta-squared effect sizes
-	eps: Greenhouse-Geisser epsilon factor (= index of sphericity)

Pairwise post-hoc tests:
-	Contrast: Factors or interaction
-	A: Name of first measurement
-	B: Name of second measurement
-	mean(A): Mean of the second measurement
-	std(A): Standard deviation of the second measurement
-	mean(B): Mean of the second measurement
-	std(B): Standard deviation of the second factor group
-	Paired: Indicates whether the two measurements are paired or independent
-	Parametric: Indicates if parametric tests were used
-	T: T statistic
-	dof: Degrees of freedom (only if parametric=True)
-	alternative: Tail of the test
-	p-unc: Uncorrected p-values
-	p-corr: Corrected p-values
-	p-adjust: p-values correction method
-	BF10: Bayes Factor
-	effect size type: Effect size as defined in “Effect size type” dropdown menu

> **Note**: Pairwise comparisons can only be calculated within time bins (comparing between-subject factors within individual time bins, but not comparing time bins within factor groups).
{style = 'note'}

> **Warning**: The time needed to calculate pairwise comparison results for mixed-design ANOVA increases with the number of time bins. In case of binning by time intervals, calculation of ANOVA results might take several minutes depending on the computer’s computing power. Therefore, when performing mixed-design ANOVA using time binning by time intervals, users can choose whether pairwise comparisons should be performed in a pop-up window.
{style = 'warning'}

![perform-pairwise-tests-dialog.png](perform-pairwise-tests-dialog.png)


# Analysis of Covariance (ANCOVA)

Analysis of Covariance (ANCOVA) allows testing for statistical differences between two or more groups while at the same time controlling for the effects of covariate variables on the dependent variable, thereby combining ANOVA and regression analysis. To perform ANCOVA in TSE Analytics, select the respective data set from the Dataset widget and choose **ANCOVA** as the analysis **Mode** in the AN(C)OVA control panel. Select a factor from the **Factors** list, choose a dependent variable from the **Dependent Variable** list and select one or multiple covariate variables from the **Covariate** list (must bot be the dependent variable) If needed, a **P-values adjustment** method and **Effect size type** can be selected from the respective dropdown menu. Analysis results are calculated according to the selected settings by clicking **Update**.

Analysis result tables for ANCOVA include:

ANCOVA:
-	Source: Names of the factors considered
-	SS: Sums of squares
-	DF: Degrees of freedom
-	F: F-values
-	p-unc: Uncorrected p-values
-	np2: Partial eta-squared

Pairwise post-hoc tests:
-	Contrast: Factor (=independent variable)
-	A: Name of first measurement
-	B: Name of second measurement
-	mean(A): Mean of the second measurement
-	std(A): Standard deviation of the second measurement
-	mean(B): Mean of the second measurement
-	std(B): Standard deviation of the second factor group
-	Paired: Indicates whether the two measurements are paired or independent
-	Parametric: Indicates if parametric tests were used
-	T: T statistic
-	dof: Degrees of freedom (only if parametric=True)
-	alternative: Tail of the test
-	p-unc: Uncorrected p-values
-	p-corr: Corrected p-values
-	p-adjust: p-values correction method
-	BF10: Bayes Factor
-	effect size type: Effect size as defined in “Effect size type” dropdown menu

 





