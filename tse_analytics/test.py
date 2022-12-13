import pandas as pd
import pingouin as pg
import scipy.stats as stats

df = pd.read_csv("C:\\Users\\anton\\Downloads\\20220404.22001.Ferran\\DrinkFeed.csv", sep="\t")

# https://stackoverflow.com/questions/22127569/opposite-of-melt-in-python-pandas
x = df.pivot(index="DateTime", columns="BoxNo")["Drink"]

# stats f_oneway functions takes the groups as input and returns ANOVA F and p value
fvalue, pvalue = stats.f_oneway(x[1], x[2], x[3], x[4])
print(fvalue, pvalue)

aov = pg.anova(data=df, dv="Drink", between="BoxNo", detailed=True)
print(aov)

pt = pg.pairwise_tukey(dv="Drink", between="BoxNo", data=df)
print(pt)
