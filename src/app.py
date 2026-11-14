import matplotlib.pyplot as plt
import streamlit as st

from analysis import analyze_trend, compute_monthly_anomalies
from catalog import VARIABLE_CATALOG
from loaders import load_giovanni_csv
from verdict import build_verdict

st.title("Trend Detective")
st.caption("Is this Earth science variable changing, where, and by how much?")

uploaded_file = st.file_uploader("Upload a Giovanni time-series CSV", type="csv")
if uploaded_file is None:
    st.info("Export a monthly area-averaged time series from Giovanni and upload it here.")
    st.stop()

monthly_series, metadata = load_giovanni_csv(uploaded_file)
variable_info = VARIABLE_CATALOG.get(
    metadata["variable_id"],
    {"name": metadata["title"], "units": "units", "definition": ""},
)

monthly_anomalies = compute_monthly_anomalies(monthly_series)
trend_result = analyze_trend(monthly_anomalies)

if variable_info["definition"]:
    st.markdown(f"**What is it?** {variable_info['definition']}")

figure, (raw_axis, anomaly_axis) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
raw_axis.plot(monthly_series, color="gray")
raw_axis.set_title("Monthly values (seasonal cycle visible)")
anomaly_axis.plot(monthly_anomalies, color="tab:blue", label="Anomaly")
anomaly_axis.plot(trend_result["trend_line"], color="tab:red", label="Trend")
anomaly_axis.set_title("Seasonal cycle removed")
anomaly_axis.legend()
st.pyplot(figure)

st.markdown(
    build_verdict(
        variable_info["name"],
        variable_info["units"],
        trend_result,
        monthly_series.index.min().year,
        monthly_series.index.max().year,
    )
)

with st.expander("Statistical details"):
    st.json({key: value for key, value in trend_result.items() if key != "trend_line"})