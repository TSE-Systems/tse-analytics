# ANOVA

The **AN(C)OVA** widget offers multiple options for the Analysis of Variances (ANOVA) including One-Way ANOVA, N-Way ANOVA, repeated measures ANOVA, mixed design ANOVA and Analysis of Covariance (ANCOVA).

![Figure:AN(C)OVA widget](AN(C)OVA widget.png)

Settings for AN(C)OVA calculations can be adjusted in the control panel of the AN(C)OVA widget:
- The respective analysis (One-Way ANOVA, N-Way ANOVA, repeated measures ANOVA, mixed design ANOVA, ANCOVA) can be chosen under **ANCOVA**. 
- One factor (one-way ANOVA, mixed ANOVA, ANCOVA) or multiple factors (N-way ANOVA) can be selected from the **Factors** list. 
- The variable of interest is selected from the variables list under **Dependent Variable**. 
- For the calculation of effect sizes, the **Effect size type** can be selected from the respective dropdown menu. The available effect size types are: unbiased Cohen d, Hedges g, eta-square, odds ratio, area under the curve and common language effect size. 
- A dropdown menu to choose a method for **P-value adjustment** is available for N-way ANOVA, repeated measures ANOVA, mixed-design ANOVA and ANCOVA. Different methods for p-value adjustment include one-step Bonferroni, one-step Sidak, step-down Bonferroni, Benjamini/Hochberg FDR (false discovery rate) and Benjamini/Yekutieli FDR (false discovery rate). 

![Figure:AN(C)OVA methods selecting](AN(C)OVA methods selecting.png)

> **Note**: For one-way ANOVA, p-value correction of pairwise comparisons is determined by the type of ANOVA (depending on homoscedasticity) and cannot be adjusted manually.
> 
> P-value adjustment is only applied in the case of more than one pairwise comparison.
{style='note'}
  
To show ANOVA results or to apply changes, click **Update** in the control panel. Result tables will not update automatically.

ANOVA results as displayed in the AN(C)OVA widget can be added to the report by clicking **Add to Report** in the control panel.

> **Warning**: Only animals selected in the Animal list are considered for the calculation of AN(C)OVA analysis results in the AN(C)OVA widget.
> Changes regarding the selection of animals are only applied after clicking **Update**.
{style = 'warning'}

Besides adding AN(C)OVA results to the report, TSE Analytics does not offer a dedicated export function for AN(C)OVA results.
However, results can be saved outside of TSE Analytics via copy and paste.
All analysis results can be selected by clicking on the data table and pressing <shortcut>Ctrl+A</shortcut> on the keyboard or by right-clicking on the analysis window and selecting **Select All**.
Selected content can then be copied to the clipboard using <shortcut>Ctrl+C</shortcut> or by right-clicking on the analysis window again and selecting **Copy**.
Content copied to the clipboard can then be pasted and saved outside of TSE Analytics.

![Figure: copy-paste report](copy-paste.png)







 





