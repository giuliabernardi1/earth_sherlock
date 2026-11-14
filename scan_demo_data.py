# scan_demo_data.py
from pathlib import Path

import pandas as pd

from src.analysis import analyze_trend, compute_monthly_anomalies
from src.catalog import VARIABLE_CATALOG, apply_catalog_scaling
from src.loaders import load_giovanni_csv

scan_rows = []
for csv_path in sorted(Path("demo_data").glob("*__*.csv")):
    region_name, _, variable_label = csv_path.stem.partition("__")
    with open(csv_path, "rb") as csv_file:
        monthly_series, metadata = load_giovanni_csv(csv_file)

    variable_info = VARIABLE_CATALOG[metadata["variable_id"]]
    scaled_series = apply_catalog_scaling(monthly_series, variable_info)
    trend_result = analyze_trend(compute_monthly_anomalies(scaled_series))
    scan_rows.append({
        "region": region_name,
        "variable": variable_label,
        "units": variable_info["display_units"],
        "mean_value": scaled_series.mean(),
        "slope_per_decade": trend_result["theil_sen_slope_per_decade"],
        "ci_low": trend_result["ci_low_per_decade"],
        "ci_high": trend_result["ci_high_per_decade"],
        "worst_case_p": trend_result["worst_case_p_value"],
        "significant": trend_result["is_significant"],
    })

pd.set_option("display.width", 250)
print(pd.DataFrame(scan_rows).round(4).to_string(index=False))