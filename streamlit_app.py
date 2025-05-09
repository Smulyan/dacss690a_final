import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
@st.cache_data
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

# Filter by selected date range
if len(date_range) == 2:
    df = df[(df["date"] >= pd.to_datetime(date_range[0])) & (df["date"] <= pd.to_datetime(date_range[1]))]

# ---------- Subject Trends ----------
st.subheader("Subject Area Trends")

subject_base = [
    "computer science", "biology", "physics", "chemistry", "mathematics",
    "engineering", "medicine", "social sciences", "humanities"
]
subject_cols = [col + ("_pct" if value_type == "Percentages" else "") for col in subject_base]
df_subject = df[["date"] + subject_cols].melt(id_vars="date", var_name="Subject", value_name="Value")
df_subject["Subject"] = df_subject["Subject"].str.replace("_pct", "", regex=False).str.title()

fig1 = px.line(df_subject, x="date", y="Value", color="Subject", markers=True)
fig1.update_layout(yaxis_title="%" if value_type == "Percentages" else "Count")
st.plotly_chart(fig1, use_container_width=True)

# ---------- Language Distribution ----------
st.subheader("Language Distribution (Most Recent Day)")

latest_date = df["date"].max()
df_latest = df[df["date"] == latest_date]

# Language codes are <=5 characters and not subject names
base_langs = [col for col in df.columns if (
    len(col) <= 5 and not col.endswith("_pct") and col not in ["date"] + subject_base)]

lang_cols = [col + ("_pct" if value_type == "Percentages" else "") for col in base_langs]

df_lang = df_latest.melt(id_vars="date", value_vars=lang_cols, var_name="Language", value_name="Value")
df_lang["Language"] = df_lang["Language"].str.replace("_pct", "", regex=False).str.upper()
df_lang = df_lang[df_lang["Value"] > 0].sort_values("Value", ascending=False)

fig2 = px.bar(df_lang, x="Language", y="Value", title=f"Languages on {latest_date.date()}")
fig2.update_layout(yaxis_title="%" if value_type == "Percentages" else "Count")
st.plotly_chart(fig2, use_container_width=True)
