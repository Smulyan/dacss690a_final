import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv("https://raw.githubusercontent.com/Smulyan/dacss690a_final/main/daily_summary.csv", parse_dates=["date"])
    return df

df = load_data()

st.title("Subject and Language Trends in Crossref Abstracts")
st.header("Daily classification using spaCy NLP")

# Sidebar filters
st.sidebar.header("Filter options")

# Date range
date_range = st.sidebar.date_input(
    "Select date range",
    [df["date"].min(), df["date"].max()],
)

# Value type: counts or percentages
value_type = st.sidebar.radio(
    "Show values as",
    ("Raw counts", "Percentages")
)

# Filtered dataframe for trends
if len(date_range) == 2:
    df_filtered = df[(df["date"] >= pd.to_datetime(date_range[0])) & (df["date"] <= pd.to_datetime(date_range[1]))]
else:
    df_filtered = df.copy()

# Identify subject and language columns
subject_base = [
    "computer science", "biology", "physics", "chemistry", "mathematics",
    "engineering", "medicine", "social sciences", "humanities"
]
subject_cols = [col + ("_pct" if value_type == "Percentages" else "") for col in subject_base]

base_langs = [col for col in df.columns if (
    len(col) <= 5 and not col.endswith("_pct") and col not in ["date"] + subject_base)]
lang_cols = [col + ("_pct" if value_type == "Percentages" else "") for col in base_langs]

# Tabs
tab1, tab2 = st.tabs(["Subject Areas", "Languages"])

# --- Subject Areas Tab ---
with tab1:
    st.subheader("📈 Subject Area Trends Over Selected Date Range")

    df_subject = df_filtered[["date"] + subject_cols].melt(id_vars="date", var_name="Subject", value_name="Value")
    df_subject["Subject"] = df_subject["Subject"].str.replace("_pct", "", regex=False).str.title()

    fig1 = px.line(df_subject, x="date", y="Value", color="Subject", markers=True)
    fig1.update_layout(yaxis_title="%" if value_type == "Percentages" else "Count")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📊 Subject Area Distribution (Total)")

    # Force raw count columns, regardless of value_type
    subject_totals = df[[col for col in subject_base]]  # no _pct
    df_total_subject = subject_totals.sum().reset_index()
    df_total_subject.columns = ["Subject", "Value"]
    df_total_subject["Subject"] = df_total_subject["Subject"].str.title()

    # Always use "Total Count" as label
    fig3 = px.bar(df_total_subject, x="Subject", y="Value")
    fig3.update_layout(yaxis_title="Total Count")

# --- Languages Tab ---
with tab2:
    st.subheader("📈 Language Trends Over Selected Date Range")

    df_lang_trend = df_filtered[["date"] + lang_cols].melt(id_vars="date", var_name="Language", value_name="Value")
    df_lang_trend["Language"] = df_lang_trend["Language"].str.replace("_pct", "", regex=False).str.upper()

    fig2 = px.line(df_lang_trend, x="date", y="Value", color="Language", markers=True)
    fig2.update_layout(yaxis_title="%" if value_type == "Percentages" else "Count")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📊 Language Distribution (Total)")

    # Force raw count columns, regardless of value_type
    lang_totals = df[[col for col in base_langs]]
    df_total_lang = lang_totals.sum().reset_index()
    df_total_lang.columns = ["Language", "Value"]
    df_total_lang["Language"] = df_total_lang["Language"].str.upper()
    df_total_lang = df_total_lang[df_total_lang["Value"] > 0].sort_values("Value", ascending=False)

    # Always use "Total Count" as label
    fig4 = px.bar(df_total_lang, x="Language", y="Value")
    fig4.update_layout(yaxis_title="Total Count")
    st.plotly_chart(fig4, use_container_width=True)