# Trend Detective

**Is an Earth science variable changing, where, by how much, and is the change significant?**

Trend Detective is a Python / Streamlit tool that turns a NASA Giovanni time series into a plain-language answer. It guides the user to a variable, removes the seasonal cycle, estimates the rate of change per decade, and tests whether the trend is statistically significant. It can also compare two regions side by side, which is where the same process can produce different trends in different places.

## What it answers

| Question | How the tool answers it |
|---|---|
| **What** is changing? | A catalog of variables with plain-language definitions, chosen through simple questions ("Is rainfall changing?") |
| **Where** is it changing? | Per-region time series, plus a two-region comparison page |
| **How much?** | Theil-Sen slope per decade with a 95% confidence interval (OLS slope reported alongside) |
| **Is it significant?** | Three independent tests; the trend counts as significant only if **all** of them agree |

## Pages

- **Demo**: pre-loaded Italy vs Philippines comparison (2005-2025) for several variables. Works with no upload.
- **Single region**: upload one Giovanni time-series CSV and get plot, trend and verdict.
- **Compare two regions**: upload two CSVs of the same variable and compare trends, significance and direction.

## Data

All data come from [NASA Giovanni](https://giovanni.gsfc.nasa.gov/) (GES DISC), using **Area-Averaged Time Series, monthly**, exported as CSV.

| Variable | Giovanni ID | Source | Display unit |
|---|---|---|---|
| Daytime surface air temperature | `AIRS3STM_006_SurfAirTemp_A` | AIRS (satellite) | °C |
| Near-surface humidity (10 m specific humidity) | `M2TMNXOCN_5_12_4_QV10M` | MERRA-2 (reanalysis) | g/kg |
| Total column ozone | `M2TMNXSLV_5_12_4_TO3` | MERRA-2 (reanalysis) | DU |
| Rainfall rate | `GLDAS_NOAH025_M_2_1_Rainf_tavg` | GLDAS (land model) | mm/day |
| Soil moisture, 10-40 cm | `GLDAS_NOAH025_M_2_1_SoilMoi10_40cm_inst` | GLDAS (land model) | kg/m² |
| Near-surface wind speed | `FLDAS_NOAH01_C_GL_M_001_Wind_f_tavg` | FLDAS (land model) | m/s |

Native units are converted for display (humidity ×1000, rain ×86400, temperature K → °C). Slopes in K and °C are identical.

Note the mix of sources: AIRS is a satellite observation, while MERRA-2, GLDAS and FLDAS are model or reanalysis products that assimilate observations. The app shows the source in the definition of each variable.

## Method

1. **Parse** the Giovanni CSV (metadata header, fill values, monthly grid).
2. **Remove the seasonal cycle:** subtract each calendar month's mean over the whole period, giving monthly anomalies.
3. **Estimate the trend** on the anomalies:
   - Theil-Sen slope with 95% confidence interval (robust to outliers), reported per decade
   - Ordinary least squares slope, for comparison
4. **Test significance** with three tests:
   - Mann-Kendall (classic)
   - Mann-Kendall with the Hamed-Rao autocorrelation correction
   - OLS with autocorrelation-robust (HAC, 12 lags) standard errors
5. **Verdict:** the trend is called significant only if the **largest** of the three p-values is below 0.05. The lag-1 autocorrelation is reported for transparency.

Using the most conservative p-value is deliberate. Monthly climate data are autocorrelated, which can make a single test look more convincing than it should, and the Hamed-Rao correction can move the p-value in either direction.

The analysis assumes a **linear** trend. Non-linear trends, step changes and multi-decadal oscillations are not modelled.

## Demo results (Italy vs Philippines, 2005-2025)

Trends are Theil-Sen slopes per decade; "significant" means all three tests give p < 0.05.

| Variable | Italy | Philippines |
|---|---|---|
| Near-surface humidity | +0.26 g/kg, significant | +0.26 g/kg, significant |
| Soil moisture (10-40 cm) | -2.8 kg/m², significant | -1.2 kg/m², not significant |
| Rainfall rate | ≈ -0.09 mm/day, not significant | ≈ -0.26 mm/day, not significant |
| Total column ozone | ≈ 0 DU, not significant | +4.0 DU, significant (see note) |
| Surface air temperature | +0.34 °C, significant | -0.05 °C, not significant |
| Near-surface wind speed | -0.01 m/s, not significant | -0.13 m/s, significant |

Reading the table:

- **Humidity** rises at nearly the same rate in both places: one process, same direction.
- **Soil moisture** declines significantly in Italy but not (statistically) in the Philippines: the same variable behaves differently by region.
- **Rainfall** shows a negative but non-significant tendency in both: a trend can exist without being significant, and a longer record might change that.
- **Ozone note:** the large Philippines trend comes from a reanalysis product and has not been independently validated (e.g. against a second source or by inspecting the series for step changes). Treat it as a result to verify, not a finding.
- **Temperature** warms significantly in Italy (+0.34 °C/decade) but shows no detectable trend in the Philippines (-0.05 °C/decade, confidence interval includes zero). Same variable, different behaviour by region. A small trend in a noisy series can need a longer record before it becomes significant.
- **Wind speed** declines significantly in the Philippines (-0.13 m/s/decade) and is flat in Italy. The wind data come from a land model (FLDAS), so this is what the dataset shows, not a confirmed change in the atmosphere.
- **No opposite-direction pair:** no variable shows significant trends of opposite sign in the two regions. The clearest contrasts are "significant in one region, not in the other" (soil moisture, temperature, wind, ozone).
- **Borderline results:** Italy temperature (p ≈ 0.015) and Philippines wind (p ≈ 0.018) are close to the 5% threshold. With 12 region-variable tests, a chance result cannot be ruled out, so these two should be read with more caution than the strongest ones (humidity, ozone).

## Project structure

```
trend_detective/
├── app.py               # Streamlit app (Demo, Single region, Compare two regions)
├── analysis.py          # anomalies, trend estimation, significance tests, comparison
├── loaders.py           # Giovanni CSV parser (metadata, fill values, monthly grid)
├── catalog.py           # variable catalog, units, definitions, topic questions
├── verdict.py           # plain-language summaries
├── scan_demo_data.py    # batch-analyzes all demo CSVs and prints a summary table
├── demo_data/           # demo CSVs, named {region}__{variable}.csv
└── README.md
```

Demo file names follow `{region}__{variable}.csv`, with variable labels `temp`, `humidity`, `ozone`, `rain`, `soil`, `wind` (e.g. `italy__humidity.csv`, `philippines__soil.csv`).

## Installation and usage

Requires Python 3.9+.

```bash
pip install streamlit pandas numpy scipy matplotlib pymannkendall statsmodels
streamlit run app.py
```

To summarize all demo files in the terminal:

```bash
python scan_demo_data.py
```

### Using your own data

1. Open [Giovanni](https://giovanni.gsfc.nasa.gov/giovanni/) (free Earthdata login required).
2. Choose the plot type **Time Series, Area-Averaged**.
3. Pick a **monthly** variable, a region (bounding box or shapefile) and a date range.
4. Plot, then download the **CSV**.
5. Upload it on the *Single region* page, or two files of the same variable on *Compare two regions*.

Variables outside the catalog still work, but they are shown with the CSV's own title and **without unit conversion** (the verdict will say "units").

## Limitations

- **Linear trends only**, on monthly data. Daily data are not supported.
- **About 20 years** of data: enough for a first look, but significance is harder to reach than with 40+ years. Short records can also be dominated by natural variability (e.g. ENSO).
- **Model and reanalysis variables** can contain artifacts from changes in the assimilated observations. Significant does not mean physically confirmed.
- **Several variables tested at once** means some "significant" results can occur by chance.
- **Trend is not cause.** The tool shows that and how much something changes, not why.
- **Area averages** depend on the region the user picked in Giovanni; a different boundary can change the trend.

## Possible extensions

- Live download of data from Giovanni, including area averages through its cloud services
- Trend **maps** (per-pixel slope with significance stippling) to show where a variable increases and decreases within a region
- More variables, including vegetation (e.g. MODIS via AppEEARS) and air quality
- Additional regions, to find variables whose trends truly flip sign
- Non-linear trend handling and explicit ENSO/QBO adjustment

## Resources and acknowledgments

- [NASA Giovanni](https://giovanni.gsfc.nasa.gov/) (GES DISC): data access and time-series generation. Please follow Giovanni's acknowledgment guidelines when publishing results.
- [KNMI Climate Explorer](https://climexp.knmi.nl/): reference for cross-checking trends
- Python libraries: pandas, NumPy, SciPy, statsmodels, pymannkendall, Matplotlib, Streamlit
- Statistical background: Mann-Kendall trend test; Hamed & Rao (1998) modified Mann-Kendall test for autocorrelated data; Theil-Sen slope estimator

## Super intelligence usage
Claude was used in ask mode to accelerate coding.