import streamlit as st
import pandas as pd
import time
import os

# ================= PAGE CONFIG =================
st.set_page_config(page_title="HR Dashboard", layout="wide")

# ================= GLOBAL STYLES =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

body {
    background-color: #0e1325;
}

/* SECTION TITLES */
.section-title {
    font-size: 24px;
    font-weight: 700;
    margin: 25px 0 18px 0;
}

/* FILTER CONTAINER */
.filter-box {
    background: #131a36;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 20px;
}

/* KPI CARDS */
.card {
    padding: 18px;
    border-radius: 16px;
    color: white;
    height: 115px;
    margin-bottom: 22px;
    box-shadow: 0 10px 26px rgba(0,0,0,0.45);
    transition: transform 0.25s ease;
}

.card:hover {
    transform: translateY(-4px);
}

.card-title {
    font-size: 13px;
    opacity: 0.85;
}

.card-value {
    font-size: 28px;
    font-weight: 700;
    margin-top: 10px;
}

/* SOFT COLOR FAMILY */
.blue   { background: linear-gradient(135deg, #1f2b45, #243b5e); }
.green  { background: linear-gradient(135deg, #1f4d4a, #256d68); }
.purple { background: linear-gradient(135deg, #3a245d, #4b2e7a); }
.gray   { background: linear-gradient(135deg, #2a2f36, #3a3f46); }
.red    { background: linear-gradient(135deg, #4a1f25, #6a2a33); }

/* TABLE */
.table-container {
    background: #131a36;
    border-radius: 16px;
    padding: 14px;
}
</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.markdown("""
<h1 style='text-align:center;'>📊 HR Recruitment Dashboard</h1>
<p style='text-align:center;color:#9aa4bf;'>Real-time recruitment intelligence</p>
""", unsafe_allow_html=True)

# ================= LIVE REFRESH =================
AUTO_REFRESH = st.toggle("🔄 Live Refresh (every 30 sec)", value=False)
if AUTO_REFRESH:
    time.sleep(30)
    st.rerun()

# ================= DATA LOAD =================
def load_from_csv():
    df = pd.read_csv("hr_Report.csv", skiprows=1, encoding="utf-8-sig", on_bad_lines="skip")
    df.columns = df.columns.str.strip()
    return df

@st.cache_data
def load_data():
    return load_from_csv()

df = load_data()

for col in ["Age", "Expected Salary"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ================= FILTERS =================
st.markdown("### 🔍 Filters")

with st.container():
    st.markdown("<div class='filter-box'>", unsafe_allow_html=True)

    f1, f2, f3, f4, f5 = st.columns([1,1,1,1,1.2])

    with f1:
        gender = st.multiselect("Gender", sorted(df["Gender"].dropna().unique()))

    with f2:
        industry = st.multiselect("Industry", sorted(df["Industry"].dropna().unique()))

    with f3:
        location = st.multiselect("Location", sorted(df["Location"].dropna().unique()))

    with f4:
        experience = st.multiselect(
            "Experience",
            sorted(df["Experience"].dropna().astype(str).unique())
        )

    with f5:
        st.markdown("**Age Range**")
        age_range = st.slider(
    "Age Range",
    int(df["Age"].min()),
    int(df["Age"].max()),
    (int(df["Age"].min()), int(df["Age"].max())),
    label_visibility="collapsed"
)

    apply = st.button("✅ Apply Filters", width="stretch")

    st.markdown("</div>", unsafe_allow_html=True)

# ================= APPLY FILTERS =================
filtered_df = df.copy()

if apply:
    if gender:
        filtered_df = filtered_df[filtered_df["Gender"].isin(gender)]
    if industry:
        filtered_df = filtered_df[filtered_df["Industry"].isin(industry)]
    if location:
        filtered_df = filtered_df[filtered_df["Location"].isin(location)]
    if experience:
        filtered_df["Experience"] = filtered_df["Experience"].astype(str)
        filtered_df = filtered_df[filtered_df["Experience"].isin(experience)]
    filtered_df = filtered_df[
        (filtered_df["Age"] >= age_range[0]) &
        (filtered_df["Age"] <= age_range[1])
    ]

# ================= INSIGHTS =================
freshers = filtered_df[filtered_df["Experience"].astype(str).str.contains("Nil|0", case=False, na=False)]
experienced = filtered_df.drop(freshers.index)

top_age = pd.cut(
    filtered_df["Age"],
    [0,22,27,35,100],
    labels=["18–22","23–27","28–35","35+"]
).value_counts().idxmax()

avg_salary = int(filtered_df["Expected Salary"].mean()) if not filtered_df.empty else 0
high_salary = filtered_df[filtered_df["Expected Salary"] > 15000]

# ================= KPI CARDS =================
st.markdown("<div class='section-title'>📌 Recruitment Overview</div>", unsafe_allow_html=True)

r1 = st.columns(4)
r1[0].markdown(f"<div class='card blue'><div class='card-title'>Total Applications</div><div class='card-value'>{len(filtered_df)}</div></div>", unsafe_allow_html=True)
r1[1].markdown(f"<div class='card green'><div class='card-title'>Freshers Pool</div><div class='card-value'>{len(freshers)}</div></div>", unsafe_allow_html=True)
r1[2].markdown(f"<div class='card purple'><div class='card-title'>Experienced Talent</div><div class='card-value'>{len(experienced)}</div></div>", unsafe_allow_html=True)
r1[3].markdown(f"<div class='card gray'><div class='card-title'>Prime Age Group</div><div class='card-value'>{top_age}</div></div>", unsafe_allow_html=True)

r2 = st.columns(2)
r2[0].markdown(f"<div class='card blue'><div class='card-title'>Avg Expected Salary</div><div class='card-value'>₹{avg_salary:,}</div></div>", unsafe_allow_html=True)
r2[1].markdown(f"<div class='card red'><div class='card-title'>High Salary Demand</div><div class='card-value'>{len(high_salary)}</div></div>", unsafe_allow_html=True)

# ================= TABLE =================
st.markdown("<div class='section-title'>📋 Candidate Details</div>", unsafe_allow_html=True)
st.markdown("<div class='table-container'>", unsafe_allow_html=True)
st.dataframe(filtered_df, width="stretch"
, hide_index=True)
st.markdown("</div>", unsafe_allow_html=True)
