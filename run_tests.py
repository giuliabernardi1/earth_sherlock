import matplotlib.pyplot as plt

from src.analysis import analyze_trend, compute_monthly_anomalies
from src.loaders import load_giovanni_csv

with open("data/italy_temp_15_25.csv", "rb") as csv_file:
    monthly_series, metadata = load_giovanni_csv(csv_file)

monthly_anomalies = compute_monthly_anomalies(monthly_series)
trend_result = analyze_trend(monthly_anomalies)

print(metadata["title"])
for key, value in trend_result.items():
    if key != "trend_line":
        print(f"{key}: {value:.4f}" if isinstance(value, float) else f"{key}: {value}")

figure, (raw_axis, anomaly_axis) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
raw_axis.plot(monthly_series, color="gray")
raw_axis.set_title("Raw monthly series (K)")
anomaly_axis.plot(monthly_anomalies, color="tab:blue", label="Monthly anomaly")
anomaly_axis.plot(trend_result["trend_line"], color="tab:red", label="Theil-Sen trend")
anomaly_axis.set_title("Seasonally adjusted anomaly (K)")
anomaly_axis.legend()
plt.tight_layout()
plt.show()