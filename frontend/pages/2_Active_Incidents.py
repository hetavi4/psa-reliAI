"""
PORTNET® Active Incidents Monitor
View and manage all active incidents with detailed analysis
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from api_client import get_api_client, check_backend_connection

# ---------- PAGE CONFIG ----------
st.set_page_config(
    layout="wide",
    page_title="Active Incidents - PORTNET®",
    page_icon="🚨"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
.incident-card {
    background: white;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    border-left: 4px solid #ff5252;
    cursor: pointer;
    transition: all 0.3s ease;
}

.incident-card:hover {
    box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
    transform: translateX(4px);
}

.incident-card-selected {
    border-left: 4px solid #0CB654;
    background: #f1f8f4;
}

.incident-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

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

.status-warning {
    background-color: #fff3e0;
    color: #ef6c00;
}

.status-resolved {
    background-color: #e8f5e9;
    color: #2e7d32;
}

.detail-section {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
}

.section-title {
    font-size: 18px;
    font-weight: bold;
    color: #0A5C2F;
    margin-bottom: 12px;
    border-bottom: 2px solid #0CB654;
    padding-bottom: 8px;
}

.action-step {
    background: #f5f5f5;
    padding: 12px;
    margin: 8px 0;
    border-left: 4px solid #0CB654;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("🚨 Active Incidents Monitor")
st.markdown("Real-time view of all system incidents requiring attention")

# Check backend connection
if not check_backend_connection():
    st.stop()

st.markdown("---")

# ---------- FETCH EDI ERRORS ----------
api_client = get_api_client()

with st.spinner("Loading active incidents..."):
    edi_errors_response = api_client.get_edi_errors(limit=50)

if 'error' in edi_errors_response:
    st.error(f"Failed to load incidents: {edi_errors_response['error']}")
    st.stop()

edi_errors = edi_errors_response.get('errors', [])

# Initialize session state for selected incident
if 'selected_incident_idx' not in st.session_state:
    st.session_state.selected_incident_idx = 0 if edi_errors else None

# ---------- FILTERS ----------
st.markdown("### 🔍 Filters")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    status_filter = st.multiselect(
        "Status",
        options=['ERROR', 'PARSED', 'RECEIVED', 'ACKED'],
        default=['ERROR']
    )

with filter_col2:
    message_type_filter = st.multiselect(
        "Message Type",
        options=['COPARN', 'COARRI', 'CODECO', 'IFTMIN', 'IFTMCS'],
        default=[]
    )

with filter_col3:
    search_term = st.text_input(
        "Search",
        placeholder="Search by container, error text...",
        help="Search in error messages"
    )

# Apply filters
filtered_errors = edi_errors

if status_filter:
    filtered_errors = [e for e in filtered_errors if e.get('status') in status_filter]

if message_type_filter:
    filtered_errors = [e for e in filtered_errors if e.get('message_type') in message_type_filter]

if search_term:
    search_term_lower = search_term.lower()
    filtered_errors = [
        e for e in filtered_errors 
        if search_term_lower in str(e.get('error_text', '')).lower() 
        or search_term_lower in str(e.get('container_id', '')).lower()
    ]

st.markdown(f"**Showing {len(filtered_errors)} incidents**")
st.markdown("---")

# ---------- LAYOUT: LIST + DETAILS ----------
if not filtered_errors:
    st.info("✅ No incidents match the current filters.")
else:
    left_col, right_col = st.columns([1, 2])
    
    # ---------- LEFT: INCIDENTS LIST ----------
    with left_col:
        st.markdown("### 📋 Incident List")
        
        for idx, error in enumerate(filtered_errors):
            is_selected = (st.session_state.selected_incident_idx == idx)
            card_class = "incident-card incident-card-selected" if is_selected else "incident-card"
            
            status = error.get('status', 'UNKNOWN')
            status_class = 'status-error' if status == 'ERROR' else 'status-warning'
            
            message_type = error.get('message_type', 'N/A')
            error_text = error.get('error_text', 'No details')[:60]
            sent_at = error.get('sent_at', 'Unknown')
            container_id = error.get('container_id', 'N/A')
            
            st.markdown(f"""
            <div class="{card_class}">
                <div class="incident-header">
                    <strong>INC-{idx+1:03d}</strong>
                    <span class="status-badge {status_class}">{status}</span>
                </div>
                <div style="font-size: 14px; color: #555;">
                    <strong>{message_type}</strong> | Container: {container_id}
                </div>
                <div style="font-size: 13px; color: #777; margin-top: 4px;">
                    {error_text}...
                </div>
                <div style="font-size: 12px; color: #999; margin-top: 4px;">
                    🕐 {sent_at}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Button to select this incident
            if st.button(f"View Details", key=f"view_inc_{idx}", use_container_width=True):
                st.session_state.selected_incident_idx = idx
                st.rerun()
    
    # ---------- RIGHT: INCIDENT DETAILS ----------
    with right_col:
        if st.session_state.selected_incident_idx is not None and st.session_state.selected_incident_idx < len(filtered_errors):
            selected_error = filtered_errors[st.session_state.selected_incident_idx]
            
            st.markdown(f"### 📊 Incident Details - INC-{st.session_state.selected_incident_idx+1:03d}")
            
            # Create tabs
            tab1, tab2, tab3 = st.tabs(["🎯 Analysis", "📦 Container Info", "📨 EDI Details"])
            
            # ---------- TAB 1: ANALYSIS ----------
            with tab1:
                # Run analysis on this EDI error
                container_id = selected_error.get('container_id', None)
                error_text = selected_error.get('error_text', 'Unknown error')
                message_type = selected_error.get('message_type', 'Unknown')
                sent_at = selected_error.get('sent_at', 'Unknown')
                
                # Construct a log line from the EDI error
                log_line = f"{sent_at} ERROR [EDI-Parser] Failed to parse {message_type} message: {error_text}. container_id: {container_id}"
                
                if st.button("🔄 Run AI Analysis", type="primary", use_container_width=True):
                    with st.spinner("Analyzing incident..."):
                        analysis_result = api_client.analyze_log(log_line)
                    
                    if 'error' in analysis_result:
                        st.error(f"Analysis failed: {analysis_result['error']}")
                    else:
                        st.session_state['current_analysis'] = analysis_result
                        st.rerun()
                
                # Display cached analysis if available
                if 'current_analysis' in st.session_state:
                    analysis_result = st.session_state['current_analysis']
                    analysis = analysis_result.get('analysis', {})
                    
                    # Root Cause
                    st.markdown("<div class='detail-section'>", unsafe_allow_html=True)
                    st.markdown("<div class='section-title'>🎯 Root Cause</div>", unsafe_allow_html=True)
                    st.markdown(analysis.get('root_cause', 'Not identified'))
                    
                    technical_details = analysis.get('technical_details', '')
                    if technical_details:
                        st.markdown("**Technical Details:**")
                        st.markdown(technical_details)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Immediate Actions
                    st.markdown("<div class='detail-section'>", unsafe_allow_html=True)
                    st.markdown("<div class='section-title'>⚡ Remediation Steps</div>", unsafe_allow_html=True)
                    
                    actions = analysis.get('immediate_actions', [])
                    if actions:
                        for idx, action in enumerate(actions, 1):
                            st.markdown(f"""
                            <div class='action-step'>
                                <strong>Step {idx}:</strong> {action}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No specific actions identified. Manual review required.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Impact & Escalation
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("<div class='detail-section'>", unsafe_allow_html=True)
                        st.markdown("<div class='section-title'>💼 Business Impact</div>", unsafe_allow_html=True)
                        st.markdown(analysis.get('business_impact', 'Not assessed'))
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("<div class='detail-section'>", unsafe_allow_html=True)
                        st.markdown("<div class='section-title'>📢 Escalation</div>", unsafe_allow_html=True)
                        st.markdown(analysis.get('escalation', 'TBD'))
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Action buttons
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("✅ Mark Resolved", use_container_width=True):
                            st.success("Incident marked as resolved!")
                            del st.session_state['current_analysis']
                    
                    with col2:
                        if st.button("📢 Escalate", use_container_width=True):
                            st.warning("Escalated to Level 3 Support")
                    
                    with col3:
                        if st.button("🔗 View in Log Analyzer", use_container_width=True):
                            st.session_state['log_to_analyze'] = log_line
                            st.switch_page("pages/1_Log_Analyzer.py")
                
                else:
                    st.info("👆 Click 'Run AI Analysis' to get detailed recommendations")
            
            # ---------- TAB 2: CONTAINER INFO ----------
            with tab2:
                if container_id:
                    with st.spinner("Loading container details..."):
                        container_details = api_client.get_container_details(str(container_id))
                    
                    if 'error' in container_details:
                        st.error(f"Failed to load container: {container_details['error']}")
                    else:
                        container = container_details.get('container', {})
                        
                        if container:
                            # Basic info
                            st.markdown("#### 📦 Container Information")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Container No", container.get('cntr_no', 'N/A'))
                                st.metric("Status", container.get('status', 'N/A'))
                                st.metric("ISO Code", container.get('iso_code', 'N/A'))
                            
                            with col2:
                                st.metric("Size/Type", container.get('size_type', 'N/A'))
                                st.metric("Weight (kg)", f"{container.get('gross_weight_kg', 0):,.0f}")
                                st.metric("Hazard Class", container.get('hazard_class', 'None'))
                            
                            with col3:
                                st.metric("Origin Port", container.get('origin_port', 'N/A'))
                                st.metric("Destination", container.get('destination_port', 'N/A'))
                                st.metric("Vessel", container.get('vessel_name', 'N/A'))
                            
                            # Timeline
                            st.markdown("---")
                            st.markdown("#### 📅 Timeline")
                            
                            timeline_col1, timeline_col2, timeline_col3 = st.columns(3)
                            
                            with timeline_col1:
                                st.markdown("**ETA**")
                                st.markdown(container.get('eta_ts', 'N/A'))
                            
                            with timeline_col2:
                                st.markdown("**ETD**")
                                st.markdown(container.get('etd_ts', 'N/A'))
                            
                            with timeline_col3:
                                st.markdown("**Last Free Day**")
                                st.markdown(container.get('last_free_day', 'N/A'))
                            
                            # EDI Messages
                            edi_messages = container_details.get('edi_messages', [])
                            if edi_messages:
                                st.markdown("---")
                                st.markdown("#### 📨 EDI Message History")
                                
                                edi_df = pd.DataFrame(edi_messages)
                                if not edi_df.empty:
                                    # Select relevant columns
                                    display_cols = ['message_type', 'status', 'sent_at', 'sender', 'receiver']
                                    display_cols = [col for col in display_cols if col in edi_df.columns]
                                    st.dataframe(edi_df[display_cols], use_container_width=True, hide_index=True)
                            
                            # API Events
                            api_events = container_details.get('api_events', [])
                            if api_events:
                                st.markdown("---")
                                st.markdown("#### 🔄 API Event History")
                                
                                events_df = pd.DataFrame(api_events)
                                if not events_df.empty:
                                    display_cols = ['event_type', 'event_ts', 'source_system', 'http_status']
                                    display_cols = [col for col in display_cols if col in events_df.columns]
                                    st.dataframe(events_df[display_cols], use_container_width=True, hide_index=True)
                        else:
                            st.warning("Container information not found")
                else:
                    st.info("No container ID associated with this incident")
            
            # ---------- TAB 3: EDI DETAILS ----------
            with tab3:
                st.markdown("#### 📨 EDI Message Details")
                
                detail_col1, detail_col2 = st.columns(2)
                
                with detail_col1:
                    st.markdown("**Message Type:**")
                    st.code(selected_error.get('message_type', 'N/A'))
                    
                    st.markdown("**Direction:**")
                    st.code(selected_error.get('direction', 'N/A'))
                    
                    st.markdown("**Status:**")
                    status = selected_error.get('status', 'N/A')
                    status_color = "🔴" if status == 'ERROR' else "🟢"
                    st.markdown(f"{status_color} **{status}**")
                
                with detail_col2:
                    st.markdown("**Sender:**")
                    st.code(selected_error.get('sender', 'N/A'))
                    
                    st.markdown("**Receiver:**")
                    st.code(selected_error.get('receiver', 'N/A'))
                    
                    st.markdown("**Message Reference:**")
                    st.code(selected_error.get('message_ref', 'N/A'))
                
                st.markdown("---")
                
                st.markdown("**Timestamps:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Sent At:**")
                    st.text(selected_error.get('sent_at', 'N/A'))
                
                with col2:
                    st.markdown("**Acknowledged At:**")
                    st.text(selected_error.get('ack_at', 'N/A') or 'Not acknowledged')
                
                st.markdown("---")
                
                st.markdown("**Error Details:**")
                error_text = selected_error.get('error_text', 'No error text available')
                st.error(error_text)
                
                # Raw message
                raw_text = selected_error.get('raw_text', '')
                if raw_text:
                    st.markdown("**Raw EDI Message:**")
                    with st.expander("View Raw Message"):
                        st.code(raw_text, language="text")

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### 📊 Statistics")
    
    if filtered_errors:
        # Status breakdown
        status_counts = {}
        for error in filtered_errors:
            status = error.get('status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        st.markdown("**By Status:**")
        for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
            st.markdown(f"- {status}: **{count}**")
        
        st.markdown("---")
        
        # Message type breakdown
        msg_type_counts = {}
        for error in filtered_errors:
            msg_type = error.get('message_type', 'UNKNOWN')
            msg_type_counts[msg_type] = msg_type_counts.get(msg_type, 0) + 1
        
        st.markdown("**By Message Type:**")
        for msg_type, count in sorted(msg_type_counts.items(), key=lambda x: x[1], reverse=True):
            st.markdown(f"- {msg_type}: **{count}**")
    
    st.markdown("---")
    
    st.markdown("### 🔄 Actions")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    if st.button("📊 View Dashboard", use_container_width=True):
        st.switch_page("Dashboard.py")

