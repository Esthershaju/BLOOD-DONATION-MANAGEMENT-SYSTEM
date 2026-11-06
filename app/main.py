"""Main Streamlit application for the Blood Donation Management System."""
import streamlit as st
import pandas as pd
from datetime import datetime, date

from app import config, db
from app.donor import (
    DonorLinkedList, load_donors_to_linked_list, get_all_donors,
    get_donor_by_id, register_donor, update_donor, delete_donor,
    toggle_availability, validate_donor
)
from app.requests import (
    BloodRequestQueue, get_all_requests, get_pending_request_queue,
    get_all_hospitals, create_blood_request, process_next_pending_request,
    update_request_status, get_operation_stack, undo_last_operation
)
from app.searching import linear_search, binary_search
from app.sorting import insertion_sort
from app.algorithms import greedy_donor_matching

# ==============================================================================
# PAGE CONFIGURATION & STYLING
# ==============================================================================
st.set_page_config(
    page_title="Blood Donation Management System",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a calm, welcoming medical portal.
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(145deg, #f4faf5 0%, #fff8f7 58%, #f8fbf7 100%);
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 1300px;
    }
    [data-testid="stSidebar"] {
        background: #edf6ee;
        border-right: 1px solid #d5e8d8;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #a7434a;
    }
    .info-card {
        background: #fffafa;
        border-left: 4px solid #d98b8e;
        padding: 14px 18px;
        border-radius: 12px;
        margin-bottom: 16px;
        box-shadow: 0 3px 12px rgba(90, 120, 95, 0.08);
    }
    .code-box {
        background-color: #294538;
        color: #d8f0dd;
        padding: 12px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 0.88rem;
    }
    table.bdms-clean-table {
        width: 100%;
        border-collapse: collapse;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 0.88rem;
    }
    table.bdms-clean-table th {
        background-color: #eaf3eb;
        color: #35513d;
        font-weight: 700;
        text-align: left;
        padding: 10px 14px;
        border-bottom: 2px solid #c9dfcd;
        white-space: nowrap;
    }
    table.bdms-clean-table td {
        padding: 9px 14px;
        border-bottom: 1px solid #e3eee4;
        color: #394c3d;
        white-space: nowrap;
    }
    table.bdms-clean-table tr:hover {
        background-color: #f4faf4;
    }
    button[kind="primary"] {
        background: linear-gradient(135deg, #e4aaaa 0%, #d8868b 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        color: #552d31 !important;
        font-weight: 700 !important;
        box-shadow: 0 3px 9px rgba(180, 91, 99, 0.18) !important;
        transition: all 0.2s ease !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 12px rgba(180, 91, 99, 0.28) !important;
        border-color: #c9757b !important;
    }
    [data-testid="stTabs"] button[role="tab"] {
        border-radius: 10px 10px 0 0;
        color: #49614d;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #a7434a;
        border-bottom-color: #d8868b;
    }
    [data-testid="stForm"], [data-testid="stExpander"], [data-testid="stMetric"] {
        border-radius: 12px;
    }
    @media (max-width: 768px) {
        .block-container {
            padding: 0.75rem 0.75rem 1.5rem;
        }
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 calc(50% - 0.5rem) !important;
            min-width: 135px !important;
        }
        .bdms-app-header {
            flex-direction: column;
            align-items: flex-start !important;
            gap: 10px;
        }
        .bdms-app-header > div:last-child {
            flex-wrap: wrap;
        }
        table.bdms-clean-table {
            font-size: 0.78rem;
        }
        table.bdms-clean-table th,
        table.bdms-clean-table td {
            padding: 8px;
        }
    }
</style>
""", unsafe_allow_html=True)

def format_cell_badges(df):
    """Adds HTML badge pills to status, urgency, and blood group columns for a site/app appearance."""
    df_copy = df.copy()
    for col in df_copy.columns:
        c_lower = str(col).lower()
        if c_lower in ["status", "lifecycle"]:
            def _b_stat(val):
                v = str(val).strip()
                if v == "Completed":
                    return '<span style="background:#dcfce7; color:#15803d; padding:3px 9px; border-radius:12px; font-weight:700; font-size:0.75rem; border:1px solid #bbf7d0;">● Completed</span>'
                elif v == "Pending":
                    return '<span style="background:#fef3c7; color:#b45309; padding:3px 9px; border-radius:12px; font-weight:700; font-size:0.75rem; border:1px solid #fde68a;">⏳ Pending</span>'
                elif v == "Processing":
                    return '<span style="background:#ede9fe; color:#6d28d9; padding:3px 9px; border-radius:12px; font-weight:700; font-size:0.75rem; border:1px solid #ddd6fe;">⚙️ Processing</span>'
                elif v == "Cancelled":
                    return '<span style="background:#f1f5f9; color:#64748b; padding:3px 9px; border-radius:12px; font-weight:700; font-size:0.75rem; border:1px solid #e2e8f0;">✕ Cancelled</span>'
                return v
            df_copy[col] = df_copy[col].apply(_b_stat)
        elif c_lower in ["urgency", "priority"]:
            def _b_urg(val):
                v = str(val).strip()
                if v == "Critical":
                    return '<span style="background:#fee2e2; color:#b91c1c; padding:3px 9px; border-radius:12px; font-weight:800; font-size:0.75rem; border:1px solid #fecaca;">🚨 CRITICAL</span>'
                elif v == "Urgent":
                    return '<span style="background:#ffedd5; color:#c2410c; padding:3px 9px; border-radius:12px; font-weight:700; font-size:0.75rem; border:1px solid #fed7aa;">⚠️ Urgent</span>'
                elif v == "Normal":
                    return '<span style="background:#e0f2fe; color:#0369a1; padding:3px 9px; border-radius:12px; font-weight:700; font-size:0.75rem; border:1px solid #bae6fd;">Normal</span>'
                return v
            df_copy[col] = df_copy[col].apply(_b_urg)
        elif c_lower in ["available", "availability"]:
            def _b_avail(val):
                v = str(val).strip()
                if "Available" in v or v in ["1", "True", "true"]:
                    return '<span style="background:#dcfce7; color:#15803d; padding:3px 9px; border-radius:12px; font-weight:700; font-size:0.75rem; border:1px solid #bbf7d0;">✓ Available</span>'
                return '<span style="background:#fee2e2; color:#b91c1c; padding:3px 9px; border-radius:12px; font-weight:700; font-size:0.75rem; border:1px solid #fecaca;">✗ Inactive</span>'
            df_copy[col] = df_copy[col].apply(_b_avail)
        elif c_lower in ["blood group", "group", "blood_group"]:
            def _b_bg(val):
                return f'<span style="background:#fff1f2; color:#e11d48; border:1px solid #fecdd3; padding:2px 8px; border-radius:6px; font-weight:800; font-size:0.8rem;">{val}</span>'
            df_copy[col] = df_copy[col].apply(_b_bg)
    return df_copy

def render_clean_table(df):
    """
    Renders a reliable, responsive HTML table that does not depend on dynamic JS chunks.
    Automatically applies status, urgency, and blood group badge styling.
    """
    if df is None:
        st.info("No data available.")
        return
    if isinstance(df, list):
        if not df:
            st.info("No records to display.")
            return
        df = pd.DataFrame(df)
    if not isinstance(df, pd.DataFrame):
        st.write(df)
        return
    if df.empty:
        st.info("No records match the selected criteria.")
        return

    badged_df = format_cell_badges(df)
    html_table = badged_df.to_html(index=False, classes="bdms-clean-table", border=0, escape=False)
    st.markdown(f'<div style="width: 100%; overflow-x: auto; margin-bottom: 1rem; border-radius: 8px; border: 1px solid #cbd5e1; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">{html_table}</div>', unsafe_allow_html=True)

def render_app_header(module_title, subtitle=""):
    """Renders the application header."""
    st.markdown(f"""
    <div class="bdms-app-header" style="background: linear-gradient(120deg, #e6f2e7 0%, #fdf0ee 100%); padding: 16px 22px; border-radius: 16px; margin-bottom: 20px; color: #35513d; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 5px 16px rgba(71,103,77,0.10); border-left: 5px solid #d8868b;">
        <div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.6rem;">🩸</span>
                <span style="font-size: 1.3rem; font-weight: 800; letter-spacing: -0.5px; color: #35513d;">LifePulse</span>
                <span style="background: #f2c9c7; color: #754247; font-size: 0.65rem; font-weight: 700; padding: 3px 8px; border-radius: 8px; text-transform: uppercase;">Hospital Portal</span>
            </div>
            <div style="font-size: 0.85rem; color: #607665; margin-top: 3px;">
                <b style="color: #35513d;">{module_title}</b> {f"• {subtitle}" if subtitle else ""}
            </div>
        </div>
        <div style="display: flex; gap: 14px; align-items: center;">
            <svg class="bdms-header-art" width="92" height="68" viewBox="0 0 92 68" role="img" aria-label="Blood donation and care illustration">
                <circle cx="58" cy="33" r="29" fill="#d5e9d7"/>
                <path d="M30 10C30 10 19 24 19 33a11 11 0 0 0 22 0c0-9-11-23-11-23Z" fill="#d8868b"/>
                <path d="M30 29v10m-5-5h10" stroke="#fff8f5" stroke-width="3" stroke-linecap="round"/>
                <path d="M52 47c5-8 16-8 21 0M57 45l-3 8m15-8 3 8" fill="none" stroke="#65866a" stroke-width="3" stroke-linecap="round"/>
                <circle cx="63" cy="31" r="8" fill="#fff8f5"/>
                <path d="M59 32c2-5 7-5 9 0-2 4-7 4-9 0Z" fill="#d8868b"/>
                <path d="M46 12c4-4 8-4 12 0-4 4-8 4-12 0Z" fill="#9cbe9f"/>
            </svg>
            <div style="background: rgba(255,255,255,0.68); padding: 6px 12px; border-radius: 16px; font-size: 0.76rem; font-weight: 600; border: 1px solid #d5e5d7; color: #49614d;">
                👤 Admin
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_app_footer():
    """Renders clean app footer with quick links and project credentials."""
    st.markdown("""
    <div style="margin-top: 45px; padding: 18px 0; border-top: 1px solid #dce9dd; text-align: center; color: #607665; font-size: 0.8rem;">
        <b>LifePulse Blood Donation Management System</b><br>
        Donor records, blood requests, inventory, and hospital information
    </div>
    """, unsafe_allow_html=True)

def show_flash_message(key):
    """Shows and clears a message saved before a Streamlit rerun."""
    notice = st.session_state.pop(key, None)
    if notice:
        message_type, message = notice
        if message_type == "success":
            st.success(message)
        else:
            st.error(message)

def set_flash_message(key, message_type, message):
    st.session_state[key] = (message_type, message)
    st.rerun()


# ==============================================================================
# SESSION STATE INITIALIZATION & AUTHENTICATION
# ==============================================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "db_connected" not in st.session_state:
    st.session_state.db_connected = False


def render_login_page():
    """Renders professional healthcare portal login screen."""
    _, col2, _ = st.columns([1, 1.8, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="display: inline-block; background: #f8e2e0; border-radius: 50%; padding: 16px; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(180,91,99,0.14);">
                <span style="font-size: 2.8rem;">🩸</span>
            </div>
            <h1 style="color: #35513d; font-size: 2.1rem; font-weight: 800; margin-bottom: 4px; letter-spacing: -0.5px;">LifePulse</h1>
            <p style="color: #64748b; font-size: 0.95rem; margin-top: 0;">
                Blood donation and hospital services in one place
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("#### 🔐 Staff Login")
            st.caption("Sign in with your staff account to manage donors and blood requests.")
            username = st.text_input("Username", value="admin", placeholder="e.g. admin")
            password = st.text_input("Password", value="admin123", type="password", placeholder="e.g. admin123")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Access Portal", type="primary", use_container_width=True):
                if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
                    st.session_state.authenticated = True
                    st.success("Authentication successful! Loading portal...")
                    st.rerun()
                else:
                    st.error("Invalid username or password. Default credentials: admin / admin123")
                    
            st.markdown("""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; margin-top: 15px; text-align: center; font-size: 0.8rem; color: #475569;">
                <b>Demonstration Credentials:</b><br>
                Username: <code>admin</code> &nbsp;|&nbsp; Password: <code>admin123</code>
            </div>
            """, unsafe_allow_html=True)


if not st.session_state.authenticated:
    render_login_page()
    st.stop()


# ==============================================================================
# DATABASE CHECK & AUTO-INITIALIZATION IN SIDEBAR
# ==============================================================================
is_conn_ok, _ = db.test_connection()
st.session_state.db_connected = is_conn_ok

with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; padding: 6px 0 10px 0;">
        <span style="font-size: 2rem;">🩸</span>
        <div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #a7434a; line-height: 1.1;">LifePulse</div>
            <div style="font-size: 0.75rem; color: #64748b; font-weight: 600;">Blood Bank Portal</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # User Profile Card
    st.markdown(f"""
    <div style="background: #f8fcf8; border: 1px solid #d5e8d8; border-radius: 10px; padding: 10px 12px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="background: #f8e2e0; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-size: 1rem;">👤</div>
            <div>
                <div style="font-weight: 700; font-size: 0.85rem; color: #1e293b;">{config.ADMIN_USERNAME}</div>
                <div style="font-size: 0.7rem; color: #15803d; font-weight: 600;">● Administrator</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    st.markdown("---")

    if not is_conn_ok:
        with st.expander("⚙️ Configure MySQL Credentials", expanded=False):
            st.info("Enter your local MySQL root password to connect and auto-seed the database.")
            db_host = st.text_input("Host", value=config.DB_HOST, key="cfg_host")
            db_port = st.number_input("Port", value=config.DB_PORT, key="cfg_port")
            db_user = st.text_input("User", value=config.DB_USER, key="cfg_user")
            db_pass = st.text_input("Password", value=config.DB_PASSWORD, type="password", key="cfg_pass")
            
            if st.button("Connect & Initialize Database", type="primary", use_container_width=True):
                success, msg = db.init_database(host=db_host, user=db_user, password=db_pass, port=int(db_port))
                if success:
                    config.DB_HOST = db_host
                    config.DB_PORT = int(db_port)
                    config.DB_USER = db_user
                    config.DB_PASSWORD = db_pass
                    # Save to .env for persistence
                    try:
                        import os
                        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
                        with open(env_file, "w", encoding="utf-8") as f:
                            f.write(f"DB_HOST={db_host}\nDB_PORT={int(db_port)}\nDB_USER={db_user}\nDB_PASSWORD={db_pass}\nDB_NAME=blood_donation_db\n")
                    except Exception:
                        pass
                    st.success("Database successfully initialized and seeded!")
                    st.rerun()
                else:
                    st.error(f"Connection Failed: {msg}")

    menu_selection = st.selectbox(
        "Navigate to",
        [
            "📊 Dashboard",
            "👥 Donor Management",
            "🩸 Blood Requests",
            "🏥 Blood Availability",
            "🌐 Hospital Network",
            "🔍 Search & Sort Donors",
            "🧠 Donor Matching & Blood Allocation",
        ],
        key="app_navigation",
    )


# ==============================================================================
# HELPER: FALLBACK DATA LOADER
# ==============================================================================
def get_donors_safe():
    """Fetches donors from MySQL, falls back to sample list if DB offline."""
    if is_conn_ok:
        return get_all_donors()
    return [
        {"donor_id": 1, "name": "Aarav Sharma", "age": 26, "gender": "Male", "blood_group": "O+", "phone": "9876543210", "email": "aarav@example.com", "city": "Mumbai", "available": 1, "last_donation_date": "2024-01-15"},
        {"donor_id": 2, "name": "Priya Patel", "age": 24, "gender": "Female", "blood_group": "A+", "phone": "9876543211", "email": "priya@example.com", "city": "Pune", "available": 1, "last_donation_date": "2024-02-10"},
        {"donor_id": 3, "name": "Rohan Mehta", "age": 31, "gender": "Male", "blood_group": "B+", "phone": "9876543212", "email": "rohan@example.com", "city": "Mumbai", "available": 1, "last_donation_date": "2023-11-20"},
        {"donor_id": 4, "name": "Ananya Deshmukh", "age": 22, "gender": "Female", "blood_group": "O-", "phone": "9876543213", "email": "ananya@example.com", "city": "Thane", "available": 1, "last_donation_date": "2024-03-01"},
        {"donor_id": 5, "name": "Vikram Joshi", "age": 35, "gender": "Male", "blood_group": "AB+", "phone": "9876543214", "email": "vikram@example.com", "city": "Pune", "available": 0, "last_donation_date": "2024-04-05"},
        {"donor_id": 6, "name": "Neha Kulkarni", "age": 29, "gender": "Female", "blood_group": "A-", "phone": "9876543215", "email": "neha@example.com", "city": "Navi Mumbai", "available": 1, "last_donation_date": "2023-12-18"}
    ]

def get_requests_safe():
    """Fetches blood requests safely."""
    if is_conn_ok:
        return get_all_requests()
    return [
        {"request_id": 1, "hospital_id": 1, "hospital_name": "City General Hospital", "hospital_city": "Mumbai", "blood_group": "O-", "units": 3, "urgency": "Critical", "status": "Pending", "requested_at": "2024-05-01 10:00:00"},
        {"request_id": 2, "hospital_id": 2, "hospital_name": "Apex Trauma & Surgical Care", "hospital_city": "Pune", "blood_group": "A+", "units": 4, "urgency": "Urgent", "status": "Pending", "requested_at": "2024-05-01 10:30:00"},
        {"request_id": 3, "hospital_id": 3, "hospital_name": "Metropolitan Blood Center", "hospital_city": "Mumbai", "blood_group": "B+", "units": 2, "urgency": "Normal", "status": "Pending", "requested_at": "2024-05-01 11:00:00"},
        {"request_id": 4, "hospital_id": 1, "hospital_name": "City General Hospital", "hospital_city": "Mumbai", "blood_group": "AB+", "units": 2, "urgency": "Urgent", "status": "Processing", "requested_at": "2024-05-01 11:15:00"},
        {"request_id": 5, "hospital_id": 4, "hospital_name": "LifeLine Specialty Hospital", "hospital_city": "Navi Mumbai", "blood_group": "O+", "units": 5, "urgency": "Critical", "status": "Completed", "requested_at": "2024-05-01 08:00:00"}
    ]

def get_inventory_safe():
    """Fetches inventory safely."""
    if is_conn_ok:
        rows = db.fetch_all("SELECT blood_group, units FROM blood_inventory ORDER BY blood_group ASC")
        return {r["blood_group"]: r["units"] for r in rows}
    return {"A+": 14, "A-": 6, "B+": 18, "B-": 5, "AB+": 9, "AB-": 3, "O+": 22, "O-": 8}


# ==============================================================================
# PAGE 1: 📊 DASHBOARD
# ==============================================================================
if menu_selection == "📊 Dashboard":
    render_app_header("Dashboard", "Blood stock, donor availability, and hospital requests")

    donors = get_donors_safe()
    requests = get_requests_safe()
    inventory = get_inventory_safe()

    total_donors = len(donors)
    available_donors = sum(1 for d in donors if d.get("available"))
    total_hospitals = 6 if not is_conn_ok else len(db.fetch_all("SELECT hospital_id FROM hospitals"))
    pending_requests = sum(1 for r in requests if r.get("status") == "Pending")
    total_units = sum(inventory.values())

    # Top KPI Metrics Row (Pure HTML Cards for 100% bug-free rendering)
    c1, c2, c3, c4, c5 = st.columns(5)
    kpis = [
        ("Total Donors", str(total_donors), "👥 In Registry", "#991b1b"),
        ("Available Donors", str(available_donors), f"{(available_donors/max(1,total_donors)*100):.0f}% active", "#15803d"),
        ("Partner Hospitals", str(total_hospitals), "🏥 Active Hubs", "#0284c7"),
        ("Pending Requests", str(pending_requests), "⏳ Awaiting action", "#b45309"),
        ("Total Blood Stock", f"{total_units} Units", "🩸 8 Blood Groups", "#dc2626")
    ]
    for idx, (label, val, subtitle, col_color) in enumerate(kpis):
        with [c1, c2, c3, c4, c5][idx]:
            st.markdown(f"""
            <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 10px; text-align: center; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">{label}</div>
                <div style="font-size: 1.65rem; font-weight: 800; color: {col_color}; margin: 3px 0;">{val}</div>
                <div style="font-size: 0.72rem; font-weight: 600; color: #475569;">{subtitle}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Blood Inventory Stock Cards
    st.subheader("🩸 Real-time Blood Inventory by Blood Group")
    inv_cols = st.columns(8)
    for idx, bg in enumerate(config.BLOOD_GROUPS):
        units = inventory.get(bg, 0)
        pct = min(100, int((units / 25.0) * 100))
        with inv_cols[idx]:
            status_color = "#15803d" if units >= 10 else ("#b45309" if units >= 5 else "#b91c1c")
            badge_text = "Adequate" if units >= 10 else ("Moderate" if units >= 5 else "CRITICAL")
            st.markdown(f"""
            <div style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 6px; text-align: center; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-size: 1.35rem; font-weight: 800; color: #b91c1c;">{bg}</div>
                <div style="font-size: 1.45rem; font-weight: 700; color: #1e293b; margin: 2px 0;">{units} <span style="font-size: 0.75rem; font-weight: 500; color: #64748b;">units</span></div>
                <div style="color: {status_color}; font-size: 0.72rem; font-weight: 700; margin-bottom: 6px;">● {badge_text}</div>
                <div style="background: #f1f5f9; border-radius: 4px; height: 5px; width: 100%; overflow: hidden;">
                    <div style="background: {status_color}; height: 100%; width: {pct}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Lower split: pending requests and recent activity
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("⏳ Pending Requests")
        pending_list = [r for r in requests if r.get("status") == "Pending"]
        if pending_list:
            df_pending = pd.DataFrame(pending_list)[["request_id", "hospital_name", "blood_group", "units", "urgency"]]
            df_pending.columns = ["Req ID", "Hospital", "Group", "Units", "Urgency"]
            render_clean_table(df_pending)
            st.info(f"**Next request:** #{pending_list[0]['request_id']} for {pending_list[0]['hospital_name']} ({pending_list[0]['blood_group']})")
        else:
            st.success("All blood requests have been fulfilled! No pending requests.")

    with col_right:
        st.subheader("🕒 Recent Activity")
        stack_items = get_operation_stack().to_list()
        if stack_items:
            for item in stack_items[:5]:
                st.markdown(f"• **`{item.get('timestamp', '')}`** — {item.get('details', '')}")
            if st.button("↩️ Undo Recent Change", key="dash_undo"):
                ok, undo_msg = undo_last_operation()
                if ok:
                    st.success(undo_msg)
                    st.rerun()
                else:
                    st.warning(undo_msg)
        else:
            st.caption("Recent changes will appear here.")

    render_app_footer()


# ==============================================================================
# PAGE 2: 👥 DONOR MANAGEMENT
# ==============================================================================
elif menu_selection == "👥 Donor Management":
    render_app_header("Donor Management", "Register, find, and update donor records")
    show_flash_message("donor_registration_notice")
    show_flash_message("donor_management_notice")

    ll = load_donors_to_linked_list() if is_conn_ok else DonorLinkedList()
    if not is_conn_ok:
        for d in get_donors_safe():
            ll.insert_at_end(d)

    tab1, tab2, tab3 = st.tabs(["➕ Register New Donor", "📋 View & Filter Donors", "✏️ Update / Delete Donor"])

    # TAB 1: REGISTER DONOR
    with tab1:
        st.subheader("Register a New Blood Donor")
        with st.form("donor_registration_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name*", placeholder="e.g. Rahul Sharma")
                age = st.number_input("Age (Years)*", min_value=18, max_value=65, value=25)
                gender = st.selectbox("Gender*", config.GENDERS)
                blood_group = st.selectbox("Blood Group*", config.BLOOD_GROUPS)
                city = st.text_input("City*", placeholder="e.g. Mumbai")
            with col2:
                phone = st.text_input("Phone Number (10 digits)*", placeholder="e.g. 9876543210")
                email = st.text_input("Email Address*", placeholder="e.g. rahul@example.com")
                last_donation = st.date_input("Last Donation Date (Optional)", value=date(2024, 1, 1))
                available = st.checkbox("Currently Available to Donate", value=True)

            submitted = st.form_submit_button("Register Donor", type="primary")

            if submitted:
                if not is_conn_ok:
                    set_flash_message(
                        "donor_registration_notice",
                        "error",
                        "Could not register the donor. Please set up the database and try again.",
                    )
                else:
                    success, msg, new_id = register_donor(
                        name=name, age=age, gender=gender, blood_group=blood_group,
                        phone=phone, email=email, city=city, available=available,
                        last_donation_date=last_donation
                    )
                    if success:
                        # Record on stack
                        get_operation_stack().push({
                            "action": "REGISTER_DONOR",
                            "donor_id": new_id,
                            "details": f"Registered new donor #{new_id} ({name}, {blood_group})",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        set_flash_message("donor_registration_notice", "success", msg)
                    else:
                        set_flash_message("donor_registration_notice", "error", msg)

    # TAB 2: VIEW & FILTER DONORS
    with tab2:
        st.subheader("Registered Donors")
        fcol1, fcol2 = st.columns([1, 1])
        filter_avail = fcol1.selectbox("Filter Availability", ["All Donors", "Available Only (✓)", "Unavailable (✗)"])
        filter_bg = fcol2.selectbox("Filter Blood Group", ["All Blood Groups"] + config.BLOOD_GROUPS)

        donors_list = ll.to_list()
        
        # Apply Linked List filtering
        filtered = donors_list
        if filter_avail == "Available Only (✓)":
            filtered = [d for d in filtered if d.get("available")]
        elif filter_avail == "Unavailable (✗)":
            filtered = [d for d in filtered if not d.get("available")]

        if filter_bg != "All Blood Groups":
            filtered = [d for d in filtered if d.get("blood_group") == filter_bg]

        st.write(f"Showing **{len(filtered)}** of **{len(donors_list)}** total donors.")
        if filtered:
            df = pd.DataFrame(filtered)
            display_cols = ["donor_id", "name", "blood_group", "age", "gender", "city", "phone", "email", "available", "last_donation_date"]
            df_display = df[[c for c in display_cols if c in df.columns]]
            df_display["available"] = df_display["available"].apply(lambda x: "✓ Available" if x else "✗ Inactive")
            render_clean_table(df_display)
        else:
            st.info("No donors match the selected filters.")

        # Check donor availability and display details
        st.markdown("---")
        st.subheader("🔍 Search Donor Details")
        st.caption("Select a donor to check availability and view their details.")
        if donors_list:
            insp_options = {f"#{d['donor_id']} - {d['name']} ({d['blood_group']})": d['donor_id'] for d in donors_list}
            sel_insp_label = st.selectbox("Select Donor to Inspect Details", list(insp_options.keys()), key="insp_donor_sel")
            sel_insp_id = insp_options[sel_insp_label]
            found_node, steps_taken = ll.find_by_id(sel_insp_id)

            if found_node:
                f_dict = found_node.to_dict()
                st.info(f"Donor found after checking {steps_taken} record(s).")
                
                det_c1, det_c2, det_c3 = st.columns([2, 2, 1.2])
                with det_c1:
                    st.markdown(f"""
                    **Full Name:** {f_dict['name']}  
                    **Donor ID:** #{f_dict['donor_id']}  
                    **Age / Gender:** {f_dict['age']} yrs / {f_dict['gender']}  
                    **Blood Group:** `{f_dict['blood_group']}`  
                    """)
                with det_c2:
                    st.markdown(f"""
                    **Phone:** {f_dict['phone']}  
                    **Email:** {f_dict['email']}  
                    **City:** {f_dict['city']}  
                    **Last Donation:** {f_dict['last_donation_date'] or 'None recorded'}  
                    """)
                with det_c3:
                    is_avail = bool(f_dict['available'])
                    status_badge = "🟢 Available" if is_avail else "🔴 Inactive"
                    st.markdown(f"**Availability:**<br><h4>{status_badge}</h4>", unsafe_allow_html=True)
                    toggle_label = "Mark Inactive" if is_avail else "Mark Available"
                    if st.button(f"🔄 {toggle_label}", key=f"toggle_btn_{sel_insp_id}"):
                        if is_conn_ok:
                            ok_tog, msg_tog = toggle_availability(sel_insp_id, not is_avail)
                            if ok_tog:
                                st.success(msg_tog)
                                st.rerun()
                            else:
                                st.error(msg_tog)
                        else:
                            st.warning("Set up the database from the sidebar to save this change.")

    # TAB 3: UPDATE / DELETE DONOR
    with tab3:
        st.subheader("Modify or Delete Donor Record")
        all_d = ll.to_list()
        if not all_d:
            st.info("No donor records available.")
        else:
            donor_options = {f"#{d['donor_id']} - {d['name']} ({d['blood_group']})": d['donor_id'] for d in all_d}
            selected_label = st.selectbox("Select Donor to Edit/Delete", list(donor_options.keys()))
            selected_id = donor_options[selected_label]
            target_donor, _ = ll.find_by_id(selected_id)

            if target_donor:
                td = target_donor.to_dict()
                u_col1, u_col2 = st.columns(2)
                with u_col1:
                    u_name = st.text_input("Name", value=td["name"], key="u_name")
                    u_age = st.number_input("Age", min_value=18, max_value=65, value=int(td["age"]), key="u_age")
                    u_gender = st.selectbox("Gender", config.GENDERS, index=config.GENDERS.index(td["gender"]) if td["gender"] in config.GENDERS else 0, key="u_gen")
                    u_bg = st.selectbox("Blood Group", config.BLOOD_GROUPS, index=config.BLOOD_GROUPS.index(td["blood_group"]) if td["blood_group"] in config.BLOOD_GROUPS else 0, key="u_bg")
                    u_city = st.text_input("City", value=td["city"], key="u_city")
                with u_col2:
                    u_phone = st.text_input("Phone", value=td["phone"], key="u_phone")
                    u_email = st.text_input("Email", value=td["email"], key="u_email")
                    u_avail = st.checkbox("Available", value=bool(td["available"]), key="u_avail")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("💾 Save Changes", type="primary", use_container_width=True):
                            if not is_conn_ok:
                                st.error("Could not save the changes. Set up the database from the sidebar and try again.")
                            else:
                                ok, msg = update_donor(
                                    donor_id=selected_id, name=u_name, age=u_age, gender=u_gender,
                                    blood_group=u_bg, phone=u_phone, email=u_email, city=u_city,
                                    available=u_avail
                                )
                                if ok:
                                    set_flash_message("donor_management_notice", "success", f"Donor changes saved successfully. {msg}")
                                else:
                                    st.error(msg)
                    with btn_col2:
                        if st.button("🗑️ Delete Donor", type="secondary", use_container_width=True):
                            if not is_conn_ok:
                                st.error("Could not delete this donor. Set up the database from the sidebar and try again.")
                            else:
                                ok, msg = delete_donor(selected_id)
                                if ok:
                                    get_operation_stack().push({
                                        "action": "DELETE_DONOR",
                                        "donor_id": selected_id,
                                        "details": f"Deleted donor #{selected_id} ({td['name']})",
                                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    })
                                    set_flash_message("donor_management_notice", "success", f"Donor deleted successfully. {msg}")
                                else:
                                    st.error(msg)

    render_app_footer()


# ==============================================================================
# PAGE 3: 🩸 BLOOD REQUESTS
# ==============================================================================
elif menu_selection == "🩸 Blood Requests":
    render_app_header("Blood Requests", "Create, process, and update hospital requests")
    show_flash_message("blood_request_notice")

    tab_req1, tab_req2, tab_req3, tab_req4, tab_req5 = st.tabs([
        "➕ Create Blood Request",
        "⏳ Process Requests",
        "📋 View Requests & Update Status",
        "🚨 Urgent & Critical Requests",
        "🕒 Recent Changes"
    ])

    # TAB 1: CREATE BLOOD REQUEST
    with tab_req1:
        st.subheader("Create a New Hospital Blood Request")
        hospitals = get_all_hospitals() if is_conn_ok else [
            {"hospital_id": 1, "hospital_name": "City General Hospital", "city": "Mumbai"},
            {"hospital_id": 2, "hospital_name": "Apex Trauma & Surgical Care", "city": "Pune"},
            {"hospital_id": 3, "hospital_name": "Metropolitan Blood Center", "city": "Mumbai"}
        ]
        hosp_map = {f"{h['hospital_name']} ({h['city']})": h["hospital_id"] for h in hospitals}

        if not hosp_map:
            st.warning("No hospitals are available for this request. Add a hospital and try again.")
        else:
            with st.form("create_request_form", clear_on_submit=True):
                r_col1, r_col2 = st.columns(2)
                with r_col1:
                    selected_hosp_label = st.selectbox("Requesting Hospital*", list(hosp_map.keys()))
                    req_bg = st.selectbox("Blood Group Required*", config.BLOOD_GROUPS)
                with r_col2:
                    req_units = st.number_input("Units Required*", min_value=1, max_value=20, value=2)
                    req_urgency = st.selectbox("Urgency Level*", config.URGENCY_LEVELS)

                req_submit = st.form_submit_button("Submit Blood Request", type="primary")

                if req_submit:
                    if not is_conn_ok:
                        set_flash_message(
                            "blood_request_notice",
                            "error",
                            "Request submission failed. Connect to the database and try again.",
                        )
                    else:
                        hosp_id = hosp_map[selected_hosp_label]
                        ok, msg, new_req_id = create_blood_request(hosp_id, req_bg, req_units, req_urgency)
                        if ok:
                            set_flash_message(
                                "blood_request_notice",
                                "success",
                                f"Request submitted successfully! Request #{new_req_id} has been added to pending requests.",
                            )
                        else:
                            set_flash_message(
                                "blood_request_notice",
                                "error",
                                f"Request submission failed: {msg}",
                            )

    # TAB 2: PROCESS REQUESTS
    with tab_req2:
        st.subheader("Pending Blood Requests")
        queue = get_pending_request_queue() if is_conn_ok else BloodRequestQueue()
        if not is_conn_ok:
            for r in [x for x in get_requests_safe() if x.get("status") == "Pending"]:
                queue.enqueue(r)

        q_size = queue.size()
        st.write(f"Requests waiting to be processed: **{q_size}**")

        if not queue.is_empty():
            front_item = queue.peek()
            st.info(
                f"**🎯 Next request:** "
                f"Request #{front_item['request_id']} | **{front_item['hospital_name']}** | "
                f"**{front_item['units']} units** of **{front_item['blood_group']}** | Urgency: **{front_item['urgency']}**"
            )

            col_proc, _ = st.columns([2, 3])
            if col_proc.button("⚡ Process Next Request", type="primary"):
                if not is_conn_ok:
                    st.error("Could not process this request. Set up the database from the sidebar and try again.")
                else:
                    ok, proc_msg, _ = process_next_pending_request()
                    if ok:
                        st.success(proc_msg)
                    else:
                        st.warning(proc_msg)
                    st.rerun()

            st.markdown("##### Requests in Arrival Order:")
            q_items = queue.to_list()
            df_q = pd.DataFrame(q_items)[["request_id", "hospital_name", "blood_group", "units", "urgency", "status", "requested_at"]]
            df_q.columns = ["Req ID", "Hospital", "Blood Group", "Units", "Urgency", "Status", "Arrival Time"]
            render_clean_table(df_q)
        else:
            st.success("🎉 No requests are waiting to be processed.")

    # TAB 3: VIEW REQUESTS & UPDATE STATUS
    with tab_req3:
        st.subheader("📋 Hospital Blood Requests Directory & Status Updates")
        st.caption("View all hospital blood requests, filter by lifecycle status, and update statuses.")
        
        all_requests = get_requests_safe()
        
        # Filters
        rf_col1, rf_col2 = st.columns(2)
        stat_filter = rf_col1.selectbox("Filter by Status", ["All Statuses"] + config.REQUEST_STATUSES)
        urg_filter = rf_col2.selectbox("Filter by Urgency", ["All Urgencies"] + config.URGENCY_LEVELS)
        
        filtered_reqs = all_requests
        if stat_filter != "All Statuses":
            filtered_reqs = [r for r in filtered_reqs if r.get("status") == stat_filter]
        if urg_filter != "All Urgencies":
            filtered_reqs = [r for r in filtered_reqs if r.get("urgency") == urg_filter]
            
        st.write(f"Showing **{len(filtered_reqs)}** of **{len(all_requests)}** total blood requests.")
        if filtered_reqs:
            df_all_r = pd.DataFrame(filtered_reqs)[["request_id", "hospital_name", "blood_group", "units", "urgency", "status", "requested_at"]]
            df_all_r.columns = ["Req ID", "Hospital", "Blood Group", "Units", "Urgency", "Status", "Requested At"]
            render_clean_table(df_all_r)
        else:
            st.info("No blood requests match the selected filters.")
            
        st.markdown("---")
        st.subheader("✏️ Update Blood Request Status")
        if all_requests:
            req_opts = {f"Req #{r['request_id']} - {r['hospital_name']} ({r['units']}u of {r['blood_group']}, Current: {r['status']})": r['request_id'] for r in all_requests}
            selected_req_label = st.selectbox("Select Blood Request to Update", list(req_opts.keys()))
            selected_req_id = req_opts[selected_req_label]
            
            # Find current request status
            curr_target = next((r for r in all_requests if r["request_id"] == selected_req_id), None)
            curr_status = curr_target.get("status", "Pending") if curr_target else "Pending"
            
            u_stat_col1, u_stat_col2 = st.columns([2, 1])
            new_status = u_stat_col1.selectbox(
                "Select New Status",
                config.REQUEST_STATUSES,
                index=config.REQUEST_STATUSES.index(curr_status) if curr_status in config.REQUEST_STATUSES else 0
            )
            
            if u_stat_col2.button("💾 Update Status", type="primary", key="btn_update_req_stat"):
                if not is_conn_ok:
                    st.error("Could not update the request. Set up the database from the sidebar and try again.")
                else:
                    ok_u, msg_u = update_request_status(selected_req_id, new_status)
                    if ok_u:
                        st.success(msg_u)
                        st.rerun()
                    else:
                        st.error(msg_u)

    # TAB 4: URGENT & CRITICAL
    with tab_req4:
        st.subheader("🚨 Priority Emergency Triage")
        all_reqs = get_requests_safe()
        critical_urgent = [r for r in all_reqs if r.get("urgency") in ["Critical", "Urgent"] and r.get("status") in ["Pending", "Processing"]]
        
        if critical_urgent:
            st.error(f"Attention: {len(critical_urgent)} Critical or Urgent blood request(s) need immediate attention!")
            df_urg = pd.DataFrame(critical_urgent)[["request_id", "hospital_name", "blood_group", "units", "urgency", "status", "requested_at"]]
            render_clean_table(df_urg)
        else:
            st.success("No active critical or urgent blood requests at this time.")

    # TAB 5: RECENT CHANGES
    with tab_req5:
        st.subheader("🕒 Recent Changes")
        st.caption("Review recent updates or undo the latest change.")
        
        stack = get_operation_stack()
        stack_list = stack.to_list()

        col_undo, _ = st.columns([2, 3])
        if col_undo.button("↩️ Undo Latest Change", type="primary"):
            ok, undo_msg = undo_last_operation()
            if ok:
                st.success(undo_msg)
                st.rerun()
            else:
                st.warning(undo_msg)

        if stack_list:
            st.markdown("##### Change History:")
            for op in stack_list:
                st.markdown(f"**`{op.get('timestamp')}`** — {op.get('details')}")
        else:
            st.info("No recent changes.")

    render_app_footer()


# ==============================================================================
# PAGE 4: 🏥 BLOOD AVAILABILITY & INVENTORY
# ==============================================================================
elif menu_selection == "🏥 Blood Availability":
    render_app_header("Blood Availability", "Review and update blood stock")

    inv = get_inventory_safe()

    # Cards layout
    st.subheader("Available Stock Across All Blood Groups")
    cols = st.columns(4)
    for i, bg in enumerate(config.BLOOD_GROUPS):
        units = inv.get(bg, 0)
        pct = min(100, int((units / 25.0) * 100))
        c = cols[i % 4]
        with c:
            color = "#15803d" if units >= 10 else ("#b45309" if units >= 5 else "#dc2626")
            status = "Sufficient" if units >= 10 else ("Low Reserve" if units >= 5 else "CRITICAL DEFICIT")
            st.markdown(f"""
            <div style="border: 2px solid {color}; border-radius: 12px; padding: 16px; margin-bottom: 12px; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-size: 1.8rem; font-weight: 800; color: #991b1b;">{bg}</div>
                <div style="font-size: 2rem; font-weight: 700; color: #0f172a;">{units} <span style="font-size: 0.9rem; font-weight: 400; color: #64748b;">units</span></div>
                <div style="color: {color}; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">● {status}</div>
                <div style="background: #f1f5f9; border-radius: 4px; height: 6px; width: 100%; margin-top: 8px; overflow: hidden;">
                    <div style="background: {color}; height: 100%; width: {pct}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Update Inventory Units
    st.subheader("Update Blood Inventory Stock")
    with st.form("update_inventory_form"):
        col1, col2, col3 = st.columns(3)
        sel_bg = col1.selectbox("Blood Group", config.BLOOD_GROUPS)
        action_type = col2.radio("Action", ["Add Units", "Set Exact Total Units"])
        unit_amount = col3.number_input("Units", min_value=1, max_value=50, value=5)
        
        inv_submit = st.form_submit_button("Update Stock", type="primary")
        if inv_submit:
            if not is_conn_ok:
                st.error("Could not update blood stock. Set up the database from the sidebar and try again.")
            else:
                curr_units = inv.get(sel_bg, 0)
                new_units = (curr_units + unit_amount) if action_type == "Add Units" else unit_amount
                db.execute_query("UPDATE blood_inventory SET units = %s WHERE blood_group = %s", (new_units, sel_bg))
                
                get_operation_stack().push({
                    "action": "UPDATE_INVENTORY",
                    "blood_group": sel_bg,
                    "details": f"Updated inventory for {sel_bg} from {curr_units} to {new_units} units.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success(f"Inventory for {sel_bg} updated to {new_units} units successfully!")
                st.rerun()

    render_app_footer()


# ==============================================================================
# PAGE 5: 🌐 HOSPITAL NETWORK
# ==============================================================================
elif menu_selection == "🌐 Hospital Network":
    render_app_header("Hospital Network", "Find hospitals by name or city")

    hospitals = get_all_hospitals() if is_conn_ok else [
        {"hospital_id": 1, "hospital_name": "City General Hospital", "city": "Mumbai", "phone": "022-24101000"},
        {"hospital_id": 2, "hospital_name": "Apex Trauma & Surgical Care", "city": "Pune", "phone": "020-25678900"},
        {"hospital_id": 3, "hospital_name": "Metropolitan Blood Center", "city": "Mumbai", "phone": "022-26543210"},
        {"hospital_id": 4, "hospital_name": "LifeLine Specialty Hospital", "city": "Navi Mumbai", "phone": "022-27894561"},
        {"hospital_id": 5, "hospital_name": "Global Heart & Kidney Institute", "city": "Thane", "phone": "022-25348970"},
        {"hospital_id": 6, "hospital_name": "St. Jude Children & Community Hospital", "city": "Pune", "phone": "020-26123456"},
    ]

    if hospitals:
        search_hospital = st.text_input("Search by hospital name or city")
        query = search_hospital.strip().casefold()
        matching_hospitals = [
            hospital for hospital in hospitals
            if query in hospital["hospital_name"].casefold()
            or query in hospital["city"].casefold()
        ]
        if matching_hospitals:
            hospital_table = pd.DataFrame(matching_hospitals)[
                ["hospital_name", "city", "phone"]
            ]
            hospital_table.columns = ["Hospital", "City", "Phone"]
            render_clean_table(hospital_table)
        else:
            st.info("No hospitals match your search.")
    else:
        st.info("No hospital records are available.")

    render_app_footer()


# ==============================================================================
# PAGE 6: 🔍 SEARCH & SORT DONORS
# ==============================================================================
elif menu_selection == "🔍 Search & Sort Donors":
    render_app_header("Search & Sort Donors", "Find donor records or arrange them by name, city, or blood group")

    donors = get_donors_safe()

    tab_s1, tab_s2, tab_s3 = st.tabs([
        "🔎 Search by Details",
        "⚡ Search by Donor ID",
        "📶 Sort Donors"
    ])

    # TAB 1: SEARCH BY DETAILS
    with tab_s1:
        st.subheader("Search by Donor Details")
        col_ls1, col_ls2, col_ls3 = st.columns([2, 2, 1])
        search_fields = {
            "Blood Group": "blood_group",
            "City": "city",
            "Gender": "gender",
            "Name": "name",
        }
        search_field_label = col_ls1.selectbox("Search by", list(search_fields))
        search_field = search_fields[search_field_label]
        if search_field == "blood_group":
            target_val = col_ls2.selectbox(
                "Blood Group to Find", config.BLOOD_GROUPS
            )
        elif search_field == "gender":
            target_val = col_ls2.selectbox("Gender to Find", config.GENDERS)
        else:
            target_val = col_ls2.text_input("Enter a name or city")
        
        if col_ls3.button("Search Donors", type="primary"):
            matches, _, _ = linear_search(donors, search_field, target_val)
            st.success(f"Found **{len(matches)}** matching donor record(s).")
            if matches:
                st.markdown("##### Matching Donors:")
                render_clean_table(pd.DataFrame(matches)[["donor_id", "name", "blood_group", "city", "phone"]])
            else:
                st.warning("No records matched the search criteria.")

    # TAB 2: SEARCH BY DONOR ID
    with tab_s2:
        st.subheader("Find a Donor by ID")
        st.info("Enter a donor ID to view the matching record.")
        
        # Sort donors by donor_id first using manual insertion sort
        sorted_by_id, _, _ = insertion_sort(donors, sort_field="donor_id", ascending=True)
        
        col_bs1, col_bs2 = st.columns([3, 1])
        target_id_search = col_bs1.number_input("Donor ID to find", min_value=1, max_value=999, value=3)
        
        if col_bs2.button("Find Donor", type="primary"):
            found, _, _ = binary_search(sorted_by_id, target_id_search)
            if found:
                st.success(f"Donor ID #{target_id_search} found.")
                donor_details = pd.DataFrame([{
                    "Donor ID": found.get("donor_id"),
                    "Name": found.get("name"),
                    "Blood Group": found.get("blood_group"),
                    "City": found.get("city"),
                    "Phone": found.get("phone"),
                    "Available": "Yes" if found.get("available") else "No",
                }])
                render_clean_table(donor_details)
            else:
                st.error(f"Donor ID #{target_id_search} was not found.")


    # TAB 3: SORT DONORS
    with tab_s3:
        st.subheader("Sort Donor Records")
        col_sort1, col_sort2, col_sort3 = st.columns([2, 2, 1])
        sort_fields = {
            "Name": "name",
            "Blood Group": "blood_group",
            "City": "city",
            "Donor ID": "donor_id",
        }
        sort_by_label = col_sort1.selectbox("Sort by", list(sort_fields))
        sort_by = sort_fields[sort_by_label]
        order_asc = col_sort2.radio("Order", ["Ascending", "Descending"], horizontal=True) == "Ascending"

        if col_sort3.button("Sort Donors", type="primary"):
            sorted_res, _, _ = insertion_sort(donors, sort_field=sort_by, ascending=order_asc)
            
            st.success(f"Donor records sorted by {sort_by_label.lower()}.")
            
            c_orig, c_sort = st.columns(2)
            with c_orig:
                st.markdown("##### Original List:")
                render_clean_table(pd.DataFrame(donors)[["donor_id", "name", "blood_group", "city"]])
            with c_sort:
                st.markdown(f"##### Sorted by {sort_by_label} ({'Ascending' if order_asc else 'Descending'}):")
                render_clean_table(pd.DataFrame(sorted_res)[["donor_id", "name", "blood_group", "city"]])


    render_app_footer()


# ==============================================================================
# PAGE 7: 🧠 DONOR MATCHING & BLOOD ALLOCATION
# ==============================================================================
elif menu_selection == "🧠 Donor Matching & Blood Allocation":
    render_app_header("Donor Matching & Blood Allocation", "Find eligible, compatible donors")

    donors = get_donors_safe()

    st.subheader("Find Suitable Donors")

    col_g1, col_g2, col_g3 = st.columns(3)
    recip_bg = col_g1.selectbox("Patient / Recipient Blood Group", config.BLOOD_GROUPS, index=0)
    units_req = col_g2.number_input("Donors Needed", min_value=1, max_value=10, value=2)

    if col_g3.button("Find Donors", type="primary"):
        selected, metrics, _ = greedy_donor_matching(donors, recip_bg, units_needed=units_req)
        if metrics["fulfilled"]:
            st.success(f"Found {metrics['selected_count']} of {units_req} requested donors.")
        else:
            st.warning(f"Partial fulfillment: Found {metrics['selected_count']} eligible donors (shortage of {units_req - metrics['selected_count']}).")

        if selected:
            st.markdown("##### Suggested Donors:")
            df_sel = pd.DataFrame(selected)[["donor_id", "name", "blood_group", "greedy_score", "days_since_donation", "city", "phone"]]
            df_sel.columns = ["Donor ID", "Name", "Blood Group", "Match Score", "Days Since Last Donation", "City", "Phone"]
            render_clean_table(df_sel)
        else:
            st.info("No available donors match this recipient's blood group.")


    render_app_footer()
