import numpy as np
import pandas as pd
from scipy.stats import f, ttest_ind, ttest_rel


def mixed_anova_manual(df, subject_col, between_col, within_col, dv_col):
    """
    Perform mixed ANOVA manually using scipy.stats

    Parameters:
    df: DataFrame with data
    subject_col: column name for subjects
    between_col: column name for between-subjects factor
    within_col: column name for within-subjects factor
    dv_col: column name for dependent variable
    """

    # Get unique values
    subjects = df[subject_col].unique()
    between_levels = df[between_col].unique()
    within_levels = df[within_col].unique()

    n_subjects = len(subjects)
    n_between = len(between_levels)
    n_within = len(within_levels)

    # Calculate means
    grand_mean = df[dv_col].mean()

    # Between-subjects effects
    between_means = df.groupby(between_col)[dv_col].mean()
    subject_means = df.groupby([subject_col, between_col])[dv_col].mean().reset_index()

    # Within-subjects effects
    within_means = df.groupby(within_col)[dv_col].mean()

    # Interaction means
    interaction_means = df.groupby([between_col, within_col])[dv_col].mean()

    # Calculate Sum of Squares

    # Total SS
    ss_total = ((df[dv_col] - grand_mean) ** 2).sum()

    # Between-subjects SS
    ss_between = 0
    for level in between_levels:
        n_level = len(df[df[between_col] == level][subject_col].unique())
        ss_between += n_level * n_within * (between_means[level] - grand_mean) ** 2

    # Within-subjects SS
    ss_within = 0
    for level in within_levels:
        n_level = n_subjects
        ss_within += n_level * (within_means[level] - grand_mean) ** 2

    # Interaction SS
    ss_interaction = 0
    for b_level in between_levels:
        for w_level in within_levels:
            n_cell = len(df[(df[between_col] == b_level) & (df[within_col] == w_level)][subject_col].unique())
            expected = between_means[b_level] + within_means[w_level] - grand_mean
            ss_interaction += n_cell * (interaction_means[b_level, w_level] - expected) ** 2

    # Error terms
    # Between-subjects error
    ss_error_between = 0
    for subject in subjects:
        subj_data = df[df[subject_col] == subject]
        subj_group = subj_data[between_col].iloc[0]
        subj_mean = subj_data[dv_col].mean()
        ss_error_between += (subj_mean - between_means[subj_group]) ** 2 * n_within

    # Within-subjects error
    ss_error_within = ss_total - ss_between - ss_within - ss_interaction - ss_error_between

    # Degrees of freedom
    df_between = n_between - 1
    df_within = n_within - 1
    df_interaction = df_between * df_within
    df_error_between = n_subjects - n_between
    df_error_within = (n_subjects - n_between) * (n_within - 1)
    df_total = n_subjects * n_within - 1

    # Mean squares
    ms_between = ss_between / df_between if df_between > 0 else 0
    ms_within = ss_within / df_within if df_within > 0 else 0
    ms_interaction = ss_interaction / df_interaction if df_interaction > 0 else 0
    ms_error_between = ss_error_between / df_error_between if df_error_between > 0 else 0
    ms_error_within = ss_error_within / df_error_within if df_error_within > 0 else 0

    # F-statistics
    f_between = ms_between / ms_error_between if ms_error_between > 0 else 0
    f_within = ms_within / ms_error_within if ms_error_within > 0 else 0
    f_interaction = ms_interaction / ms_error_within if ms_error_within > 0 else 0

    # P-values
    p_between = 1 - f.cdf(f_between, df_between, df_error_between) if f_between > 0 else 1
    p_within = 1 - f.cdf(f_within, df_within, df_error_within) if f_within > 0 else 1
    p_interaction = 1 - f.cdf(f_interaction, df_interaction, df_error_within) if f_interaction > 0 else 1

    # Create results table
    results = pd.DataFrame({
        'Source': ['Between (Group)', 'Within (Time)', 'Interaction', 'Error (Between)', 'Error (Within)'],
        'SS': [ss_between, ss_within, ss_interaction, ss_error_between, ss_error_within],
        'df': [df_between, df_within, df_interaction, df_error_between, df_error_within],
        'MS': [ms_between, ms_within, ms_interaction, ms_error_between, ms_error_within],
        'F': [f_between, f_within, f_interaction, np.nan, np.nan],
        'p-value': [p_between, p_within, p_interaction, np.nan, np.nan]
    })

    return results


def posthoc_tests(df, subject_col, between_col, within_col, dv_col):
    """
    Perform post-hoc tests for significant effects
    """

    print("POST-HOC TESTS")
    print("=" * 30)

    # Between-subjects post-hoc (if more than 2 groups)
    between_groups = df[between_col].unique()
    if len(between_groups) == 2:
        # Simple t-test between groups (averaged across time)
        group_means = df.groupby([subject_col, between_col])[dv_col].mean().reset_index()
        group1_data = group_means[group_means[between_col] == between_groups[0]][dv_col]
        group2_data = group_means[group_means[between_col] == between_groups[1]][dv_col]

        t_stat, p_val = ttest_ind(group1_data, group2_data)
        print(f"\nBetween-groups t-test:")
        print(f"{between_groups[0]} vs {between_groups[1]}: t={t_stat:.3f}, p={p_val:.3f}")

    # Within-subjects post-hoc (pairwise comparisons)
    within_levels = df[within_col].unique()
    print(f"\nWithin-subjects pairwise comparisons:")

    pivot_df = df.pivot_table(
        values=dv_col,
        index=subject_col,
        columns=within_col,
        aggfunc='mean'
    )

    for i, level1 in enumerate(within_levels):
        for level2 in within_levels[i + 1:]:
            t_stat, p_val = ttest_rel(pivot_df[level1], pivot_df[level2])
            print(f"{level1} vs {level2}: t={t_stat:.3f}, p={p_val:.3f}")

    # Simple effects analysis (effect of time within each group)
    print(f"\nSimple effects (Time within each Group):")
    for group in between_groups:
        group_data = df[df[between_col] == group]
        group_pivot = group_data.pivot_table(
            values=dv_col,
            index=subject_col,
            columns=within_col,
            aggfunc='mean'
        )

        print(f"\n{group} group:")
        for i, level1 in enumerate(within_levels):
            for level2 in within_levels[i + 1:]:
                t_stat, p_val = ttest_rel(group_pivot[level1], group_pivot[level2])
                print(f"  {level1} vs {level2}: t={t_stat:.3f}, p={p_val:.3f}")
