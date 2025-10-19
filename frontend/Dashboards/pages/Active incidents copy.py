import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Resolver Dashboard")
st.title("Resolver Dashboard")

import streamlit as st

st.set_page_config(layout="wide", page_title="Incident Resolver Dashboard")

# Sidebar (Active Tickets)
with st.sidebar:
    st.markdown("### Active Tickets")
    tickets = [
        {"id": "TCK-006", "status": "Accepted", "desc": "Vessel AIS transponder not broadcasting position data", "reporter": "Alice Brown", "date": "2025-10-18"},
        {"id": "TCK-007", "status": "Escalated", "desc": "Port crane management system showing incorrect load weights", "reporter": "Bob Smith", "date": "2025-10-17"},
        {"id": "TCK-009", "status": "Accepted", "desc": "Weather API integration returning null values", "reporter": "David Lee", "date": "2025-10-17"},
        {"id": "TCK-008", "status": "Accepted", "desc": "Container inventory database sync delayed", "reporter": "Carol Witts", "date": "2025-10-18"},
        {"id": "TCK-010", "status": "Escalated", "desc": "Cargo manifest PDF generation failing", "reporter": "Emma Chen", "date": "2025-10-18"},
    ]

    for t in tickets:
        bg_color = "#e8f7ef" if t["status"] == "Accepted" else "#fff3f0"
        border_color = "#57cc99" if t["status"] == "Accepted" else "#ff8b6a"

        with st.container():
            st.markdown(
                f"""
                <div style='background:{bg_color}; border:1px solid {border_color}; border-radius:10px; padding:12px; margin-bottom:10px;'>
                    <b style='color:#333;'>{t["id"]}</b>
                    <span style='float:right; color:{border_color}; font-weight:600;'>{t["status"]}</span>
                    <p style='color:#555; font-size:14px;'>{t["desc"]}</p>
                    <p style='font-size:13px; color:#888;'>Reporter: {t["reporter"]} · {t["date"]}</p>
                    <div style='display:flex; gap:6px;'>
                        <button style='background-color:#57cc99; color:white; border:none; border-radius:6px; padding:4px 10px;'>Mark Resolved</button>
                        <button style='background-color:white; border:1px solid #ff8b6a; color:#ff8b6a; border-radius:6px; padding:4px 10px;'>Escalate</button>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
/* General page styling */
body {
    font-family: 'Source Sans Pro', sans-serif;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #A5E5DF, #257E73);
    color: white;
    padding-top: 2rem;
}

.sidebar-avatar {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 2rem;
}

.sidebar-avatar img {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    background: #ccc;
    margin-bottom: 10px;
}

.sidebar-button {
    display: block;
    width: 100%;
    background-color: transparent;
    color: white;
    border: none;
    padding: 10px 20px;
    text-align: left;
    cursor: pointer;
    font-size: 16px;
}

.sidebar-button:hover {
    background-color: rgba(255,255,255,0.1);
    border-radius: 8px;
}

/* KPI Cards */
.kpi-card {
    background: white;
    border-radius: 10px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
    padding: 20px;
    text-align: center;
}

.kpi-value {
    font-size: 32px;
    font-weight: bold;
    margin-top: 8px;
}

.kpi-label {
    font-size: 16px;
    color: #555;
}

/* Incident Table */
.incident-card {
    background: white;
    border-radius: 10px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    padding: 15px 20px;
    margin-bottom: 10px;
}

.incident-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.incident-info {
    flex-grow: 1;
    margin-left: 10px;
}

.incident-status {
    font-size: 13px;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: bold;
}

.status-new {
    background-color: #00c853;
    color: white;
}

.status-escalated {
    background-color: #d50000;
    color: white;
}

.accept-button {
    background-color: #00acc1;
    border: none;
    border-radius: 20px;
    color: white;
    padding: 6px 14px;
    cursor: pointer;
    font-size: 13px;
}

.accept-button:hover {
    background-color: #00838f;
}
.st-key-accepting button {
    color: white;
    background-image: None;
    border-radius: 10px;
            }
</style>
""", unsafe_allow_html=True)
profile_container = st.container()
# Main area
st.markdown("## Incident Details")

tab1, tab2 = st.tabs(["Remedial Steps", "Similar Cases"])

with tab1:
    st.markdown("### Overview")
    st.info("Reefer CONTAINER_ID telemetry gap. Temperature feed offline briefly; backfill later within acceptable range. Yard block G7, handled by YC22.")

    st.markdown("### Root Cause")
    st.write("Reefer CONTAINER_ID telemetry gap. Temperature feed offline briefly; backfill later within acceptable range. Yard block G7, handled by YC22.")

    st.markdown("### Remedial Steps")
    st.markdown(
        """
        1. Reset telemetry bridge; enabled store-and-forward; alert for >5m gaps; confirmed stability post-recovery; tagged for periodic review.  
        2. Confirm scope and reproduction on a safe test entity.  
        3. Check recent deployments/config toggles around the timestamp.  
        4. Apply compliant fix and document the change.  
            - Capture before/after evidence (screenshots/queries).  
            - Update the case with sanitized details.  
        5. Validate end-to-end user flow.  
            - Capture before/after evidence (screenshots/queries).  
            - Update the case with sanitized details.  
        """
    )

    st.markdown("### Verification")
    st.markdown(
        """
        1. Run the end-to-end journey again; confirm success.  
        2. No new errors for 30 minutes in monitoring.  
        3. Attach evidence and close the case.  
        """
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        st.button("✅ Mark as Solved", use_container_width=True)
    with c2:
        st.button("⚠️ Escalate", use_container_width=True)

with tab2:
    st.write("🧩 Display similar past cases here.")

