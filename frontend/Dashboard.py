"""
PORTNET® AI Incident Management Dashboard
Main dashboard showing system overview and statistics
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from api_client import get_api_client, check_backend_connection

# ---------- PAGE CONFIG ----------
st.set_page_config(
    layout="wide",
    page_title="PORTNET® AI Incident Manager",
    page_icon="🚢",
    initial_sidebar_state="expanded"
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
    background: linear-gradient(180deg, #0A5C2F, #0CB654);
    color: white;
    padding-top: 2rem;
}

[data-testid="stSidebar"] .block-container {
    color: white;
}

[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: white !important;
}

[data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
    color: white !important;
}

/* KPI Cards */
.kpi-card {
    background: white;
    border-radius: 10px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
    padding: 24px;
    text-align: center;
    border-left: 4px solid #0CB654;
}

.kpi-value {
    font-size: 42px;
    font-weight: bold;
    margin-top: 8px;
    color: #0A5C2F;
}

.kpi-label {
    font-size: 16px;
    color: #555;
    font-weight: 600;
}

/* Alert Cards */
.alert-card {
    background: white;
    border-radius: 10px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    padding: 16px 20px;
    margin-bottom: 12px;
    border-left: 4px solid #ff5252;
}

.alert-card-warning {
    border-left-color: #ffa726;
}

.alert-card-info {
    border-left-color: #42a5f5;
}

/* Status badges */
.status-badge {
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
    display: inline-block;
}

.status-error {
    background-color: #ffebee;
    color: #c62828;
}

.status-parsed {
    background-color: #e8f5e9;
    color: #2e7d32;
}

.status-warning {
    background-color: #fff3e0;
    color: #ef6c00;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
col1, col2 = st.columns([6, 1])
with col1:
    st.title("🚢 PORTNET® AI Incident Manager")
    st.markdown("**Level 2 Operations Dashboard** - Real-time incident monitoring and AI-powered resolution")

with col2:
    st.markdown(f"<div style='text-align: right; padding-top: 20px;'><small>🕐 {datetime.now().strftime('%H:%M:%S')}</small></div>", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### 🎛️ System Status")
    
    # Check backend connection
    backend_connected = check_backend_connection()
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    
    if backend_connected:
        api_client = get_api_client()
        
        # Get dashboard stats
        with st.spinner("Loading stats..."):
            stats = api_client.get_dashboard_stats()
            
            if 'error' not in stats:
                # EDI Errors count
                edi_errors = stats.get('recent_edi_errors', [])
                st.metric("Recent EDI Errors", len(edi_errors))
                
                # Container status summary
                container_summary = stats.get('container_status_summary', {})
                total_containers = sum(container_summary.values())
                st.metric("Total Containers", total_containers)
                
                # Containers in TRANSHIP status
                tranship = container_summary.get('TRANSHIP', 0)
                st.metric("In Transhipment", tranship)
            else:
                st.warning(f"Stats unavailable: {stats['error']}")
    
    st.markdown("---")
    st.markdown("### 👤 Current User")
    st.markdown("**John Doe**")
    st.markdown("Level 2 Duty Officer")
    st.markdown("Shift: 08:00 - 20:00")

# Stop here if backend is not connected
if not backend_connected:
    st.stop()

# ---------- MAIN CONTENT ----------
api_client = get_api_client()

# Fetch dashboard data
with st.spinner("Loading dashboard data..."):
    dashboard_data = api_client.get_dashboard_stats()

if 'error' in dashboard_data:
    st.error(f"Failed to load dashboard: {dashboard_data['error']}")
    st.stop()

# ---------- KPI ROW ----------
st.markdown("### 📈 System Overview")

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

recent_edi_errors = dashboard_data.get('recent_edi_errors', [])
error_count = len([e for e in recent_edi_errors if e.get('status') == 'ERROR'])
parsed_count = len([e for e in recent_edi_errors if e.get('status') == 'PARSED'])

container_summary = dashboard_data.get('container_status_summary', {})
total_containers = sum(container_summary.values())
in_yard = container_summary.get('IN_YARD', 0)
tranship = container_summary.get('TRANSHIP', 0)

with kpi_col1:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>EDI Messages</div>
        <div class='kpi-value'>{len(recent_edi_errors)}</div>
        <div style='font-size: 14px; color: #777;'>Last 24 hours</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>EDI Errors</div>
        <div class='kpi-value' style='color: #d32f2f;'>{error_count}</div>
        <div style='font-size: 14px; color: #777;'>Requires attention</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>Total Containers</div>
        <div class='kpi-value'>{total_containers}</div>
        <div style='font-size: 14px; color: #777;'>Active in system</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>Transhipment</div>
        <div class='kpi-value'>{tranship}</div>
        <div style='font-size: 14px; color: #777;'>In transit</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------- CONTENT COLUMNS ----------
left_col, right_col = st.columns([2, 1])

# ---------- LEFT: RECENT EDI ERRORS ----------
with left_col:
    st.markdown("### 🚨 Recent EDI Errors & Warnings")
    
    if error_count == 0:
        st.success("✅ No recent EDI errors detected")
    else:
        # Show only error messages
        error_messages = [e for e in recent_edi_errors if e.get('status') == 'ERROR']
        
        for idx, error in enumerate(error_messages[:10]):
            container_id = error.get('container_id', 'N/A')
            message_type = error.get('message_type', 'Unknown')
            error_text = error.get('error_text', 'No details')
            sent_at = error.get('sent_at', 'Unknown time')
            sender = error.get('sender', 'Unknown')
            
            status_class = 'status-error'
            
            st.markdown(f"""
            <div class='alert-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <strong>EDI-{idx+1:03d}</strong> | {message_type} | Container ID: {container_id}
                    </div>
                    <span class='status-badge {status_class}'>{error.get('status', 'ERROR')}</span>
                </div>
                <div style='margin-top: 8px; color: #555;'>
                    <strong>Error:</strong> {error_text}
                </div>
                <div style='margin-top: 4px; font-size: 13px; color: #777;'>
                    {sender} • {sent_at}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add analyze button
            if st.button(f"🔍 Analyze EDI-{idx+1:03d}", key=f"analyze_edi_{idx}"):
                # Create a log line from EDI error
                log_line = f"{sent_at} ERROR [EDI-Parser] Failed to parse {message_type} message: {error_text}. container_id: {container_id}"
                st.session_state['log_to_analyze'] = log_line
                st.info(f"Navigate to 'Log Analyzer' page to see full analysis")

# ---------- RIGHT: CONTAINER STATUS SUMMARY ----------
with right_col:
    st.markdown("### 📦 Container Status Summary")
    
    # Create a nice display of container statuses
    status_colors = {
        'TRANSHIP': '#4CAF50',
        'IN_YARD': '#2196F3',
        'ON_VESSEL': '#9C27B0',
        'GATE_OUT': '#FF9800',
        'GATE_IN': '#00BCD4',
        'DISCHARGED': '#795548',
        'LOADED': '#607D8B'
    }
    
    for status, count in sorted(container_summary.items(), key=lambda x: x[1], reverse=True):
        color = status_colors.get(status, '#999')
        percentage = (count / total_containers * 100) if total_containers > 0 else 0
        
        st.markdown(f"""
        <div style='background: white; padding: 12px; border-radius: 8px; margin-bottom: 8px; box-shadow: 0px 2px 4px rgba(0,0,0,0.1);'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-weight: 600;'>{status.replace('_', ' ')}</span>
                <span style='font-size: 20px; font-weight: bold; color: {color};'>{count}</span>
            </div>
            <div style='background: #eee; height: 6px; border-radius: 3px; margin-top: 6px;'>
                <div style='background: {color}; height: 6px; border-radius: 3px; width: {percentage}%;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🎯 Quick Actions")
    
    if st.button("📝 Analyze New Log Line", use_container_width=True):
        st.switch_page("pages/1_Log_Analyzer.py")
    
    if st.button("📊 View All Incidents", use_container_width=True):
        st.switch_page("pages/2_Active_Incidents.py")
    
    if st.button("🔍 Search Database", use_container_width=True):
        st.switch_page("pages/3_Database_Explorer.py")
    
    if st.button("📤 Upload Log File", use_container_width=True):
        st.switch_page("pages/4_Upload_Logs.py")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #777; font-size: 13px;'>
    PORTNET® AI Incident Management System | PSA Singapore | © 2025
</div>
""", unsafe_allow_html=True)

# Auto-refresh option
st.markdown("""
<script>
// Auto-refresh every 60 seconds
setTimeout(function(){
    window.location.reload();
}, 60000);
</script>
""", unsafe_allow_html=True)

