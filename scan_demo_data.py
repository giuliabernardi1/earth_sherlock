from pathlib import Path

import pandas as pd

from src.analysis import analyze_trend, compute_monthly_anomalies
from src.loaders import load_giovanni_csv

DEMO_DATA_DIRECTORY = Path("data")

scan_rows = []
for csv_path in sorted(DEMO_DATA_DIRECTORY.glob("*.csv")):
    variable_label, _, region_name,= csv_path.stem.partition("_")
    with open(csv_path, "rb") as csv_file:
        monthly_series, metadata = load_giovanni_csv(csv_file)

    trend_result = analyze_trend(compute_monthly_anomalies(monthly_series))
    scan_rows.append(
        {
            "region": region_name,
            "variable": variable_label,
            "variable_id": metadata["variable_id"],
            "mean_value": monthly_series.mean(),
            "slope_per_decade": trend_result["theil_sen_slope_per_decade"],
            "ci_low": trend_result["ci_low_per_decade"],
            "ci_high": trend_result["ci_high_per_decade"],
            "worst_case_p": trend_result["worst_case_p_value"],
            "significant": trend_result["is_significant"],
            "missing_months": int(monthly_series.isna().sum()),
        }
    )

scan_table = pd.DataFrame(scan_rows)
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", None)
print(scan_table.round(6).to_string(index=False))