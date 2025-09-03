import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy import stats

# Example: 3 factors (A, B, C) fully crossed, unbalanced on purpose
rng = np.random.default_rng(0)
n_per_cell = rng.integers(8, 15, size=(3, 3, 2))  # A=3 levels, B=3, C=2

rows = []
levels_A = ["low", "mid", "high"]
levels_B = ["X", "Y", "Z"]
levels_C = ["on", "off"]

for i, a in enumerate(levels_A):
    for j, b in enumerate(levels_B):
        for k, c in enumerate(levels_C):
            n = n_per_cell[i, j, k]
            # true means with interactions
            mu = 50 + 5 * i + 3 * j + (-4 if c == "on" else 0) + 2 * i * j + (3 if (i == 2 and c == "on") else 0)
            y = rng.normal(mu, 8, size=n)
            rows += [(val, a, b, c) for val in y]

df = pd.DataFrame(rows, columns=["Y", "AA", "BB", "CC"])
df["AA"] = df["AA"].astype("category")
df["BB"] = df["BB"].astype("category")
df["CC"] = df["CC"].astype("category")


# Full factorial up to three-way interaction
formula = "Y ~ C(AA)*C(BB)*C(CC)"
model = smf.ols(formula, data=df).fit()

anova2 = anova_lm(model, typ=2)
print(anova2)
