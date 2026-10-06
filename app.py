import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import json

st.set_page_config(page_title="Dynamic Banking Operations CRM", page_icon="🏦", layout="wide")

# --------------------------------------------------------------------------
# DATABASE INITIALIZATION (SQLite Engine)
# --------------------------------------------------------------------------
def get_db():
    conn = sqlite3.connect("tsp_crm_v2.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    # User / Team Table
    c.execute('''CREATE TABLE IF NOT EXISTS team_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id TEXT UNIQUE,
                    name TEXT,
                    assigned_projects TEXT,
                    support_roles TEXT,
                    access_level TEXT)''')
    
    # Custom Dynamic Columns Schema Registry
    c.execute('''CREATE TABLE IF NOT EXISTS project_schema (
                    project_name TEXT PRIMARY KEY,
                    columns_json TEXT)''')

    # Master Merchants Table
    c.execute('''CREATE TABLE IF NOT EXISTS merchants (
                    merchant_id TEXT PRIMARY KEY,
                    merchant_name TEXT,
                    project_name TEXT,
                    status TEXT,
                    assigned_handlers TEXT,
                    support_roles TEXT,
                    open_tickets INTEGER,
                    extra_fields_json TEXT,
                    last_updated_by TEXT)''')
    
    # Seed Initial Team Data
    c.execute("SELECT COUNT(*) FROM team_members")
    if c.fetchone()[0] == 0:
        initial_team = [
            ("Member A", "Ops Admin / Lead", json.dumps(["PAY NSDL", "IATA", "S2PAY", "AIRTEL CHIMPE", "AIRTEL NEXDHA", "ESSAS FINO"]), json.dumps(["QUALITY ANALYST"]), "Admin"),
            ("Member B", "INDUMATHI", json.dumps(["PAY NSDL", "S2PAY"]), json.dumps(["FLOOR SUPPORT"]), "Team Member"),
            ("Member C", "ATHUL", json.dumps(["IATA", "AIRTEL CHIMPE"]), json.dumps(["DATA MANAGEMENT"]), "Team Member"),
            ("Member D", "MANJUSHA", json.dumps(["PAY NSDL", "ESSAS FINO"]), json.dumps(["QUALITY ANALYST"]), "Team Member"),
            ("Member E", "MIDHUN", json.dumps(["AIRTEL NEXDHA"]), json.dumps(["SEAL AND PRINT MANAGEMENT"]), "Team Member"),
            ("Member F", "MANJUSHA", json.dumps(["IATA"]), json.dumps(["CLEARANCE EXECUTIVE"]), "Team Member"),
            ("Member G", "TAMIL", json.dumps(["S2PAY", "ESSAS FINO"]), json.dumps(["FLOOR SUPPORT"]), "Team Member"),
        ]
        c.executemany("INSERT INTO team_members (member_id, name, assigned_projects, support_roles, access_level) VALUES (?, ?, ?, ?, ?)", initial_team)
    
    # Seed Initial Projects & Schemas
    c.execute("SELECT COUNT(*) FROM project_schema")
    if c.fetchone()[0] == 0:
        default_projects = {
            "PAY NSDL": ["Company Name", "MCC", "Category", "Bank Name", "Account No", "IFSC", "Domain Mail ID", "GST", "POC Name"],
            "IATA": ["Agency Name", "IATA Numeric Code", "BSP Settlement", "GDS Engine", "Postal Code", "Account Number"],
            "S2PAY": ["Merchant Name", "Gateway MID", "Switch Route", "Risk Category", "Bank Switch"],
            "AIRTEL CHIMPE": ["Merchant ID", "Agent Code", "KYC Status", "Circle", "Terminal ID"],
            "AIRTEL NEXDHA": ["Enterprise Name", "Nexdha ID", "API Routing", "Compliance Status"],
            "ESSAS FINO": ["Fino Client Code", "Settlement Account", "IFSC Code", "Branch Code"]
        }
        for proj, cols in default_projects.items():
            c.execute("INSERT INTO project_schema VALUES (?, ?)", (proj, json.dumps(cols)))
            
    conn.commit()
    conn.close()

init_db()

# --------------------------------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------------------------------
def load_team():
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM team_members", conn)
    conn.close()
    return df

def load_schemas():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM project_schema")
    rows = c.fetchall()
    conn.close()
    return {r[0]: json.loads(r[1]) for r in rows}

# --------------------------------------------------------------------------
# SIDEBAR: USER AUTHENTICATION & ACCESS CONTROL
# --------------------------------------------------------------------------
st.sidebar.title("🏦 CRM Identity & Access")

team_df = load_team()
user_options = [f"{row['member_id']} - {row['name']} ({row['access_level']})" for _, row in team_df.iterrows()]
selected_identity = st.sidebar.selectbox("Log in as User:", user_options)

selected_row = team_df[team_df['member_id'] == selected_identity.split(" - ")[0]].iloc[0]
current_user_id = selected_row['member_id']
current_user_name = selected_row['name']
current_user_role = selected_row['access_level']
user_projects = json.loads(selected_row['assigned_projects'])
user_support_roles = json.loads(selected_row['support_roles'])

st.sidebar.divider()
st.sidebar.markdown(f"**Logged User:** {current_user_name}")
st.sidebar.markdown(f"**Access Role:** `{current_user_role}`")
st.sidebar.markdown(f"**Assigned Projects:** {', '.join(user_projects)}")

# --------------------------------------------------------------------------
# MAIN INTERFACE NAVIGATION
# --------------------------------------------------------------------------
st.title("🏦 Banking Operations & Multi-Project CRM")

# Level-Wise Access Routing
if current_user_role == "Admin":
    navigation_tabs = st.tabs([
        "📊 Executive Analytics Dashboard", 
        "📁 Multi-Project Workspaces", 
        "➕ Onboard Merchant Record", 
        "⚙️ Dynamic System Configuration"
    ])
else:
    navigation_tabs = st.tabs([
        "📋 My Assigned Tasks Workspace", 
        "➕ Onboard New Merchant", 
        "👤 My Profile & Support Roles"
    ])

# --------------------------------------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD (Admin Only) or MY TASKS (Team)
# --------------------------------------------------------------------------
with navigation_tabs[0]:
    conn = get_db()
    df_merchants = pd.read_sql_query("SELECT * FROM merchants", conn)
    conn.close()

    if current_user_role == "Admin":
        st.subheader("📊 Centralized Performance & Executive Overview")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Merchants", len(df_merchants))
        m2.metric("Active Live Projects", len(load_schemas()))
        m3.metric("Total Open Escalations", df_merchants['open_tickets'].sum() if not df_merchants.empty else 0)
        m4.metric("Active Operations Team", len(team_df))

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Merchant Distribution by Project")
            if not df_merchants.empty:
                fig_bar = px.bar(df_merchants, x="project_name", color="status", title="Project Status Breakdown")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No merchant records available.")
        with c2:
            st.markdown("### Operational Health Overview")
            if not df_merchants.empty:
                fig_pie = px.pie(df_merchants, names="status", title="Overall Pipeline Health")
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No data for pie chart.")
    else:
        st.subheader(f"📋 Personal Workspace: {current_user_name}")
        st.info("Viewing records filtered exclusively for your assigned projects and handler allocations.")
        
        if not df_merchants.empty:
            my_records = df_merchants[
                df_merchants['project_name'].isin(user_projects) | 
                df_merchants['assigned_handlers'].str.contains(current_user_name, na=False)
            ]
            st.dataframe(my_records, use_container_width=True)
        else:
            st.warning("No records assigned to you yet.")

# --------------------------------------------------------------------------
# TAB 2: MULTI-PROJECT WORKSPACES / ONBOARD MERCHANT
# --------------------------------------------------------------------------
if current_user_role == "Admin":
    with navigation_tabs[1]:
        st.subheader("📁 Project-Specific Dynamic Workspaces")
        schemas = load_schemas()
        
        selected_proj = st.selectbox("Select Project Workspace:", list(schemas.keys()))
        
        conn = get_db()
        proj_merchants = pd.read_sql_query("SELECT * FROM merchants WHERE project_name = ?", conn, params=(selected_proj,))
        conn.close()
        
        st.markdown(f"**Custom Columns for {selected_proj}:** {', '.join(schemas[selected_proj])}")
        
        if not proj_merchants.empty:
            st.data_editor(proj_merchants, num_rows="dynamic", use_container_width=True, key=f"editor_{selected_proj}")
        else:
            st.warning(f"No records currently registered under {selected_proj}.")

    with navigation_tabs[2]:
        st.subheader("➕ Onboard New Merchant Record")
        schemas = load_schemas()
        
        target_project = st.selectbox("Select Target Project Workflow:", list(schemas.keys()))
        
        with st.form("add_merchant_form"):
            st.markdown(f"### Onboarding Entry Form: **{target_project}**")
            m_id = st.text_input("Merchant ID / Registration Code (Required)")
            m_name = st.text_input("Merchant / Company Name")
            m_status = st.selectbox("Status Health", ["In Progress", "LIVE", "STOP", "DOCUMENT SUBMITTED", "BLOCKED"])
            
            # Multi-Select Project Handlers & Support Roles
            assigned_handlers = st.multiselect("Assign Team Handlers:", team_df['name'].unique())
            assigned_support = st.multiselect("Assign Support Roles:", ["FLOOR SUPPORT", "QUALITY ANALYST", "SEAL AND PRINT MANAGEMENT", "DATA MANAGEMENT", "CLEARANCE EXECUTIVE"])
            
            tickets = st.number_input("Open Escalation Tickets", min_value=0, value=0)
            
            # Dynamic Custom Fields based on Project Schema
            st.markdown("#### Project-Specific Custom Fields")
            custom_data = {}
            for col in schemas[target_project]:
                custom_data[col] = st.text_input(f"{col}")
                
            submitted = st.form_submit_button("Create Merchant Record")
            if submitted:
                conn = get_db()
                c = conn.cursor()
                c.execute("""INSERT INTO merchants VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                          (m_id, m_name, target_project, m_status, json.dumps(assigned_handlers),
                           json.dumps(assigned_support), tickets, json.dumps(custom_data), current_user_name))
                conn.commit()
                conn.close()
                st.success(f"Merchant '{m_name}' successfully added to {target_project}!")

# --------------------------------------------------------------------------
# TAB 3 / 4: DYNAMIC SYSTEM CONFIGURATION & PROJECT CREATION (Admin Only)
# --------------------------------------------------------------------------
if current_user_role == "Admin":
    with navigation_tabs[3]:
        st.subheader("⚙️ Dynamic Project & Team Management Engine")
        
        config_col1, config_col2 = st.columns(2)
        
        # Add New Project & Dynamic Columns
        with config_col1:
            st.markdown("### ➕ Create New Project Line")
            with st.form("new_project_form"):
                new_proj_name = st.text_input("New Project Name (e.g., AIRTEL PAYMENTS)")
                custom_cols_raw = st.text_area("Define Custom Columns (Comma Separated):", value="Terminal ID, API Key, Settlement Status")
                
                create_proj_btn = st.form_submit_button("Register New Project Schema")
                if create_proj_btn:
                    cols_list = [c.strip() for c in custom_cols_raw.split(",") if c.strip()]
                    conn = get_db()
                    c = conn.cursor()
                    c.execute("INSERT OR REPLACE INTO project_schema VALUES (?, ?)", (new_proj_name, json.dumps(cols_list)))
                    conn.commit()
                    conn.close()
                    st.success(f"Project '{new_proj_name}' registered with {len(cols_list)} custom columns!")
                    st.rerun()

        # Manage Team Members & Roles
        with config_col2:
            st.markdown("### 👤 Add / Edit Team Member")
            all_projects = list(load_schemas().keys())
            all_support = ["FLOOR SUPPORT", "QUALITY ANALYST", "SEAL AND PRINT MANAGEMENT", "DATA MANAGEMENT", "CLEARANCE EXECUTIVE"]
            
            with st.form("team_management_form"):
                m_code = st.text_input("Member Code (e.g., Member H)")
                m_real_name = st.text_input("Full Name")
                m_projs = st.multiselect("Assign Projects:", all_projects)
                m_roles = st.multiselect("Assign Support Roles:", all_support)
                m_access = st.selectbox("System Access Role:", ["Team Member", "Admin"])
                
                team_submit = st.form_submit_button("Save Team Member Profile")
                if team_submit:
                    conn = get_db()
                    c = conn.cursor()
                    c.execute("INSERT OR REPLACE INTO team_members (member_id, name, assigned_projects, support_roles, access_level) VALUES (?, ?, ?, ?, ?)",
                              (m_code, m_real_name, json.dumps(m_projs), json.dumps(m_roles), m_access))
                    conn.commit()
                    conn.close()
                    st.success(f"Profile for {m_real_name} updated successfully!")
                    st.rerun()

else:
    # Team Member Profile View
    with navigation_tabs[1]:
        st.subheader("➕ Onboard New Merchant")
        st.info("Fill in onboarding details for your assigned projects.")
    with navigation_tabs[2]:
        st.subheader("👤 My Assigned Profile & Support Criteria")
        st.json({
            "Member Name": current_user_name,
            "User Code": current_user_id,
            "Assigned Projects": user_projects,
            "Support Roles": user_support_roles,
            "Access Role": current_user_role
        })
