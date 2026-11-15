from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

from analysis import analyze_trend, compare_two_regions, compute_monthly_anomalies
from catalog import (
    DEMO_FILE_KEYS,
    TOPIC_QUESTIONS,
    VARIABLE_CATALOG,
    apply_catalog_scaling,
)
from loaders import load_giovanni_csv
from styling import REGION_COLORS, apply_custom_style, render_hero, render_metrics, show_verdict
from verdict import build_comparison_verdict, build_verdict

DEMO_DIRECTORY = Path("demo_data")
UNKNOWN_VARIABLE_INFO = {
    "name": None,
    "display_units": "units",
    "scale_factor": 1.0,
    "offset": 0.0,
    "definition": "",
}


# ---------- Helpers ----------

def get_variable_info(metadata: dict) -> dict:
    """Catalog entry for the uploaded variable, or a neutral fallback."""
    variable_info = dict(VARIABLE_CATALOG.get(metadata["variable_id"], UNKNOWN_VARIABLE_INFO))
    if variable_info["name"] is None:
        variable_info["name"] = metadata["title"]
    return variable_info


def render_single_region(monthly_series, variable_info: dict) -> None:
    scaled_series = apply_catalog_scaling(monthly_series, variable_info)
    monthly_anomalies = compute_monthly_anomalies(scaled_series)
    trend_result = analyze_trend(monthly_anomalies)

    if variable_info["definition"]:
        st.markdown(f"**What is it?** {variable_info['definition']}")

    figure, (raw_axis, anomaly_axis) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    raw_axis.plot(scaled_series, color="gray")
    raw_axis.set_title("Monthly values (seasonal cycle visible)")
    raw_axis.set_ylabel(variable_info["display_units"])
    anomaly_axis.plot(monthly_anomalies, color="tab:blue", label="Anomaly")
    anomaly_axis.plot(trend_result["trend_line"], color="tab:red", label="Trend")
    anomaly_axis.set_title("Seasonal cycle removed")
    anomaly_axis.set_ylabel(variable_info["display_units"])
    anomaly_axis.legend()
    st.pyplot(figure)

    st.markdown(
        build_verdict(
            variable_info["name"],
            variable_info["display_units"],
            trend_result,
            scaled_series.index.min().year,
            scaled_series.index.max().year,
        )
    )
    with st.expander("Statistical details"):
        st.json({key: value for key, value in trend_result.items() if key != "trend_line"})


def render_comparison(first_series, second_series, first_label, second_label, variable_info: dict) -> None:
    scaled_first_series = apply_catalog_scaling(first_series, variable_info)
    scaled_second_series = apply_catalog_scaling(second_series, variable_info)
    first_result, second_result = compare_two_regions(scaled_first_series, scaled_second_series)

    if variable_info["definition"]:
        st.markdown(f"**What is it?** {variable_info['definition']}")

    figure, axis = plt.subplots(figsize=(10, 4))
    for series, result, label, color in [
        (scaled_first_series, first_result, first_label, "tab:red"),
        (scaled_second_series, second_result, second_label, "tab:blue"),
    ]:
        axis.plot(compute_monthly_anomalies(series), color=color, alpha=0.4)
        axis.plot(result["trend_line"], color=color, linewidth=2, label=label)
    axis.set_ylabel(f"Anomaly ({variable_info['display_units']})")
    axis.legend()
    st.pyplot(figure)

    st.markdown(
        build_comparison_verdict(
            first_label, second_label, first_result, second_result,
            variable_info["display_units"],
        )
    )
    with st.expander("Statistical details"):
        st.write(first_label)
        st.json({key: value for key, value in first_result.items() if key != "trend_line"})
        st.write(second_label)
        st.json({key: value for key, value in second_result.items() if key != "trend_line"})

#---------- Styling ----------
def render_single_region(monthly_series, variable_info: dict) -> None:
    scaled_series = apply_catalog_scaling(monthly_series, variable_info)
    monthly_anomalies = compute_monthly_anomalies(scaled_series)
    trend_result = analyze_trend(monthly_anomalies)
    units = variable_info["display_units"]

    if variable_info["definition"]:
        st.caption(f"**What is it?** {variable_info['definition']}")

    render_metrics(trend_result, units)

    figure, (raw_axis, anomaly_axis) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    raw_axis.plot(scaled_series, color="#8a8f98", linewidth=1.5)
    raw_axis.set_title("Monthly values (seasonal cycle visible)")
    raw_axis.set_ylabel(units)
    anomaly_axis.axhline(0, color="#0f1b2d", linewidth=0.8, alpha=0.5)
    anomaly_axis.plot(monthly_anomalies, color=REGION_COLORS["first"], alpha=0.45, label="Monthly anomaly")
    anomaly_axis.plot(trend_result["trend_line"], color="#0f1b2d", linewidth=3, label="Trend")
    anomaly_axis.set_title("Seasonal cycle removed")
    anomaly_axis.set_ylabel(units)
    anomaly_axis.legend(frameon=False)
    figure.tight_layout()
    st.pyplot(figure)

    verdict_text = build_verdict(
        variable_info["name"], units, trend_result,
        scaled_series.index.min().year, scaled_series.index.max().year,
    )
    show_verdict(verdict_text, trend_result["is_significant"])
    with st.expander("Statistical details"):
        st.json({key: value for key, value in trend_result.items() if key != "trend_line"})


def render_comparison(first_series, second_series, first_label, second_label, variable_info: dict) -> None:
    scaled_first_series = apply_catalog_scaling(first_series, variable_info)
    scaled_second_series = apply_catalog_scaling(second_series, variable_info)
    first_result, second_result = compare_two_regions(scaled_first_series, scaled_second_series)
    units = variable_info["display_units"]

    if variable_info["definition"]:
        st.caption(f"**What is it?** {variable_info['definition']}")

    for label, result in [(first_label, first_result), (second_label, second_result)]:
        st.markdown(f"##### {label}")
        render_metrics(result, units)

    figure, axis = plt.subplots(figsize=(11, 4.5))
    axis.axhline(0, color="#0f1b2d", linewidth=0.8, alpha=0.5)
    for series, result, label, color in [
        (scaled_first_series, first_result, first_label, REGION_COLORS["first"]),
        (scaled_second_series, second_result, second_label, REGION_COLORS["second"]),
    ]:
        axis.plot(compute_monthly_anomalies(series), color=color, alpha=0.35)
        axis.plot(result["trend_line"], color=color, linewidth=3.5, label=label)
    axis.set_ylabel(f"Anomaly ({units})")
    axis.set_title("Seasonally adjusted anomalies and trends")
    axis.legend(frameon=False)
    figure.tight_layout()
    st.pyplot(figure)

    comparison_text = build_comparison_verdict(
        first_label, second_label, first_result, second_result, units
    )
    show_verdict(comparison_text, first_result["is_significant"] or second_result["is_significant"])
    with st.expander("Statistical details"):
        st.write(first_label)
        st.json({key: value for key, value in first_result.items() if key != "trend_line"})
        st.write(second_label)
        st.json({key: value for key, value in second_result.items() if key != "trend_line"})


# ---------- Pages ----------

def page_single_region() -> None:
    st.header("Single region")
    uploaded_file = st.file_uploader("Upload a Giovanni time-series CSV", type="csv", key="single_upload")
    if uploaded_file is None:
        st.info("Export a monthly area-averaged time series from Giovanni and upload it here.")
        return
    monthly_series, metadata = load_giovanni_csv(uploaded_file)
    render_single_region(monthly_series, get_variable_info(metadata))


def page_compare_two_regions() -> None:
    st.header("Compare two regions")
    first_file = st.file_uploader("Region A (Giovanni CSV)", type="csv", key="compare_upload_a")
    second_file = st.file_uploader("Region B (Giovanni CSV, same variable)", type="csv", key="compare_upload_b")
    first_label = st.text_input("Label for region A", "Region A")
    second_label = st.text_input("Label for region B", "Region B")

    if first_file is None or second_file is None:
        st.info("Upload one CSV per region, both for the same variable and period.")
        return

    first_series, first_metadata = load_giovanni_csv(first_file)
    second_series, second_metadata = load_giovanni_csv(second_file)
    if first_metadata["variable_id"] != second_metadata["variable_id"]:
        st.error("The two files contain different variables. Upload the same variable for both regions.")
        return
    render_comparison(first_series, second_series, first_label, second_label, get_variable_info(first_metadata))


def page_demo() -> None:
    st.header("Demo: Italy vs Philippines, 2005–2025")
    topic_question = st.selectbox("What do you want to investigate?", list(TOPIC_QUESTIONS))
    selected_topic = TOPIC_QUESTIONS[topic_question]
    matching_labels = [
        file_label for file_label, catalog_key in DEMO_FILE_KEYS.items()
        if VARIABLE_CATALOG[catalog_key]["topic"] == selected_topic
    ]
    selected_label = matching_labels[0]
    variable_info = VARIABLE_CATALOG[DEMO_FILE_KEYS[selected_label]]

    region_names = sorted({path.stem.split("__")[0] for path in DEMO_DIRECTORY.glob("*__*.csv")})
    if len(region_names) < 2:
        st.error("Put the demo CSVs in demo_data/ named like italy__temp.csv.")
        return
    first_region = st.selectbox("Region A", region_names, index=0)
    second_region = st.selectbox("Region B", region_names, index=1)

    first_path = DEMO_DIRECTORY / f"{first_region}__{selected_label}.csv"
    second_path = DEMO_DIRECTORY / f"{second_region}__{selected_label}.csv"
    if not first_path.exists() or not second_path.exists():
        st.error("Demo file missing for this variable/region combination.")
        return

    with open(first_path, "rb") as first_file, open(second_path, "rb") as second_file:
        first_series, _ = load_giovanni_csv(first_file)
        second_series, _ = load_giovanni_csv(second_file)
    render_comparison(first_series, second_series, first_region.title(), second_region.title(), variable_info)


# ---------- Main ----------

st.set_page_config(page_title="Earth Sherlock - the Trend Detective", page_icon="🌍", layout="wide")
apply_custom_style()
render_hero()

demo_tab, single_tab, compare_tab = st.tabs(["Demo", "Single region", "Compare two regions"])
with demo_tab:
    page_demo()
with single_tab:
    page_single_region()
with compare_tab:
    page_compare_two_regions()