import pandas as pd
import pymannkendall as mk
from scipy import stats

DAYS_PER_YEAR = 365.25


def compute_monthly_anomalies(time_series: pd.Series) -> pd.Series:
    """Remove the seasonal cycle by subtracting each calendar month's mean."""
    monthly_climatology = time_series.groupby(time_series.index.month).transform("mean")
    return time_series - monthly_climatology


def analyze_trend(anomaly_series: pd.Series) -> dict:
    valid_series = anomaly_series.dropna()
    years_elapsed = ((valid_series.index - valid_series.index[0]).days / DAYS_PER_YEAR).to_numpy()
    values = valid_series.to_numpy()

    ols_result = stats.linregress(years_elapsed, values)
    theil_sen_slope, theil_sen_intercept, slope_ci_low, slope_ci_high = stats.theilslopes(
        values, years_elapsed
    )
    classic_mann_kendall = mk.original_test(values)
    corrected_mann_kendall = mk.hamed_rao_modification_test(values)

    return {
        "number_of_months": len(values),
        "number_of_years": years_elapsed[-1],
        "ols_slope_per_decade": ols_result.slope * 10,
        "theil_sen_slope_per_decade": theil_sen_slope * 10,
        "ci_low_per_decade": slope_ci_low * 10,
        "ci_high_per_decade": slope_ci_high * 10,
        "ols_p_value": ols_result.pvalue,
        "mann_kendall_p_value": classic_mann_kendall.p,
        "corrected_p_value": corrected_mann_kendall.p,
        "is_significant": corrected_mann_kendall.p < 0.05,
        "trend_line": pd.Series(
            theil_sen_intercept + theil_sen_slope * years_elapsed, index=valid_series.index
        ),
    }