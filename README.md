# Trend Detective

**Is an Earth science variable changing, where, by how much, and is the change significant?**

Earth Sherlock is a Python / Streamlit tool that turns a NASA Giovanni time series into a plain-language answer. It guides the user to a variable, removes the seasonal cycle, estimates the rate of change per decade, and tests whether the trend is statistically significant. It can also compare two regions side by side, because the same variable can change in one place and not in another.

## What it answers

| Question | How the tool answers it |
|---|---|
| **What** is changing? | A catalog of variables with plain-language definitions, chosen through simple questions ("Is it getting warmer?") |
| **Where** is it changing? | Per-region time series, plus a two-region comparison |
| **How much?** | Theil-Sen slope per decade with a 95% confidence interval (OLS slope reported alongside) |
| **Is it significant?** | Three different tests; the trend counts as significant only if **all three** agree |

## Pages

The app opens on an interface with three tabs:

- **Demo:** pre-loaded comparison of **Italy, the Philippines or Finland** (2005-2025) for six possible variables. Pick a question, then any two of the three regions. Works with no upload.
- **Single region:** upload one Giovanni time-series CSV and get metrics, plot and significance of the trend.
- **Compare two regions:** upload two CSVs of the same variable and compare trends, significance and direction.

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

## Method

1. **Parse** the Giovanni CSV (metadata header, fill values, monthly grid).
2. **Remove the seasonal cycle:** subtract each calendar month's mean over the whole period, giving monthly anomalies.
3. **Estimate the trend** on the anomalies:
   - Theil-Sen slope with a 95% confidence interval (robust to outliers), per decade
   - Ordinary least squares slope, for comparison
4. **Test significance** with three different tests of the same null hypothesis (no trend):
   - Mann-Kendall (classic)
   - Mann-Kendall with the Hamed-Rao autocorrelation correction
   - Linear regression with autocorrelation-robust (Newey-West / HAC, 12 monthly lags) standard errors
5. **Verdict:** the trend is called significant only if the **largest** of the three p-values is below 0.05. The lag-1 autocorrelation is reported for transparency.

Using the most conservative p-value is deliberate. Monthly climate data are autocorrelated, which can make a single test look more convincing than it should, and the Hamed-Rao correction can move the p-value in either direction. The three tests run on the same data, so they are three robustness checks with different assumptions, not independent evidence.

The analysis assumes a **linear** trend. Non-linear trends, step changes and multi-decadal oscillations are not modelled.

## Demo results (2005-2025)

Trends are Theil-Sen slopes per decade. **sig.** = all three tests give p < 0.05; **n.s.** = not significant.

| Variable | Italy | Philippines | Finland |
|---|---|---|---|
| Near-surface humidity (g/kg) | +0.26 · sig. | +0.26 · sig. | +0.16 · sig. |
| Soil moisture (kg/m²) | -2.8 · sig. | -1.2 · n.s. | -1.1 · n.s. |
| Surface air temperature (°C) | +0.34 · sig. | -0.05 · n.s. | +0.10 · n.s. |
| Near-surface wind speed (m/s) | -0.01 · n.s. | -0.13 · sig. | +0.02 · n.s. |
| Total column ozone (DU) | +0.1 · n.s. | +4.0 · sig.* | +4.7 · n.s. |
| Rainfall rate (mm/day) | -0.09 · n.s. | -0.25 · n.s. | +0.002 · n.s. |


### Reading the table

- **Humidity** rises significantly in all three regions. Relative to each region's period mean (slope ÷ mean, our own calculation) that is about +3.4% per decade in Italy and Finland and about +1.5% in the Philippines.
- **Temperature** changes significantly only in Italy (+0.34 °C/decade). Finland (+0.10, confidence interval -0.35 to +0.54) and the Philippines (-0.05) show no detectable trend: a small trend in a highly variable 20-year series is hard to detect, and a longer record might change this.
- **Soil moisture** declines in all three regions, but significantly only in Italy: same direction, different strength.
- **Wind speed** declines significantly only in the Philippines (-0.13 m/s/decade). 
- **Ozone:** the Philippines shows a significant +4.0 DU/decade. Finland has a larger slope (+4.7) that is not significant (worst-case p = 0.13), and Italy shows none. 
- **Rainfall** shows no significant trend anywhere. The signs differ between regions, but all changes are within the noise.
- **No opposite-direction pair:** no variable shows significant trends of opposite sign in two regions. The clearest contrasts are "significant in one region, not in the others" (temperature, soil moisture, wind, ozone).

## Project structure

```
trend_detective/
├── app.py               # Streamlit app (Demo, Single region, Compare two regions)
├── analysis.py          # anomalies, trend estimation, significance tests, comparison
├── loaders.py           # Giovanni CSV parser (metadata, fill values, monthly grid)
├── catalog.py           # variable catalog, units, definitions, topic questions
├── verdict.py           # plain-language summaries
├── styling.py           # colour palette, custom CSS, plot theme
├── scan_demo_data.py    # batch-analyzes all demo CSVs and prints a summary table
├── .streamlit/
│   └── config.toml      # dark-blue Streamlit theme
├── demo_data/           # demo CSVs, named {region}__{variable}.csv
└── README.md
```

Demo file names follow `{region}__{variable}.csv`, with variable labels `temp`, `humidity`, `ozone`, `rain`, `soil`, `wind` (for example `italy__humidity.csv`, `finland__soil.csv`, `philippines__wind.csv`).

## Installation and usage

Requires Python 3.9+.

```bash
pip install streamlit pandas numpy scipy matplotlib pymannkendall statsmodels
streamlit run app.py
```
or with python 3.15
```bash
pip install -r requirements.txt
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
5. Upload it on the *Single region* tab, or two files of the same variable on *Compare two regions*.

Variables outside the catalog still work, but they are shown with the CSV's own title and **without unit conversion** (the verdict will say "units").

## Limitations

- **Linear trends only**, on monthly data. Daily data are not supported.
- **About 20 years** of data: enough for a first look, but significance is harder to reach than with 40+ years, and short records can be dominated by natural variability (for example ENSO).
- **Many variables and regions tested at once** (18 combinations here) means some "significant" results can occur by chance.
- **Trend is not cause.** The tool shows that and how much something changes, not why.

## Possible extensions

- Live download of data from Giovanni, including area averages through its cloud services
- More variables
- More regions
- Non-linear trend handling and explicit ENSO/QBO adjustment

## Resources and acknowledgments

- [NASA Giovanni](https://giovanni.gsfc.nasa.gov/) (GES DISC): data access and time-series generation. Please follow Giovanni's acknowledgment guidelines when publishing results.
- [KNMI Climate Explorer](https://climexp.knmi.nl/): reference for cross-checking trends
- Python libraries: pandas, NumPy, SciPy, statsmodels, pymannkendall, Matplotlib, Streamlit
- Statistical background: Mann-Kendall trend test; Hamed & Rao (1998) modified Mann-Kendall test for autocorrelated data; Theil-Sen slope estimator

## Use of AI tools

Claude (Anthropic) was used as an assistant for faster coding.
