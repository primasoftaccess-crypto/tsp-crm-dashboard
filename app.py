import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page & Layout Configuration
st.set_page_config(
    page_title="Banking TSP Operations CRM",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Banking TSP Operations & Merchant Onboarding CRM")
st.caption("SME Management Platform | Active Projects: PAY NSDL, IATA, S2PAY")

# 2. Sidebar Setup & Operational Role Matrix
st.sidebar.header("⚙️ Operational Leadership")
st.sidebar.info("""
**Core Operations Setup:**
- **SME & Primary Ops Lead**: Member A
- **Secondary Ops Lead**: Member C
- **Universal QA Lead**: Member D (All Projects)

**Project Execution Handlers:**
- **PAY NSDL**: Member B & Member E
- **IATA**: Member F
- **S2PAY**: Member G
""")

# 3. Master Merchant Onboarding Data Editor
st.subheader("📋 Centralized Merchant Onboarding Tracker")
st.write("Edit cell values live inside your browser grid below:")

initial_data = pd.DataFrame([
    {
        "Merchant ID": "M-101", 
        "Merchant Name": "Apex FinTech", 
        "Project": "PAY NSDL", 
        "Stage": "Testing", 
        "Status": "On Track", 
        "Primary Lead": "Member A", 
        "Secondary Lead": "Member C", 
        "QA Lead": "Member D", 
        "Project Handler": "Member B", 
        "Open Tickets": 1
    },
    {
        "Merchant ID": "M-102", 
        "Merchant Name": "BlueSky Payments", 
        "Project": "PAY NSDL", 
        "Stage": "Infra Setup", 
        "Status": "Delayed", 
        "Primary Lead": "Member A", 
        "Secondary Lead": "Member C", 
        "QA Lead": "Member D", 
        "Project Handler": "Member E", 
        "Open Tickets": 3
    },
    {
        "Merchant ID": "M-201", 
        "Merchant Name": "Global Travels", 
        "Project": "IATA", 
        "Stage": "Live", 
        "Status": "Completed", 
        "Primary Lead": "Member A", 
        "Secondary Lead": "Member C", 
        "QA Lead": "Member D", 
        "Project Handler": "Member F", 
        "Open Tickets": 0
    },
    {
        "Merchant ID": "M-301", 
        "Merchant Name": "FastPay Solutions", 
        "Project": "S2PAY", 
        "Stage": "Testing", 
        "Status": "Blocked", 
        "Primary Lead": "Member A", 
        "Secondary Lead": "Member C", 
        "QA Lead": "Member D", 
        "Project Handler": "Member G", 
        "Open Tickets": 4
    }
])

# Interactive Browser-based Spreadsheet
df = st.data_editor(initial_data, num_rows="dynamic", use_container_width=True)

# 4. Filter Controls
st.divider()
f_col1, f_col2 = st.columns(2)
with f_col1:
    selected_project = st.multiselect(
        "Filter View by Active Project:", 
        options=["PAY NSDL", "IATA", "S2PAY"], 
        default=["PAY NSDL", "IATA", "S2PAY"]
    )
with f_col2:
    selected_status = st.multiselect(
        "Filter View by Status:", 
        options=df["Status"].unique(), 
        default=df["Status"].unique()
    )

filtered_df = df[(df["Project"].isin(selected_project)) & (df["Status"].isin(selected_status))]

# 5. SME KPI Performance Metrics
st.divider()
st.subheader("📊 Executive Metrics & Risk Indicators")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Merchants Managed", len(filtered_df))
m2.metric("Active Onboardings", len(filtered_df[filtered_df["Status"].isin(["On Track", "Delayed"])]))
m3.metric("Blocked (SME Intervention)", len(filtered_df[filtered_df["Status"] == "Blocked"]))
m4.metric("Pending QA & Support Tickets", filtered_df["Open Tickets"].sum())

# 6. Visual Operations Charts
st.divider()
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Pipeline Stage Distribution")
    fig_stage = px.bar(
        filtered_df, x="Project", color="Stage", 
        title="Merchant Count by Onboarding Stage", barmode="stack"
    )
    st.plotly_chart(fig_stage, use_container_width=True)

with chart_col2:
    st.subheader("Operational Health Breakdown")
    fig_status = px.pie(
        filtered_df, names="Status", title="Health Status Ratio",
        color="Status",
        color_discrete_map={"Completed": "green", "On Track": "blue", "Delayed": "orange", "Blocked": "red"}
    )
    st.plotly_chart(fig_status, use_container_width=True)
