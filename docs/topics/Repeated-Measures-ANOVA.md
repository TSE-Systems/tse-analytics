# Repeated Measures ANOVA

Repeated measures ANOVA is used to identify significant differences between the means of groups with the same subjects, for example for repeated measurements in the same animals at different time points. 

To perform repeated measures ANOVA using the within-subject factor “time bin” without additional between-subject factors, select the respective data set from the *Add widget* and choose **Repeated measures ANOVA** as the analysis **Mode** in the AN(C)OVA control panel.
**Apply (Time) Binning** using the binning mode which defines the repeated measures, i.e. bins, and choose a variable from the **Dependent Variable** list.
If needed, select a **P-values adjustment** method or adjust the **Effect size type** via the dropdown menu.
Click **Update** to calculate analysis results and apply changes in the analysis settings.

![Figure: Repeated Measure ANOVA widget](Repeated Measure ANOVA widget.png)

> **Note**: Repeated measures ANOVA is only be performed if **Time Binning** is applied.
{style='note'}

Analysis result tables for repeated measures ANOVA include:

![Figure: Sphericity test table](Sphericity test table.png)

**Sphericity test:**

- Sphericity: True, if data has the sphericity property.
- W: Test statistic
- Chi-square: Chi-square statistic
- DOF: Degrees of freedom
- p-value: p-value

![Figure: Repeated measures one-way ANOVA table](Repeated measures one-way ANOVA table.png)

**Repeated measures one-way ANOVA:**

- Source: Name of the within-subject factor (“Bin”) or Error
- SS: Sums of squares
- DF: Degrees of freedom
- MS: Mean squares
- F: F-value
- p-unc: Uncorrected p-value
- p-GG-corr: Greenhouse-Geisser corrected p-value
- ng2: Generalized eta-square effect size
- eps: Greenhouse-Geisser epsilon factor (= index of sphericity)
- sphericity: Sphericity of the data (True / False)
- W-spher: Sphericity test statistic
- p-spher: p-value of the sphericity test

![Figure: Pairwise post-hoc tests table](Pairwise post-hoc tests table.png)

**Pairwise post-hoc tests:**

- Contrast: Within-subject factor (“Bin”)
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

> **Warning**: The time needed to calculate pairwise comparison results for repeated measures ANOVA increases with the number of time bins.
> In case of binning by time intervals, calculation of ANOVA results might take several minutes depending on the computer’s computing power. 
>
> Therefore, when performing repeated measures ANOVA using time binning by time intervals, users can choose whether pairwise comparisons should be performed in a pop-up window.
{style = 'warning'}

![Figure: Pop-up window to decide on pairwise comparisons for repeated measures ANOVA for binning by time intervals](perform-pairwise-tests-dialog.png)
