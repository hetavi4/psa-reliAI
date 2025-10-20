# backend/db/connector.py
"""
Database connector for querying operational state - SQLite version
"""
import sqlite3
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

# Database path relative to the project root
DB_PATH = Path(__file__).resolve().parents[2] / "portnet.db"


class DatabaseConnector:
    """Manages database connections and queries for incident correlation"""
    
    def __init__(self):
        self.db_path = str(DB_PATH)
        self.conn = None
    
    def connect(self):
        """Establish database connection"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable dict-like access
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute a query and return results as list of dicts"""
        self.connect()
        cursor = self.conn.cursor()
        
        # Convert MySQL style %s placeholders to SQLite ? placeholders
        query = query.replace('%s', '?')
        
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        
        # Convert sqlite3.Row objects to dictionaries
        results = []
        for row in rows:
            row_dict = dict(row)
            # Parse JSON fields if they exist
            for key, value in row_dict.items():
                if key == 'payload_json' and value:
                    try:
                        row_dict[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        pass  # Keep as string if not valid JSON
            results.append(row_dict)
        
        cursor.close()
        return results
    
    def get_container_details(self, container_no: str) -> Dict[str, Any]:
        """Get comprehensive container information"""
        result = {
            'container': None,
            'vessel': None,
            'edi_messages': [],
            'api_events': [],
            'edi_errors_count': 0
        }
        
        # Get latest container snapshot
        query = """
            SELECT 
                c.container_id, c.cntr_no, c.iso_code, c.size_type,
                c.gross_weight_kg, c.status, c.origin_port, 
                c.tranship_port, c.destination_port, c.hazard_class,
                c.vessel_id, c.eta_ts, c.etd_ts, c.last_free_day,
                v.vessel_name, v.imo_no, v.operator_name, v.flag_state
            FROM container c
            LEFT JOIN vessel v ON c.vessel_id = v.vessel_id
            WHERE c.cntr_no = %s
            ORDER BY c.created_at DESC
            LIMIT 1
        """
        containers = self.execute_query(query, (container_no,))
        if not containers:
            return result
        
        result['container'] = containers[0]
        container_id = result['container']['container_id']
        
        # Get vessel details if available
        if result['container']['vessel_id']:
            result['vessel'] = {
                'vessel_name': result['container']['vessel_name'],
                'imo_no': result['container']['imo_no'],
                'operator_name': result['container']['operator_name'],
                'flag_state': result['container']['flag_state']
            }
        
        # Get recent EDI messages
        edi_query = """
            SELECT 
                edi_id, message_type, direction, status,
                message_ref, sender, receiver, sent_at, 
                ack_at, error_text
            FROM edi_message
            WHERE container_id = %s
            ORDER BY sent_at DESC
            LIMIT 10
        """
        result['edi_messages'] = self.execute_query(edi_query, (container_id,))
        result['edi_errors_count'] = sum(1 for msg in result['edi_messages'] if msg['status'] == 'ERROR')
        
        # Get recent API events
        api_query = """
            SELECT 
                api_id, event_type, source_system, http_status,
                correlation_id, event_ts, payload_json
            FROM api_event
            WHERE container_id = %s
            ORDER BY event_ts DESC
            LIMIT 10
        """
        result['api_events'] = self.execute_query(api_query, (container_id,))
        
        return result
    
    def get_vessel_advice_status(self, vessel_name: str) -> Dict[str, Any]:
        """Get vessel advice information"""
        query = """
            SELECT 
                vessel_advice_no, vessel_name, system_vessel_name,
                effective_start_datetime, effective_end_datetime
            FROM vessel_advice
            WHERE system_vessel_name = %s
            ORDER BY effective_start_datetime DESC
            LIMIT 5
        """
        records = self.execute_query(query, (vessel_name,))
        
        active_records = [r for r in records if r['effective_end_datetime'] is None]
        
        return {
            'records': records,
            'active_count': len(active_records),
            'has_conflict': len(active_records) > 1
        }
    
    def get_all_containers_status(self) -> List[Dict]:
        """Get summary of all containers"""
        query = """
            SELECT 
                c.cntr_no, c.status, c.size_type,
                c.origin_port, c.destination_port,
                v.vessel_name, c.eta_ts, c.etd_ts
            FROM container c
            LEFT JOIN vessel v ON c.vessel_id = v.vessel_id
            ORDER BY c.created_at DESC
            LIMIT 50
        """
        return self.execute_query(query)
    
    def get_recent_edi_errors(self, limit: int = 20) -> List[Dict]:
        """Get recent EDI errors across all containers"""
        query = """
            SELECT 
                e.edi_id, e.message_type, e.error_text, e.sent_at,
                e.sender, e.receiver,
                c.cntr_no, v.vessel_name
            FROM edi_message e
            LEFT JOIN container c ON e.container_id = c.container_id
            LEFT JOIN vessel v ON e.vessel_id = v.vessel_id
            WHERE e.status = 'ERROR'
            ORDER BY e.sent_at DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))
    
    def search_incidents_by_pattern(self, pattern: str) -> List[Dict]:
        """Search for containers/vessels matching a pattern"""
        query = """
            SELECT 
                c.cntr_no, c.status, v.vessel_name,
                c.origin_port, c.destination_port
            FROM container c
            LEFT JOIN vessel v ON c.vessel_id = v.vessel_id
            WHERE c.cntr_no LIKE %s OR v.vessel_name LIKE %s
            ORDER BY c.created_at DESC
            LIMIT 20
        """
        search_pattern = f"%{pattern}%"
        return self.execute_query(query, (search_pattern, search_pattern))


# Singleton instance
_db_instance = None

def get_db() -> DatabaseConnector:
    """Get database connector singleton"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnector()
    return _db_instance