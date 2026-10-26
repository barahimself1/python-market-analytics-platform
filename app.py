from pathlib import Path
import plotly.express as px
import streamlit as st
from src.data_loader import load_market_data
from src.analysis import calibration_table, summary_metrics, feature_return_summary

st.set_page_config(page_title="Python Market Analytics Research Platform", page_icon="📈", layout="wide")
DATA_PATH = Path(__file__).parent / "data" / "sample_markets.csv"

@st.cache_data
def get_data():
    return load_market_data(DATA_PATH)

df = get_data()

st.title("Python Market Analytics Research Platform")
st.caption("Prediction market calibration, return behavior, and chronological validation.")

st.info(
    "This public demo uses synthetic sample data. The full research workflow covers "
    "2,139 unique resolved tickers with a 1,497 market research sample and a 642 market later test sample."
)

selected_sample = st.sidebar.selectbox("Sample", ["All", "Research", "Test"])
view = df.copy() if selected_sample == "All" else df[df["sample"] == selected_sample].copy()

m = summary_metrics(view)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Unique markets", f"{m['markets']:,}")
c2.metric("Observations", f"{m['observations']:,}")
c3.metric("Mean return", f"{m['mean_return_pct']:.2f}%")
c4.metric("Positive return rate", f"{m['positive_return_rate']*100:.1f}%")

tab1, tab2, tab3 = st.tabs(["Calibration", "Returns", "Feature explorer"])

with tab1:
    cal = calibration_table(view)
    chart = cal.melt(
        id_vars=["probability_bucket"],
        value_vars=["mean_implied_probability", "realized_outcome_rate"],
        var_name="series",
        value_name="probability",
    )
    fig = px.line(
        chart, x="probability_bucket", y="probability",
        color="series", markers=True,
        title="Implied probability compared with realized outcome rate"
    )
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(cal, use_container_width=True, hide_index=True)

with tab2:
    fig = px.histogram(
        view, x="return_pct", nbins=30, color="sample",
        barmode="overlay", title="Return distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    feature = st.selectbox(
        "Feature",
        ["direction", "entry_price", "atr", "normalized_distance", "time_to_expiry_minutes"],
    )
    summary = feature_return_summary(view, feature)
    xcol = "feature_bucket" if "feature_bucket" in summary.columns else feature
    summary[xcol] = summary[xcol].astype(str)
    fig = px.bar(summary, x=xcol, y="mean_return_pct", title=f"Mean return by {feature}")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(summary, use_container_width=True, hide_index=True)

st.caption("Public portfolio version. Private credentials and execution logic are intentionally excluded.")
