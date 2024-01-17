Time Series Decomposition is a technique to extract multiple types of variation from your dataset. There are three important components in the temporal data of a time series: seasonality, trend, and noise.

- **Seasonality** is a recurring movement that is present in your time series variable. For example, the temperature of a place will be higher in the summer months and lower in the winter months.
You could compute average monthly temperatures and use this seasonality as a basis for forecasting future values.
- **A trend** can be a long-term upward or downward pattern. In a temperature time series, a trend could be present due to global warming.
For example, on top of the summer/winter seasonality, you may well see a slight increase in average temperatures over time.
- **Noise** is the part of the variability in a time series that can neither be explained by seasonality nor by a trend.
When building models, you end up combining different components into a mathematical formula.
Two parts of such a formula can be seasonality and trend. A model that combines both will never represent the values of temperature perfectly: an error will always remain. This is represented by the noise factor.
