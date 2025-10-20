"""
PORTNET® Log Analyzer
Real-time log line analysis with AI-powered incident detection and resolution recommendations
"""
import streamlit as st
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from api_client import get_api_client, check_backend_connection

# ---------- PAGE CONFIG ----------
st.set_page_config(
    layout="wide",
    page_title="Log Analyzer - PORTNET®",
    page_icon="🔍"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
.analysis-section {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
}

.section-header {
    font-size: 18px;
    font-weight: bold;
    color: #0A5C2F;
    margin-bottom: 12px;
    border-bottom: 2px solid #0CB654;
    padding-bottom: 8px;
}

.entity-badge {
    display: inline-block;
    padding: 6px 12px;
    margin: 4px;
    border-radius: 16px;
    background: #e8f5e9;
    color: #2e7d32;
    font-size: 13px;
    font-weight: 600;
}

.severity-high {
    background: #ffebee;
    color: #c62828;
}

.severity-medium {
    background: #fff3e0;
    color: #ef6c00;
}

.severity-low {
    background: #e3f2fd;
    color: #1565c0;
}

.action-item {
    background: #f5f5f5;
    padding: 12px;
    margin: 8px 0;
    border-left: 4px solid #0CB654;
    border-radius: 4px;
}

.confidence-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-weight: bold;
    font-size: 12px;
}

.confidence-high {
    background: #4CAF50;
    color: white;
}

.confidence-medium {
    background: #FF9800;
    color: white;
}

.confidence-low {
    background: #f44336;
    color: white;
}

.kb-result {
    background: #fafafa;
    padding: 12px;
    margin: 8px 0;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("🔍 Real-Time Log Analyzer")
st.markdown("Analyze log lines with AI-powered root cause detection and remediation recommendations")

# Check backend connection
if not check_backend_connection():
    st.stop()

st.markdown("---")

# ---------- LOG INPUT SECTION ----------
st.markdown("### 📝 Enter Log Line for Analysis")

# Sample log lines for quick testing
sample_logs = {
    "EDI Parse Error": "2025-10-19 14:23:15 ERROR [EDI-Parser] Failed to parse IFTMIN message: Segment missing. container: MSKU0000007",
    "Container Status Mismatch": "2025-10-20 08:15:30 ERROR [TOS-Service] Container status mismatch detected for MSCU0000006. Expected: LOADED, Found: IN_YARD",
    "Duplicate Container Entry": "2025-10-20 10:42:18 ERROR [Container-Service] Duplicate entry for container CMAU0000020. Constraint violation on primary key.",
    "Vessel Advice Conflict": "2025-10-20 12:30:45 WARNING [Berth-Service] Multiple active vessel advice records detected for MV Lion City 08. Data integrity issue.",
    "API Timeout": "2025-10-20 15:22:10 ERROR [API-Gateway] Connection timeout while fetching data for container TEMU0000015. Downstream service unavailable."
}

col1, col2 = st.columns([3, 1])

with col1:
    log_input = st.text_area(
        "Enter log line to analyze:",
        height=120,
        placeholder="Paste error/warning log line here...",
        help="Enter a log line containing ERROR, WARN, or CRITICAL"
    )

with col2:
    st.markdown("**Quick Test Samples:**")
    selected_sample = st.selectbox(
        "Choose a sample:",
        options=[""] + list(sample_logs.keys()),
        label_visibility="collapsed"
    )
    
    if selected_sample and st.button("Load Sample", use_container_width=True):
        log_input = sample_logs[selected_sample]
        st.rerun()

# Check if there's a log from dashboard
if 'log_to_analyze' in st.session_state and not log_input:
    log_input = st.session_state['log_to_analyze']
    st.info("📌 Loaded log from dashboard")
    del st.session_state['log_to_analyze']

analyze_button = st.button("🚀 Analyze Log Line", type="primary", use_container_width=True)

# ---------- ANALYSIS SECTION ----------
if analyze_button and log_input:
    api_client = get_api_client()
    
    with st.spinner("🔄 Analyzing log line... This may take a few seconds..."):
        result = api_client.analyze_log(log_input)
    
    if 'error' in result:
        st.error(f"❌ Analysis failed: {result['error']}")
    else:
        # Display results
        st.success("✅ Analysis Complete!")
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 AI Analysis", 
            "📊 Database Context", 
            "📚 Knowledge Base Results",
            "🔧 Raw Data"
        ])
        
        # ---------- TAB 1: AI ANALYSIS ----------
        with tab1:
            incident = result.get('incident', {})
            analysis = result.get('analysis', {})
            
            # Incident Overview
            st.markdown("<div class='analysis-section'>", unsafe_allow_html=True)
            st.markdown("<div class='section-header'>📋 Incident Overview</div>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                timestamp = incident.get('timestamp', 'N/A')
                st.markdown(f"**⏰ Timestamp:** {timestamp}")
            
            with col2:
                severity = incident.get('severity', 'MEDIUM')
                severity_class = f"severity-{severity.lower()}"
                st.markdown(f"**🚨 Severity:** <span class='entity-badge {severity_class}'>{severity}</span>", unsafe_allow_html=True)
            
            with col3:
                confidence = analysis.get('confidence', 'MEDIUM')
                confidence_class = f"confidence-{confidence.lower()}"
                st.markdown(f"**🎯 Confidence:** <span class='confidence-badge {confidence_class}'>{confidence}</span>", unsafe_allow_html=True)
            
            # Entities Detected
            entities = incident.get('entities', {})
            if any(entities.values()):
                st.markdown("**🔍 Entities Detected:**")
                
                if entities.get('containers'):
                    st.markdown("**Containers:**")
                    for container in entities['containers']:
                        st.markdown(f"<span class='entity-badge'>📦 {container}</span>", unsafe_allow_html=True)
                
                if entities.get('vessels'):
                    st.markdown("**Vessels:**")
                    for vessel in entities['vessels']:
                        st.markdown(f"<span class='entity-badge'>🚢 {vessel}</span>", unsafe_allow_html=True)
                
                if entities.get('message_types'):
                    st.markdown("**EDI Message Types:**")
                    for msg_type in entities['message_types']:
                        st.markdown(f"<span class='entity-badge'>📨 {msg_type}</span>", unsafe_allow_html=True)
                
                if entities.get('error_keywords'):
                    st.markdown("**Error Types:**")
                    for keyword in entities['error_keywords']:
                        st.markdown(f"<span class='entity-badge severity-high'>⚠️ {keyword}</span>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Root Cause
            st.markdown("<div class='analysis-section'>", unsafe_allow_html=True)
            st.markdown("<div class='section-header'>🎯 Root Cause Analysis</div>", unsafe_allow_html=True)
            
            root_cause = analysis.get('root_cause', 'Not identified')
            st.markdown(f"**{root_cause}**")
            
            technical_details = analysis.get('technical_details', '')
            if technical_details:
                st.markdown("**Technical Details:**")
                st.markdown(technical_details)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Immediate Actions
            st.markdown("<div class='analysis-section'>", unsafe_allow_html=True)
            st.markdown("<div class='section-header'>⚡ Immediate Remediation Steps</div>", unsafe_allow_html=True)
            
            actions = analysis.get('immediate_actions', [])
            if actions:
                for idx, action in enumerate(actions, 1):
                    st.markdown(f"""
                    <div class='action-item'>
                        <strong>Step {idx}:</strong> {action}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No specific actions recommended. Manual investigation required.")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Business Impact & Escalation
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<div class='analysis-section'>", unsafe_allow_html=True)
                st.markdown("<div class='section-header'>💼 Business Impact</div>", unsafe_allow_html=True)
                business_impact = analysis.get('business_impact', 'Impact assessment unavailable')
                st.markdown(business_impact)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div class='analysis-section'>", unsafe_allow_html=True)
                st.markdown("<div class='section-header'>📢 Escalation Path</div>", unsafe_allow_html=True)
                escalation = analysis.get('escalation', 'Contact Level 3 support if unresolved')
                st.markdown(escalation)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Action Buttons
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("✅ Mark as Resolved", use_container_width=True):
                    st.success("Incident marked as resolved ✅")
            
            with col2:
                if st.button("📢 Escalate to L3", use_container_width=True):
                    st.warning("Escalated to Level 3 Support ⚠️")
            
            with col3:
                if st.button("📋 Generate Report", use_container_width=True):
                    # Generate escalation report
                    report = f"""
PORTNET® INCIDENT REPORT
========================
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Severity: {severity}
Confidence: {confidence}

ROOT CAUSE:
{root_cause}

TECHNICAL DETAILS:
{technical_details}

REMEDIATION STEPS:
{chr(10).join([f"{i}. {action}" for i, action in enumerate(actions, 1)])}

BUSINESS IMPACT:
{business_impact}

ESCALATION:
{escalation}

--- End of Report ---
"""
                    st.download_button(
                        label="📥 Download Report",
                        data=report,
                        file_name=f"incident_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
            
            with col4:
                if st.button("🔄 Analyze Another", use_container_width=True):
                    st.rerun()
        
        # ---------- TAB 2: DATABASE CONTEXT ----------
        with tab2:
            db_context = result.get('database_context', {})
            
            if not db_context:
                st.info("No database context available for this log line.")
            else:
                for key, value in db_context.items():
                    if isinstance(value, dict):
                        st.markdown(f"### {key.replace('_', ' ').title()}")
                        
                        if 'error' in value:
                            st.error(f"Error fetching data: {value['error']}")
                        else:
                            # Display container details
                            if 'container' in value:
                                container = value['container']
                                
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("Container No", container.get('cntr_no', 'N/A'))
                                    st.metric("Status", container.get('status', 'N/A'))
                                
                                with col2:
                                    st.metric("Origin Port", container.get('origin_port', 'N/A'))
                                    st.metric("Destination", container.get('destination_port', 'N/A'))
                                
                                with col3:
                                    st.metric("Vessel", container.get('vessel_name', 'N/A'))
                                    st.metric("Weight (kg)", f"{container.get('gross_weight_kg', 0):,.0f}")
                                
                                # EDI Messages
                                edi_messages = value.get('edi_messages', [])
                                if edi_messages:
                                    st.markdown("**📨 EDI Messages:**")
                                    for msg in edi_messages[:5]:
                                        status_color = "🔴" if msg.get('status') == 'ERROR' else "🟢"
                                        st.markdown(f"- {status_color} {msg.get('message_type')} | {msg.get('status')} | {msg.get('sent_at')}")
                                        if msg.get('error_text'):
                                            st.markdown(f"  *Error: {msg['error_text']}*")
                                
                                # API Events
                                api_events = value.get('api_events', [])
                                if api_events:
                                    st.markdown("**🔄 Recent API Events:**")
                                    for evt in api_events[:5]:
                                        st.markdown(f"- {evt.get('event_type')} | {evt.get('event_ts')} | Source: {evt.get('source_system')}")
                            
                            # Display vessel details
                            elif 'active_count' in value:
                                st.metric("Active Vessel Advice Records", value.get('active_count', 0))
                                
                                if value.get('has_conflict'):
                                    st.error("⚠️ **CONFLICT DETECTED:** Multiple active vessel advice records found!")
                                    st.warning("This indicates a data integrity issue that requires immediate attention.")
                                else:
                                    st.success("✅ No conflicts detected")
                                
                                if 'records' in value:
                                    st.markdown("**Records:**")
                                    st.json(value['records'])
                        
                        st.markdown("---")
        
        # ---------- TAB 3: KNOWLEDGE BASE RESULTS ----------
        with tab3:
            kb_results = result.get('knowledge_base_results', {})
            
            # Past Cases
            cases = kb_results.get('cases', [])
            if cases:
                st.markdown("### 📂 Similar Past Cases")
                st.markdown("Historical cases from the support log database:")
                
                for idx, case in enumerate(cases[:5], 1):
                    score = case.get('_score', 0)
                    text = case.get('text', 'No content')
                    
                    st.markdown(f"""
                    <div class='kb-result'>
                        <div style='display: flex; justify-content: space-between;'>
                            <strong>Case #{idx}</strong>
                            <span style='color: #666; font-size: 13px;'>Similarity: {score:.2f}</span>
                        </div>
                        <p style='margin-top: 8px; color: #444;'>{text[:500]}{'...' if len(text) > 500 else ''}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No similar past cases found in the database.")
            
            st.markdown("---")
            
            # Knowledge Base Articles
            knowledge = kb_results.get('knowledge', [])
            if knowledge:
                st.markdown("### 📚 Knowledge Base Articles")
                st.markdown("Relevant documentation and resolution guides:")
                
                for idx, kb in enumerate(knowledge[:5], 1):
                    score = kb.get('_score', 0)
                    text = kb.get('text', 'No content')
                    
                    st.markdown(f"""
                    <div class='kb-result'>
                        <div style='display: flex; justify-content: space-between;'>
                            <strong>KB Article #{idx}</strong>
                            <span style='color: #666; font-size: 13px;'>Relevance: {score:.2f}</span>
                        </div>
                        <p style='margin-top: 8px; color: #444;'>{text[:500]}{'...' if len(text) > 500 else ''}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No relevant knowledge base articles found.")
        
        # ---------- TAB 4: RAW DATA ----------
        with tab4:
            st.markdown("### 🔧 Raw Analysis Data")
            st.markdown("Complete JSON response from the backend API:")
            
            st.json(result)
            
            # Download option
            st.download_button(
                label="📥 Download Raw JSON",
                data=json.dumps(result, indent=2),
                file_name=f"analysis_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

elif analyze_button:
    st.warning("⚠️ Please enter a log line to analyze.")

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### 📖 How to Use")
    st.markdown("""
    1. **Paste a log line** containing ERROR, WARN, or CRITICAL
    2. **Click Analyze** to get AI-powered insights
    3. **Review the analysis** including:
       - Root cause identification
       - Remediation steps
       - Database context
       - Similar past cases
    4. **Take action** - resolve, escalate, or generate report
    """)
    
    st.markdown("---")
    
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Use the sample logs for quick testing
    - Include container/vessel IDs for better context
    - EDI and API service logs work best
    - The AI uses historical data for recommendations
    """)

