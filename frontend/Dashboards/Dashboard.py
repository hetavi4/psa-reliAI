import streamlit as st
from datetime import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(layout="wide", page_title="Resolver Dashboard")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
/* General page styling */
body {
    font-family: 'Source Sans Pro', sans-serif;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A5C2F, #0CB654);
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
# ---------- SIDEBAR ----------
with st.sidebar:

    st.markdown(
        """
        <div class='sidebar-avatar'>
            <img src='https://via.placeholder.com/100' alt='User Avatar'>
            <h4>John Doe</h4>
        </div>
        """, unsafe_allow_html=True
    )

# ------- MAIN CONTENT -----
st.markdown("### Hi John,")
st.markdown("Welcome back! Here’s your overview 👋")


# KPI ROW
kpi_cols = st.columns(4)
kpi_data = [
    ("New", 12),
    ("Accepted", 5),
    ("Resolved", 24),
    ("Escalated", 3),
]
for i, (label, value) in enumerate(kpi_data):
    with kpi_cols[i]:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-value'>{value}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("### Recent Incidents")

# INCIDENTS DATA
incidents = [
    {"message": "Overlapping container range(s) found", "reporter": "Emily", "date": "13/10/25", "status": "Escalated"},
    {"message": "Discrepancy between the customer portal and TOS", "reporter": "Susan", "date": "10/10/25", "status": "New"},
    {"message": "Translator rejected EDIFACT COARRI", "reporter": "Emily", "date": "10/10/25", "status": "Escalated"},
    {"message": "Reefer CONTAINER_ID telemetry gap", "reporter": "Susan", "date": "8/10/25", "status": "New"},
    {"message": "Auth token rejection for CONTAINER_ID", "reporter": "Susan", "date": "8/10/25", "status": "New"},
]

for incident in incidents:
    status_class = "status-new" if incident["status"] == "New" else "status-escalated"
    st.markdown(f"""
    <div class='incident-card'>
        <div class='incident-row'>
            <button class='accept-button'>Accept</button>
            <div class='incident-info'>
                <strong>{incident["message"]}</strong><br>
                <small>{incident["reporter"]} • {incident["date"]}</small>
            </div>
            <div class='incident-status {status_class}'>{incident["status"]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
