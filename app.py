import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# Page setup
st.set_page_config(page_title="TSP Multi-Project Enterprise CRM", page_icon="🏦", layout="wide")

# Database Initialization (Embedded SQLite - No External Sheets/Drive Needed)
def init_db():
    conn = sqlite3.connect('tsp_crm_production.db')
    c = conn.cursor()
    
    # 1. PAY NSDL Project Table
    c.execute('''CREATE TABLE IF NOT EXISTS pay_nsdl (
                    merchant_id TEXT PRIMARY KEY,
                    merchant_name TEXT,
                    terminal_id TEXT,
                    api_status TEXT,
                    nsdl_compliance TEXT,
                    status TEXT,
                    assigned_handler TEXT,
                    open_tickets INTEGER,
                    last_updated_by TEXT)''')
                    
    # 2. IATA Project Table
    c.execute('''CREATE TABLE IF NOT EXISTS iata (
                    merchant_id TEXT PRIMARY KEY,
                    agency_name TEXT,
                    iata_code TEXT,
                    bsp_settlement TEXT,
                    gds_integration TEXT,
                    status TEXT,
                    assigned_handler TEXT,
                    open_tickets INTEGER,
                    last_updated_by TEXT)''')
                    
    # 3. S2PAY Project Table
    c.execute('''CREATE TABLE IF NOT EXISTS s2pay (
                    merchant_id TEXT PRIMARY KEY,
                    merchant_name TEXT,
                    gateway_mid TEXT,
                    switch_route TEXT,
                    risk_evaluation TEXT,
                    status TEXT,
                    assigned_handler TEXT,
                    open_tickets INTEGER,
                    last_updated_by TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Database Helper Functions
def run_query(query, params=()):
    conn = sqlite3.connect('tsp_crm_production.db')
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def execute_cmd(cmd, params=()):
    conn = sqlite3.connect('tsp_crm_production.db')
    c = conn.cursor()
    c.execute(cmd, params)
    conn.commit()
    conn.close()

# Sidebar: User Authentication / Identity Switcher
st.sidebar.header("👤 User Identity")
current_user = st.sidebar.selectbox("Log in as:", [
    "Member A (SME / Primary Ops Lead)",
    "Member C (Secondary Ops Lead)",
    "Member D (Universal QA Lead)",
    "Member B (PAY NSDL Handler)",
    "Member E (PAY NSDL Handler)",
    "Member F (IATA Handler)",
    "Member G (S2PAY Handler)"
])

st.sidebar.divider()
st.sidebar.info(f"**Logged in user:** {current_user}")

# Header
st.title("🏦 Banking Operations & Merchant Onboarding CRM")
st.caption("Custom Enterprise Multi-Project Database & Performance Tracker")

# Main Navigation
tab_dash, tab_manage, tab_entry = st.tabs([
    "📊 Executive Performance & Analytics", 
    "📁 Manage Merchant Records (By Project)", 
    "➕ Onboard New Merchant"
])

# --------------------------------------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# --------------------------------------------------------------------------
with tab_dash:
    st.subheader("📈 Overall Operations & Team Performance")
    
    df_nsdl = run_query("SELECT * FROM pay_nsdl")
    df_iata = run_query("SELECT * FROM iata")
    df_s2pay = run_query("SELECT * FROM s2pay")
    
    col1, col2, col3, col4 = st.columns(4)
    total_merchants = len(df_nsdl) + len(df_iata) + len(df_s2pay)
    
    total_tickets = (df_nsdl['open_tickets'].sum() if not df_nsdl.empty else 0) + \
                    (df_iata['open_tickets'].sum() if not df_iata.empty else 0) + \
                    (df_s2pay['open_tickets'].sum() if not df_s2pay.empty else 0)
                    
    col1.metric("Total Active Merchants", total_merchants)
    col2.metric("PAY NSDL Merchants", len(df_nsdl))
    col3.metric("IATA Merchants", len(df_iata))
    col4.metric("S2PAY Merchants", len(df_s2pay))
    
    st.divider()
    
    # Project Breakdown Graphs
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Project Distribution Summary")
        project_counts = pd.DataFrame({
            "Project": ["PAY NSDL", "IATA", "S2PAY"],
            "Count": [len(df_nsdl), len(df_iata), len(df_s2pay)]
        })
        fig = px.bar(project_counts, x="Project", y="Count", color="Project", title="Merchants per Project Line")
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.subheader("Ticket Distribution")
        st.metric("Total Active Escalation Tickets", total_tickets)
        st.info("Member D (QA) and Member A (SME) oversee ticket resolution across all 3 active projects.")

# --------------------------------------------------------------------------
# TAB 2: MANAGE MERCHANT RECORDS BY PROJECT
# --------------------------------------------------------------------------
with tab_manage:
    selected_project = st.selectbox("Select Project Workspace:", ["PAY NSDL", "IATA", "S2PAY"])
    
    if selected_project == "PAY NSDL":
        st.subheader("📋 PAY NSDL Specific Database")
        data = run_query("SELECT * FROM pay_nsdl")
        if data.empty:
            st.warning("No records found in PAY NSDL database. Use the 'Onboard New Merchant' tab to add records.")
        else:
            edited_data = st.data_editor(data, num_rows="dynamic", key="nsdl_edit", use_container_width=True)
            if st.button("Save Changes to PAY NSDL Database"):
                for _, row in edited_data.iterrows():
                    execute_cmd("""UPDATE pay_nsdl SET 
                                    merchant_name=?, terminal_id=?, api_status=?, 
                                    nsdl_compliance=?, status=?, assigned_handler=?, 
                                    open_tickets=?, last_updated_by=? WHERE merchant_id=?""",
                                (row['merchant_name'], row['terminal_id'], row['api_status'], 
                                 row['nsdl_compliance'], row['status'], row['assigned_handler'], 
                                 row['open_tickets'], current_user, row['merchant_id']))
                st.success("Database updated successfully!")

    elif selected_project == "IATA":
        st.subheader("✈️ IATA Specific Database")
        data = run_query("SELECT * FROM iata")
        if data.empty:
            st.warning("No records found in IATA database.")
        else:
            edited_data = st.data_editor(data, num_rows="dynamic", key="iata_edit", use_container_width=True)
            if st.button("Save Changes to IATA Database"):
                for _, row in edited_data.iterrows():
                    execute_cmd("""UPDATE iata SET 
                                    agency_name=?, iata_code=?, bsp_settlement=?, 
                                    gds_integration=?, status=?, assigned_handler=?, 
                                    open_tickets=?, last_updated_by=? WHERE merchant_id=?""",
                                (row['agency_name'], row['iata_code'], row['bsp_settlement'], 
                                 row['gds_integration'], row['status'], row['assigned_handler'], 
                                 row['open_tickets'], current_user, row['merchant_id']))
                st.success("IATA Database updated successfully!")

    elif selected_project == "S2PAY":
        st.subheader("💳 S2PAY Specific Database")
        data = run_query("SELECT * FROM s2pay")
        if data.empty:
            st.warning("No records found in S2PAY database.")
        else:
            edited_data = st.data_editor(data, num_rows="dynamic", key="s2pay_edit", use_container_width=True)
            if st.button("Save Changes to S2PAY Database"):
                for _, row in edited_data.iterrows():
                    execute_cmd("""UPDATE s2pay SET 
                                    merchant_name=?, gateway_mid=?, switch_route=?, 
                                    risk_evaluation=?, status=?, assigned_handler=?, 
                                    open_tickets=?, last_updated_by=? WHERE merchant_id=?""",
                                (row['merchant_name'], row['gateway_mid'], row['switch_route'], 
                                 row['risk_evaluation'], row['status'], row['assigned_handler'], 
                                 row['open_tickets'], current_user, row['merchant_id']))
                st.success("S2PAY Database updated successfully!")

# --------------------------------------------------------------------------
# TAB 3: ONBOARD NEW MERCHANT (DYNAMIC CRITERIA FORM)
# --------------------------------------------------------------------------
with tab_entry:
    st.subheader("➕ Create New Merchant Record")
    target_project = st.radio("Select Target Project Workflow:", ["PAY NSDL", "IATA", "S2PAY"], horizontal=True)
    
    with st.form("dynamic_merchant_form"):
        st.markdown(f"### Onboarding Form for: **{target_project}**")
        
        m_id = st.text_input("Merchant ID (Required)", value="M-101")
        
        # Dynamic Columns based on Selected Project
        if target_project == "PAY NSDL":
            m_name = st.text_input("Merchant / Company Name")
            term_id = st.text_input("NSDL Terminal ID")
            api_stat = st.selectbox("API Integration Status", ["Pending", "In Progress", "Verified", "Failed"])
            compliance = st.selectbox("NSDL Compliance Check", ["Passed", "Pending Documents", "Rejected"])
            status = st.selectbox("Overall Health", ["On Track", "Delayed", "Blocked", "Live"])
            handler = st.selectbox("Assigned Project Handler", ["Member B", "Member E", "Member A", "Member C"])
            tickets = st.number_input("Open Tickets", min_value=0, value=0)
            
        elif target_project == "IATA":
            m_name = st.text_input("Agency / Travel Merchant Name")
            iata_code = st.text_input("IATA Numeric Code")
            bsp_stat = st.selectbox("BSP Settlement Status", ["Active", "Suspended", "Under Review"])
            gds_type = st.selectbox("GDS Integration Engine", ["Amadeus", "Sabre", "Travelport", "Custom Direct"])
            status = st.selectbox("Overall Health", ["On Track", "Delayed", "Blocked", "Live"])
            handler = st.selectbox("Assigned Project Handler", ["Member F", "Member A", "Member C"])
            tickets = st.number_input("Open Tickets", min_value=0, value=0)

        elif target_project == "S2PAY":
            m_name = st.text_input("Merchant Name")
            gateway_mid = st.text_input("Gateway MID (Merchant ID)")
            switch_route = st.selectbox("Switch Route Provider", ["Primary Route A", "Backup Route B", "Direct Bank Switch"])
            risk_eval = st.selectbox("Risk Evaluation Category", ["Low Risk", "Medium Risk", "High Risk / Fraud Monitoring"])
            status = st.selectbox("Overall Health", ["On Track", "Delayed", "Blocked", "Live"])
            handler = st.selectbox("Assigned Project Handler", ["Member G", "Member A", "Member C"])
            tickets = st.number_input("Open Tickets", min_value=0, value=0)
            
        submit_btn = st.form_submit_button("Create & Store Record")
        
        if submit_btn:
            if target_project == "PAY NSDL":
                execute_cmd("""INSERT INTO pay_nsdl VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                            (m_id, m_name, term_id, api_stat, compliance, status, handler, tickets, current_user))
            elif target_project == "IATA":
                execute_cmd("""INSERT INTO iata VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                            (m_id, m_name, iata_code, bsp_stat, gds_type, status, handler, tickets, current_user))
            elif target_project == "S2PAY":
                execute_cmd("""INSERT INTO s2pay VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                            (m_id, m_name, gateway_mid, switch_route, risk_eval, status, handler, tickets, current_user))
                            
            st.success(f"Successfully recorded '{m_id}' into {target_project} Database!")
