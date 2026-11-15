import re

import matplotlib.pyplot as plt
import streamlit as st

# ---- Edit colours here ----
BRIGHT_YELLOW = "#eafe07"
DARK_BLUE = "#07173f"
BLUE = "#0960e1"
LIGHT_BLUE = "#2e96f5"
WHITE = "#ffffff"
BLACK = "#000000"
PANEL = "#0f2759"  # only colour not in the palette: slightly lighter dark blue for cards
# ---------------------------

REGION_COLORS = {"first": BRIGHT_YELLOW, "second": LIGHT_BLUE}

CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap');
h1, h2, h3, h4, h5 { font-family: 'Space Grotesk', sans-serif; }
#MainMenu, footer { visibility: hidden; }

[data-testid="stMetric"] {
    background: __PANEL__;
    border: 1px solid __BLUE__;
    border-radius: 16px;
    padding: 16px 20px;
    box-shadow: 0 4px 10px __BLACK__66;
}
[data-testid="stMetricLabel"] p { color: __LIGHT_BLUE__; font-size: 0.85rem; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] div { color: __WHITE__; }

.hero {
    background: linear-gradient(120deg, __PANEL__ 0%, __BLUE__ 100%);
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 24px;
}
.hero h1 { color: __WHITE__; margin: 0; font-size: 2.6rem; }
.hero h1 span { color: __BRIGHT_YELLOW__; }
.hero p { color: __WHITE__; opacity: 0.9; margin: 6px 0 0 0; font-size: 1.1rem; }

.verdict {
    background: __PANEL__;
    color: __WHITE__;
    border: 1px solid __BLUE__;
    border-left: 8px solid __LIGHT_BLUE__;
    border-radius: 16px;
    padding: 20px 24px;
    margin: 12px 0 20px 0;
    font-size: 1.05rem;
    line-height: 1.55;
}
.verdict.significant { border-left-color: __BRIGHT_YELLOW__; }
.verdict b { color: __BRIGHT_YELLOW__; }
</style>
"""


def build_css() -> str:
    palette = {
        "__BRIGHT_YELLOW__": BRIGHT_YELLOW, "__BLUE__": BLUE,
        "__LIGHT_BLUE__": LIGHT_BLUE, "__WHITE__": WHITE,
        "__BLACK__": BLACK, "__PANEL__": PANEL,
    }
    css = CSS_TEMPLATE
    for token, color in palette.items():
        css = css.replace(token, color)
    return css


def apply_custom_style() -> None:
    st.markdown(build_css(), unsafe_allow_html=True)
    plt.rcParams.update({
        "figure.facecolor": PANEL,
        "axes.facecolor": PANEL,
        "axes.edgecolor": WHITE,
        "axes.labelcolor": WHITE,
        "text.color": WHITE,
        "xtick.color": WHITE,
        "ytick.color": WHITE,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": WHITE,
        "grid.alpha": 0.12,
        "axes.titleweight": "bold",
        "axes.titlesize": 13,
        "font.size": 11,
    })


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>Trend <span>Detective</span></h1>
            <p>Is this Earth science variable changing, where, by how much, and is it significant?</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(trend_result: dict, units: str) -> None:
    metric_columns = st.columns(4)
    metric_columns[0].metric(
        "Trend per decade",
        f"{trend_result['theil_sen_slope_per_decade']:+.2f} {units}",
    )
    metric_columns[1].metric(
        "95% confidence interval",
        f"{trend_result['ci_low_per_decade']:+.2f} to {trend_result['ci_high_per_decade']:+.2f}",
    )
    metric_columns[2].metric("Worst-case p-value", f"{trend_result['worst_case_p_value']:.4f}")
    metric_columns[3].metric("Significant?", "Yes" if trend_result["is_significant"] else "No")


def markdown_to_html(text: str) -> str:
    """Minimal conversion for the verdict text (bold, italics, paragraphs)."""
    html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    html = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"<i>\1</i>", html)
    return html.replace("\n\n", "<br><br>")


def show_verdict(verdict_text: str, is_significant: bool) -> None:
    css_class = "verdict significant" if is_significant else "verdict"
    st.markdown(
        f'<div class="{css_class}">{markdown_to_html(verdict_text)}</div>',
        unsafe_allow_html=True,
    )