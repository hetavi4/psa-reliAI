"""
PORTNET® Database Explorer
Search and explore containers, vessels, and other database entities
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from api_client import get_api_client, check_backend_connection

# ---------- PAGE CONFIG ----------
st.set_page_config(
    layout="wide",
    page_title="Database Explorer - PORTNET®",
    page_icon="🔍"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
.search-result {
    background: white;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    border-left: 4px solid #0CB654;
}

.detail-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
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

.status-active {
    background-color: #e8f5e9;
    color: #2e7d32;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
}

.status-inactive {
    background-color: #ffebee;
    color: #c62828;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("🔍 Database Explorer")
st.markdown("Search and explore containers, vessels, and database entities")

# Check backend connection
if not check_backend_connection():
    st.stop()

st.markdown("---")

# ---------- TABS FOR DIFFERENT SEARCHES ----------
tab1, tab2, tab3 = st.tabs(["📦 Container Search", "🚢 Vessel Search", "📊 All Containers"])

# ---------- TAB 1: CONTAINER SEARCH ----------
with tab1:
    st.markdown("### 📦 Search Container by Number")
    
    container_search_col1, container_search_col2 = st.columns([3, 1])
    
    with container_search_col1:
        container_no = st.text_input(
            "Enter Container Number:",
            placeholder="e.g., MSKU0000007",
            help="Enter the full container number (4 letters + 7 digits)"
        )
    
    with container_search_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
    if search_button and container_no:
        api_client = get_api_client()
        
        with st.spinner(f"Searching for container {container_no}..."):
            result = api_client.get_container_details(container_no)
        
        if 'error' in result:
            st.error(f"❌ Search failed: {result['error']}")
        else:
            container = result.get('container', {})
            
            if not container:
                st.warning(f"No container found with number: {container_no}")
            else:
                st.success(f"✅ Container found: {container_no}")
                
                # Basic Information
                st.markdown("<div class='detail-card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-header'>📦 Basic Information</div>", unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Container No", container.get('cntr_no', 'N/A'))
                    st.metric("ISO Code", container.get('iso_code', 'N/A'))
                
                with col2:
                    st.metric("Status", container.get('status', 'N/A'))
                    st.metric("Size/Type", container.get('size_type', 'N/A'))
                
                with col3:
                    st.metric("Weight (kg)", f"{container.get('gross_weight_kg', 0):,.0f}")
                    st.metric("Hazard Class", container.get('hazard_class', 'None') or 'None')
                
                with col4:
                    st.metric("Vessel", container.get('vessel_name', 'N/A'))
                    st.metric("IMO No", container.get('imo_no', 'N/A'))
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Route Information
                st.markdown("<div class='detail-card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-header'>🌍 Route Information</div>", unsafe_allow_html=True)
                
                route_col1, route_col2, route_col3 = st.columns(3)
                
                with route_col1:
                    st.markdown("**Origin Port**")
                    st.markdown(f"### {container.get('origin_port', 'N/A')}")
                
                with route_col2:
                    st.markdown("**Tranship Port**")
                    st.markdown(f"### {container.get('tranship_port', 'N/A')}")
                
                with route_col3:
                    st.markdown("**Destination Port**")
                    st.markdown(f"### {container.get('destination_port', 'N/A')}")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Timeline
                st.markdown("<div class='detail-card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-header'>📅 Timeline</div>", unsafe_allow_html=True)
                
                timeline_col1, timeline_col2, timeline_col3 = st.columns(3)
                
                with timeline_col1:
                    st.markdown("**ETA (Estimated Time of Arrival)**")
                    st.info(container.get('eta_ts', 'N/A'))
                
                with timeline_col2:
                    st.markdown("**ETD (Estimated Time of Departure)**")
                    st.info(container.get('etd_ts', 'N/A'))
                
                with timeline_col3:
                    st.markdown("**Last Free Day**")
                    st.info(container.get('last_free_day', 'N/A'))
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # EDI Messages
                edi_messages = result.get('edi_messages', [])
                if edi_messages:
                    st.markdown("<div class='detail-card'>", unsafe_allow_html=True)
                    st.markdown("<div class='section-header'>📨 EDI Message History</div>", unsafe_allow_html=True)
                    
                    # Show error count
                    error_count = len([msg for msg in edi_messages if msg.get('status') == 'ERROR'])
                    if error_count > 0:
                        st.warning(f"⚠️ {error_count} EDI error(s) detected")
                    else:
                        st.success(f"✅ All {len(edi_messages)} EDI messages processed successfully")
                    
                    edi_df = pd.DataFrame(edi_messages)
                    
                    # Format dataframe
                    display_columns = ['message_type', 'status', 'sent_at', 'sender', 'receiver', 'error_text']
                    display_columns = [col for col in display_columns if col in edi_df.columns]
                    
                    if not edi_df.empty:
                        st.dataframe(
                            edi_df[display_columns],
                            use_container_width=True,
                            hide_index=True
                        )
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # API Events
                api_events = result.get('api_events', [])
                if api_events:
                    st.markdown("<div class='detail-card'>", unsafe_allow_html=True)
                    st.markdown("<div class='section-header'>🔄 API Event History</div>", unsafe_allow_html=True)
                    
                    st.info(f"📊 Total events: {len(api_events)}")
                    
                    events_df = pd.DataFrame(api_events)
                    
                    display_columns = ['event_type', 'event_ts', 'source_system', 'http_status']
                    display_columns = [col for col in display_columns if col in events_df.columns]
                    
                    if not events_df.empty:
                        st.dataframe(
                            events_df[display_columns],
                            use_container_width=True,
                            hide_index=True
                        )
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Action buttons
                st.markdown("---")
                action_col1, action_col2 = st.columns(2)
                
                with action_col1:
                    if st.button("📊 View in Active Incidents", use_container_width=True):
                        st.switch_page("pages/2_Active_Incidents.py")
                
                with action_col2:
                    if st.button("🔄 Refresh Data", use_container_width=True):
                        st.rerun()

# ---------- TAB 2: VESSEL SEARCH ----------
with tab2:
    st.markdown("### 🚢 Search by Pattern")
    st.markdown("Search for containers, vessels, or other entities matching a pattern")
    
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        pattern = st.text_input(
            "Enter search pattern:",
            placeholder="e.g., MSKU, MV Lion, etc.",
            help="Search for containers, vessels, or other patterns"
        )
    
    with search_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        pattern_search_button = st.button("🔍 Search Pattern", type="primary", use_container_width=True)
    
    if pattern_search_button and pattern:
        api_client = get_api_client()
        
        with st.spinner(f"Searching for pattern: {pattern}..."):
            search_result = api_client.search_incidents(pattern)
        
        if 'error' in search_result:
            st.error(f"❌ Search failed: {search_result['error']}")
        else:
            results = search_result.get('results', [])
            total = search_result.get('total', 0)
            
            if total == 0:
                st.warning(f"No results found for pattern: {pattern}")
            else:
                st.success(f"✅ Found {total} result(s) matching '{pattern}'")
                
                # Display results
                for idx, item in enumerate(results):
                    st.markdown(f"""
                    <div class='search-result'>
                        <strong>Result #{idx+1}</strong>
                        <pre>{item}</pre>
                    </div>
                    """, unsafe_allow_html=True)

# ---------- TAB 3: ALL CONTAINERS ----------
with tab3:
    st.markdown("### 📊 All Containers Overview")
    
    api_client = get_api_client()
    
    # Fetch all containers
    with st.spinner("Loading all containers..."):
        containers_response = api_client.get_all_containers()
    
    if 'error' in containers_response:
        st.error(f"Failed to load containers: {containers_response['error']}")
    else:
        containers = containers_response.get('containers', [])
        total = containers_response.get('total', 0)
        
        st.info(f"📦 Total containers in system: **{total}**")
        
        if containers:
            # Convert to DataFrame
            df = pd.DataFrame(containers)
            
            # Status filter
            st.markdown("#### Filters")
            
            filter_col1, filter_col2 = st.columns(2)
            
            with filter_col1:
                # Status filter
                unique_statuses = df['status'].unique().tolist() if 'status' in df.columns else []
                selected_statuses = st.multiselect(
                    "Filter by Status:",
                    options=unique_statuses,
                    default=[]
                )
            
            with filter_col2:
                # Port filter
                unique_ports = []
                if 'origin_port' in df.columns:
                    unique_ports.extend(df['origin_port'].unique().tolist())
                if 'destination_port' in df.columns:
                    unique_ports.extend(df['destination_port'].unique().tolist())
                unique_ports = list(set(unique_ports))
                
                selected_ports = st.multiselect(
                    "Filter by Port:",
                    options=unique_ports,
                    default=[]
                )
            
            # Apply filters
            filtered_df = df.copy()
            
            if selected_statuses:
                filtered_df = filtered_df[filtered_df['status'].isin(selected_statuses)]
            
            if selected_ports:
                filtered_df = filtered_df[
                    (filtered_df['origin_port'].isin(selected_ports)) | 
                    (filtered_df['destination_port'].isin(selected_ports))
                ]
            
            st.markdown(f"**Showing {len(filtered_df)} of {total} containers**")
            
            # Display dataframe
            if not filtered_df.empty:
                # Select columns to display
                display_cols = [
                    'cntr_no', 'status', 'size_type', 'gross_weight_kg',
                    'origin_port', 'destination_port', 'vessel_name'
                ]
                display_cols = [col for col in display_cols if col in filtered_df.columns]
                
                st.dataframe(
                    filtered_df[display_cols],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download option
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name="containers_export.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No containers match the selected filters")
            
            # Statistics
            st.markdown("---")
            st.markdown("### 📈 Statistics")
            
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            
            with stat_col1:
                if 'status' in df.columns:
                    status_counts = df['status'].value_counts()
                    st.markdown("**By Status:**")
                    for status, count in status_counts.items():
                        st.markdown(f"- {status}: **{count}**")
            
            with stat_col2:
                if 'size_type' in df.columns:
                    size_counts = df['size_type'].value_counts()
                    st.markdown("**By Size:**")
                    for size, count in size_counts.head(5).items():
                        st.markdown(f"- {size}: **{count}**")
            
            with stat_col3:
                if 'origin_port' in df.columns:
                    origin_counts = df['origin_port'].value_counts()
                    st.markdown("**Top Origins:**")
                    for port, count in origin_counts.head(5).items():
                        st.markdown(f"- {port}: **{count}**")
            
            with stat_col4:
                if 'destination_port' in df.columns:
                    dest_counts = df['destination_port'].value_counts()
                    st.markdown("**Top Destinations:**")
                    for port, count in dest_counts.head(5).items():
                        st.markdown(f"- {port}: **{count}**")

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### 💡 Quick Tips")
    st.markdown("""
    **Container Search:**
    - Enter exact container number
    - Format: 4 letters + 7 digits
    - Example: MSKU0000007
    
    **Pattern Search:**
    - Search by partial matches
    - Works for containers, vessels
    - Example: MSKU, MV Lion
    
    **All Containers:**
    - View complete inventory
    - Filter by status or port
    - Download data as CSV
    """)
    
    st.markdown("---")
    
    st.markdown("### 🔄 Quick Actions")
    
    if st.button("📊 View Dashboard", use_container_width=True):
        st.switch_page("Dashboard.py")
    
    if st.button("🚨 View Incidents", use_container_width=True):
        st.switch_page("pages/2_Active_Incidents.py")

