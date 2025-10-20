"""
API Client for connecting Streamlit frontend to FastAPI backend
Handles all HTTP requests to the backend server
"""
import requests
import streamlit as st
from typing import Dict, Any, List, Optional

# Backend configuration
BACKEND_URL = "http://localhost:8000"

class APIClient:
    """Client for making API requests to FastAPI backend"""
    
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and errors"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_detail = "Unknown error"
            try:
                error_detail = response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            return {'error': error_detail, 'status_code': response.status_code}
        except requests.exceptions.ConnectionError:
            return {'error': 'Cannot connect to backend. Make sure the FastAPI server is running on http://localhost:8000'}
        except Exception as e:
            return {'error': f'Unexpected error: {str(e)}'}
    
    def health_check(self) -> Dict[str, Any]:
        """Check if backend is healthy"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            return {'error': 'Backend request timed out'}
    
    def analyze_log(self, log_line: str) -> Dict[str, Any]:
        """Analyze a single log line"""
        try:
            response = requests.post(
                f"{self.base_url}/api/analyze",
                json={"log_line": log_line},
                timeout=30
            )
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            return {'error': 'Analysis request timed out'}
    
    def analyze_batch(self, log_lines: List[str]) -> Dict[str, Any]:
        """Analyze multiple log lines"""
        try:
            response = requests.post(
                f"{self.base_url}/api/analyze/batch",
                json={"log_lines": log_lines},
                timeout=60
            )
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            return {'error': 'Batch analysis request timed out'}
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        try:
            response = requests.get(f"{self.base_url}/api/dashboard", timeout=10)
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            return {'error': 'Dashboard request timed out'}
    
    def get_container_details(self, container_no: str) -> Dict[str, Any]:
        """Get detailed information about a container"""
        try:
            response = requests.post(
                f"{self.base_url}/api/container/details",
                json={"container_no": container_no},
                timeout=10
            )
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            return {'error': 'Container details request timed out'}
    
    def get_all_containers(self) -> Dict[str, Any]:
        """Get all containers status"""
        try:
            response = requests.get(f"{self.base_url}/api/containers/status", timeout=10)
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            return {'error': 'Containers request timed out'}
    
    def get_edi_errors(self, limit: int = 20) -> Dict[str, Any]:
        """Get recent EDI errors"""
        try:
            response = requests.get(
                f"{self.base_url}/api/edi/errors",
                params={"limit": limit},
                timeout=10
            )
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            return {'error': 'EDI errors request timed out'}
    
    def upload_log_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Upload and analyze a log file"""
        try:
            files = {'file': (filename, file_content)}
            response = requests.post(
                f"{self.base_url}/api/upload/logs",
                files=files,
                timeout=120
            )
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            return {'error': 'File upload request timed out'}
    
    def search_incidents(self, pattern: str) -> Dict[str, Any]:
        """Search for incidents by pattern"""
        try:
            response = requests.get(
                f"{self.base_url}/api/search",
                params={"pattern": pattern},
                timeout=10
            )
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            return {'error': 'Search request timed out'}


# Cached API client instance
@st.cache_resource
def get_api_client() -> APIClient:
    """Get cached API client instance"""
    return APIClient()


def check_backend_connection() -> bool:
    """Check if backend is available and show status"""
    client = get_api_client()
    health = client.health_check()
    
    if 'error' in health:
        st.error(f"⚠️ Backend Offline: {health['error']}")
        st.info("Please start the FastAPI backend: `cd portnet/backend/api && uvicorn main:app --reload`")
        return False
    
    st.success(f"✅ Backend Connected: {health.get('api', 'unknown')} | DB: {health.get('database', 'unknown')}")
    return True

