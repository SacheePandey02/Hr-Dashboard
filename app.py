# ================================
# HR ANALYTICS DASHBOARD - INTERACTIVE VERSION
# ================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import seaborn as sns

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="HR Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 HR Recruitment Analytics Dashboard")
st.markdown("Interactive dashboard to analyze HR recruitment data with filters and visualizations.")

# -------------------------------
# LOAD & CLEAN DATA
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "hr_Report.csv",
        skiprows=1,
        engine="python",
        sep=",",
        quotechar='"',
        on_bad_lines="skip"
    )

    # Clean columns
    df.columns = df.columns.str.strip()
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df["Expected Salary"] = pd.to_numeric(df["Expected Salary"], errors="coerce")
    
    for col in ["Gender", "Industry", "Location", "Experience"]:
        df[col] = df[col].astype(str).str.strip()

    df = df.dropna(subset=["Gender", "Industry", "Location", "Age"])
    return df

df = load_data()

# -------------------------------
# SIDEBAR FILTERS
# -------------------------------
st.sidebar.header("🔍 Filters")

gender = st.sidebar.multiselect("Gender", sorted(df["Gender"].unique()))
industry = st.sidebar.multiselect("Industry", sorted(df["Industry"].unique()))
location = st.sidebar.multiselect("Location", sorted(df["Location"].unique()))
age_range = st.sidebar.slider("Age Range", int(df["Age"].min()), int(df["Age"].max()), (18, 60))
salary_range = st.sidebar.slider(
    "Expected Salary Range",
    int(df["Expected Salary"].min()),
    int(df["Expected Salary"].max()),
    (0, int(df["Expected Salary"].max()))
)

# APPLY FILTERS
filtered_df = df.copy()
if gender:
    filtered_df = filtered_df[filtered_df["Gender"].isin(gender)]
if industry:
    filtered_df = filtered_df[filtered_df["Industry"].isin(industry)]
if location:
    filtered_df = filtered_df[filtered_df["Location"].isin(location)]

filtered_df = filtered_df[
    (filtered_df["Age"].between(age_range[0], age_range[1])) &
    (filtered_df["Expected Salary"].between(salary_range[0], salary_range[1]))
]

# -------------------------------
# KPI METRICS
# -------------------------------
st.subheader("📈 Key Metrics")
c1, c2, c3, c4 = st.columns(4)

c1.metric("👥 Total Candidates", len(filtered_df))
c2.metric("🎂 Average Age", round(filtered_df["Age"].mean(), 1) if not filtered_df.empty else 0)
c3.metric(
    "💰 Avg Expected Salary",
    f"₹{int(filtered_df['Expected Salary'].mean()):,}" if not filtered_df.empty else "₹0"
)
c4.metric("🌍 Unique Locations", filtered_df["Location"].nunique())

st.markdown("---")

# -------------------------------
# VISUALIZATIONS
# -------------------------------
st.subheader("📊 Candidate Visualizations")
col1, col2, col3 = st.columns([1,1,1])

# Gender Pie Chart
with col1:
    st.markdown("**Gender Distribution**")
    if not filtered_df.empty:
        gender_counts = filtered_df["Gender"].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(
            gender_counts,
            labels=gender_counts.index,
            autopct="%1.1f%%",
            startangle=140,
            colors=sns.color_palette("pastel")
        )
        ax1.axis("equal")
        st.pyplot(fig1)
    else:
        st.info("No data to display.")

# Industry Bar Chart
with col2:
    st.markdown("**Industry-wise Candidates**")
    if not filtered_df.empty:
        fig2, ax2 = plt.subplots()
        filtered_df["Industry"].value_counts().plot(kind="barh", ax=ax2, color=sns.color_palette("Set2"))
        ax2.set_xlabel("Number of Candidates")
        st.pyplot(fig2)
    else:
        st.info("No data to display.")

# Location Pie Chart
with col3:
    st.markdown("**Location Distribution**")
    if not filtered_df.empty:
        loc_counts = filtered_df["Location"].value_counts()
        fig3, ax3 = plt.subplots()
        ax3.pie(
            loc_counts,
            labels=loc_counts.index,
            autopct="%1.1f%%",
            startangle=140,
            colors=sns.color_palette("tab20")
        )
        ax3.axis("equal")
        st.pyplot(fig3)
    else:
        st.info("No data to display.")

# Age & Salary Histograms
col4, col5 = st.columns(2)

with col4:
    st.subheader("Age Distribution")
    if not filtered_df["Age"].dropna().empty:
        fig4, ax4 = plt.subplots()
        filtered_df["Age"].plot(kind="hist", bins=10, color="#FFA07A", edgecolor="black", ax=ax4)
        ax4.set_xlabel("Age")
        st.pyplot(fig4)

with col5:
    st.subheader("Expected Salary Distribution")
    if not filtered_df["Expected Salary"].dropna().empty:
        fig5, ax5 = plt.subplots()
        filtered_df["Expected Salary"].plot(kind="hist", bins=10, color="#20B2AA", edgecolor="black", ax=ax5)
        ax5.set_xlabel("Expected Salary")
        st.pyplot(fig5)

st.markdown("---")

# -------------------------------
# DATA TABLE & EXPORT
# -------------------------------
st.subheader("📄 Candidate Details")

if filtered_df.empty:
    st.warning("No candidates match the selected filters.")
else:
    st.dataframe(
        filtered_df[
            ["Date", "Name", "Gender", "Age", "Mobile", "Industry", "Location", "Experience", "Expected Salary"]
        ],
        use_container_width=True
    )

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Candidates")
    return output.getvalue()

st.download_button(
    "📥 Download Filtered Data as Excel",
    convert_df_to_excel(filtered_df),
    "filtered_candidates.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
