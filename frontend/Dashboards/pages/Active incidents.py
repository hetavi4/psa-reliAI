import streamlit as st

st.set_page_config(page_title="Incident Dashboard", layout="wide")

# ---- Inject Sidebar Styling ----
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

/* Ticket List Styling */
.ticket-card {
    background: white;
    border-radius: 10px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    padding: 15px 20px;
    margin-bottom: 10px;
    border: 2px solid transparent;
}
.ticket-card.selected {
    border: 2px solid #FF9B55;
}

.ticket-status {
    font-size: 12px;
    padding: 3px 8px;
    border-radius: 8px;
    color: white;
    font-weight: 600;
}
.status-accepted { background-color: #00c853; }
.status-escalated { background-color: #d50000; }

.accept-button {
    background-color: #00acc1;
    border: none;
    border-radius: 20px;
    color: white;
    padding: 6px 14px;
    cursor: pointer;
    font-size: 13px;
}
.accept-button:hover { background-color: #00838f; }
</style>
""", unsafe_allow_html=True)

# ---- KPI Section ----
st.markdown("### System Overview")
col1, col2, col3 = st.columns(3)
for c, val, label in zip([col1, col2, col3], [18, 4, 13], ["Active Tickets", "Escalated", "Resolved"]):
    with c:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{val}</div><div class="kpi-label">{label}</div></div>', unsafe_allow_html=True)

st.divider()

# ---- Data ----
tickets = [
    {"id": "TCK-006", "status": "Accepted", "desc": "Vessel AIS transponder not broadcasting position data", "reporter": "Alice Brown", "date": "2025-10-18"},
    {"id": "TCK-007", "status": "Escalated", "desc": "Port crane management system showing incorrect load weights", "reporter": "Bob Smith", "date": "2025-10-17"},
    {"id": "TCK-009", "status": "Accepted", "desc": "Weather API integration returning null values", "reporter": "David Lee", "date": "2025-10-17"},
]

if "selected_ticket" not in st.session_state:
    st.session_state.selected_ticket = tickets[0]["id"]

# ---- Layout: Left Tickets / Right Details ----
left, right = st.columns([1, 2.5])

# LEFT
with left:
    st.markdown("### Active Tickets")
    for t in tickets:
        selected = st.session_state.selected_ticket == t["id"]
        card_class = "ticket-card selected" if selected else "ticket-card"
        st.markdown(
            f"""
            <div class="{card_class}">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <b>{t["id"]}</b>
                    <span class="ticket-status {'status-accepted' if t['status']=='Accepted' else 'status-escalated'}">{t["status"]}</span>
                </div>
                <p style="font-size:14px;margin-top:4px;">{t["desc"]}</p>
                <p style="font-size:12px;color:#666;">Reporter: {t["reporter"]} · {t["date"]}</p>
            </div>
            """, unsafe_allow_html=True
        )

# RIGHT
with right:
    st.markdown(f"### Ticket Details — {st.session_state.selected_ticket}")
    tab1, tab2 = st.tabs(["Remedial Steps", "Similar Cases"])

    with tab1:
        st.markdown("#### Overview")
        st.info("Reefer CONTAINER_ID telemetry gap. Temperature feed offline briefly; backfill later within acceptable range.")

        st.markdown("#### Root Cause")
        st.write("Telemetry temporarily disconnected from bridge. No major data loss observed.")

        st.markdown("#### Remedial Steps")
        st.markdown("""
1. Reset telemetry bridge; enable store-and-forward; alert for >5m gaps.  
2. Confirm scope on test entity and check recent deployments.  
3. Apply compliant fix and document changes.  
4. Validate full user flow, capture before/after evidence.  
        """)

        colA, colB = st.columns(2)
        with colA:
            if st.button("✅ Mark as Solved", use_container_width=True):
                st.success("Case marked as solved ✅")
        with colB:
            if st.button("⚠️ Escalate", use_container_width=True):
                st.warning("Case escalated ⚠️")

    with tab2:
        st.markdown("#### Similar Cases")
        st.info("Closest match: Yard telemetry desync (2025-05-14) handled by YC18; same cause pattern.")
