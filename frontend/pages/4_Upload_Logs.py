"""
PORTNET® Log File Upload
Upload and analyze complete log files for batch incident detection
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
    page_title="Upload Logs - PORTNET®",
    page_icon="📤"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
.upload-zone {
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    border: 3px dashed #0CB654;
    border-radius: 16px;
    padding: 40px;
    text-align: center;
    margin: 20px 0;
}

.result-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
}

.incident-summary {
    background: #f5f5f5;
    border-radius: 8px;
    padding: 16px;
    margin: 12px 0;
    border-left: 4px solid #0CB654;
}

.severity-high {
    border-left-color: #f44336;
}

.severity-medium {
    border-left-color: #ff9800;
}

.section-header {
    font-size: 18px;
    font-weight: bold;
    color: #0A5C2F;
    margin-bottom: 12px;
    border-bottom: 2px solid #0CB654;
    padding-bottom: 8px;
}

.stat-box {
    background: white;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
}

.stat-value {
    font-size: 36px;
    font-weight: bold;
    color: #0A5C2F;
}

.stat-label {
    font-size: 14px;
    color: #666;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("📤 Batch Log File Analyzer")
st.markdown("Upload complete log files for automated incident detection and analysis")

# Check backend connection
if not check_backend_connection():
    st.stop()

st.markdown("---")

# ---------- FILE UPLOAD SECTION ----------
st.markdown("### 📁 Upload Log Files")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div class='upload-zone'>
        <h3>📂 Drag and Drop Log Files Here</h3>
        <p>Supported formats: .log, .txt</p>
        <p>Maximum file size: 10 MB</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose log files",
        type=['log', 'txt'],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

with col2:
    st.markdown("### 📋 Sample Log Files")
    st.markdown("""
    Available sample logs:
    - API Event Service
    - Berth Application
    - Container Service
    - EDI Advice
    - Vessel Advice
    - Vessel Registry
    """)
    
    if st.button("📥 Load Sample Logs", use_container_width=True):
        st.info("Sample logs will be analyzed from the data/logs directory")

# ---------- ANALYZE UPLOADED FILES ----------
if uploaded_files:
    st.markdown("---")
    st.markdown(f"### 📊 Uploaded Files ({len(uploaded_files)})")
    
    for uploaded_file in uploaded_files:
        with st.expander(f"📄 {uploaded_file.name} ({uploaded_file.size:,} bytes)"):
            st.code(uploaded_file.read(500).decode('utf-8', errors='ignore')[:500] + "...")
            uploaded_file.seek(0)  # Reset file pointer
    
    # Analyze button
    if st.button("🚀 Analyze All Files", type="primary", use_container_width=True):
        api_client = get_api_client()
        
        all_results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Analyzing {uploaded_file.name}... ({idx+1}/{len(uploaded_files)})")
            
            # Read file content
            file_content = uploaded_file.read()
            uploaded_file.seek(0)  # Reset for next use
            
            # Upload to backend
            with st.spinner(f"Processing {uploaded_file.name}..."):
                result = api_client.upload_log_file(file_content, uploaded_file.name)
            
            if 'error' not in result:
                all_results.append(result)
            else:
                st.error(f"Failed to analyze {uploaded_file.name}: {result['error']}")
            
            # Update progress
            progress_bar.progress((idx + 1) / len(uploaded_files))
        
        status_text.text("Analysis complete! ✅")
        progress_bar.empty()
        
        # Store results in session state
        st.session_state['upload_results'] = all_results
        st.rerun()

# ---------- DISPLAY RESULTS ----------
if 'upload_results' in st.session_state and st.session_state['upload_results']:
    results = st.session_state['upload_results']
    
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Overall statistics
    total_lines = sum(r.get('total_lines', 0) for r in results)
    total_incidents = sum(r.get('analyzed_incidents', 0) for r in results)
    total_files = len(results)
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-value'>{total_files}</div>
            <div class='stat-label'>Files Analyzed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col2:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-value'>{total_lines:,}</div>
            <div class='stat-label'>Total Lines</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col3:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-value' style='color: #f44336;'>{total_incidents}</div>
            <div class='stat-label'>Incidents Detected</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col4:
        detection_rate = (total_incidents / total_lines * 100) if total_lines > 0 else 0
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-value' style='color: #ff9800;'>{detection_rate:.1f}%</div>
            <div class='stat-label'>Detection Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detailed results by file
    st.markdown("### 📁 Detailed Results by File")
    
    for file_result in results:
        filename = file_result.get('filename', 'Unknown')
        total_lines = file_result.get('total_lines', 0)
        incidents_count = file_result.get('analyzed_incidents', 0)
        incidents = file_result.get('results', [])
        
        with st.expander(f"📄 {filename} - {incidents_count} incidents found in {total_lines} lines"):
            if incidents_count == 0:
                st.info("✅ No incidents detected in this file")
            else:
                # Show incidents
                for idx, incident_result in enumerate(incidents[:20], 1):  # Limit to first 20
                    incident = incident_result.get('incident', {})
                    analysis = incident_result.get('analysis', {})
                    
                    severity = incident.get('severity', 'MEDIUM')
                    severity_class = f"severity-{severity.lower()}"
                    
                    st.markdown(f"""
                    <div class='incident-summary {severity_class}'>
                        <strong>Incident #{idx}</strong> | Severity: {severity} | 
                        Confidence: {analysis.get('confidence', 'MEDIUM')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Incident details
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📋 Root Cause:**")
                        st.markdown(analysis.get('root_cause', 'Not identified'))
                    
                    with col2:
                        st.markdown("**⚡ First Action:**")
                        actions = analysis.get('immediate_actions', [])
                        if actions:
                            st.markdown(actions[0])
                        else:
                            st.markdown("Manual investigation required")
                    
                    # Raw log
                    with st.expander("View Raw Log"):
                        st.code(incident.get('raw_log', ''))
                    
                    st.markdown("---")
                
                if len(incidents) > 20:
                    st.warning(f"⚠️ Showing first 20 of {len(incidents)} incidents. Download full report for complete analysis.")
    
    # Export options
    st.markdown("---")
    st.markdown("### 📥 Export Results")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        # Export summary
        summary_report = f"""
PORTNET® BATCH LOG ANALYSIS REPORT
===================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
-------
Files Analyzed: {total_files}
Total Lines Processed: {total_lines:,}
Incidents Detected: {total_incidents}
Detection Rate: {detection_rate:.2f}%

FILE BREAKDOWN
--------------
"""
        for file_result in results:
            summary_report += f"\n{file_result.get('filename', 'Unknown')}:\n"
            summary_report += f"  Lines: {file_result.get('total_lines', 0):,}\n"
            summary_report += f"  Incidents: {file_result.get('analyzed_incidents', 0)}\n"
        
        st.download_button(
            label="📄 Download Summary Report",
            data=summary_report,
            file_name=f"log_analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with export_col2:
        # Export detailed incidents as CSV
        all_incidents = []
        for file_result in results:
            filename = file_result.get('filename', 'Unknown')
            for incident_result in file_result.get('results', []):
                incident = incident_result.get('incident', {})
                analysis = incident_result.get('analysis', {})
                
                all_incidents.append({
                    'File': filename,
                    'Timestamp': incident.get('timestamp', 'N/A'),
                    'Severity': incident.get('severity', 'MEDIUM'),
                    'Root Cause': analysis.get('root_cause', 'Not identified'),
                    'Confidence': analysis.get('confidence', 'MEDIUM'),
                    'Business Impact': analysis.get('business_impact', 'N/A'),
                    'Escalation': analysis.get('escalation', 'N/A')
                })
        
        if all_incidents:
            incidents_df = pd.DataFrame(all_incidents)
            csv = incidents_df.to_csv(index=False)
            
            st.download_button(
                label="📊 Download Incidents CSV",
                data=csv,
                file_name=f"incidents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with export_col3:
        # Export full JSON
        import json
        
        full_json = json.dumps(results, indent=2)
        
        st.download_button(
            label="🔧 Download Full JSON",
            data=full_json,
            file_name=f"analysis_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    # Clear results button
    st.markdown("---")
    if st.button("🔄 Clear Results & Upload New Files", use_container_width=True):
        del st.session_state['upload_results']
        st.rerun()

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### 📖 How to Use")
    st.markdown("""
    1. **Upload log files** using the file uploader
    2. **Review uploaded files** in the expandable sections
    3. **Click Analyze** to process all files
    4. **Review results** with incident summaries
    5. **Export reports** for documentation
    """)
    
    st.markdown("---")
    
    st.markdown("### 💡 Features")
    st.markdown("""
    - **Batch Processing**: Analyze multiple files at once
    - **AI Analysis**: Automatic root cause detection
    - **Database Context**: Real-time system state lookup
    - **Knowledge Base**: Historical case matching
    - **Export Options**: CSV, JSON, Text reports
    """)
    
    st.markdown("---")
    
    st.markdown("### 📊 Supported Log Types")
    st.markdown("""
    - ✅ API Event Service logs
    - ✅ EDI Parser logs
    - ✅ Container Service logs
    - ✅ Vessel Service logs
    - ✅ TOS Service logs
    - ✅ Gateway logs
    """)
    
    st.markdown("---")
    
    st.markdown("### 🔄 Quick Navigation")
    
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("Dashboard.py")
    
    if st.button("🔍 Log Analyzer", use_container_width=True):
        st.switch_page("pages/1_Log_Analyzer.py")
    
    if st.button("🚨 Active Incidents", use_container_width=True):
        st.switch_page("pages/2_Active_Incidents.py")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #777; font-size: 13px;'>
    PORTNET® AI Incident Management System | Batch Log Analyzer | © 2025
</div>
""", unsafe_allow_html=True)

