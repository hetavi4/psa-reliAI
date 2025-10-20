# backend/core/analyzer.py
"""
Main incident analyzer combining log parsing, DB queries, and RAG
"""
import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

import sys
from pathlib import Path
# Add parent directory to path to import ai modules
sys.path.append(str(Path(__file__).parent.parent))

from ai.retriever import Retriever
from ai.generator import generate_answer
from db.connector import get_db


class LogParser:
    """Parse log files to extract incidents"""
    
    @staticmethod
    def parse_log_line(log_line: str) -> Optional[Dict[str, Any]]:
        """Extract incident information from a log line"""
        
        # Skip if not an error/warning
        if not any(level in log_line.upper() for level in ['ERROR', 'WARN', 'CRITICAL']):
            return None
        
        incident = {
            'raw_log': log_line,
            'timestamp': None,
            'severity': 'MEDIUM',
            'entities': {
                'containers': [],
                'vessels': [],
                'message_types': [],
                'error_keywords': []
            }
        }
        
        # Extract timestamp
        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', log_line)
        if timestamp_match:
            incident['timestamp'] = timestamp_match.group(1)
        
        # Determine severity
        if 'ERROR' in log_line or 'CRITICAL' in log_line:
            incident['severity'] = 'HIGH'
        elif 'WARN' in log_line:
            incident['severity'] = 'MEDIUM'
        
        # Extract container numbers (4 letters + 7 digits)
        containers = re.findall(r'\b[A-Z]{4}\d{7}\b', log_line)
        incident['entities']['containers'] = list(set(containers))
        
        # Extract vessel names
        vessels = re.findall(r'MV [A-Za-z0-9 ]+\d+', log_line)
        incident['entities']['vessels'] = list(set(vessels))
        
        # Extract EDI message types
        for msg_type in ['COPARN', 'COARRI', 'CODECO', 'IFTMIN', 'IFTMCS']:
            if msg_type in log_line:
                incident['entities']['message_types'].append(msg_type)
        
        # Extract error keywords
        error_keywords = []
        if 'parse' in log_line.lower() or 'segment' in log_line.lower():
            error_keywords.append('PARSE_ERROR')
        if 'duplicate' in log_line.lower() or 'constraint' in log_line.lower():
            error_keywords.append('CONSTRAINT_VIOLATION')
        if 'timeout' in log_line.lower():
            error_keywords.append('TIMEOUT')
        if 'status' in log_line.lower() and 'mismatch' in log_line.lower():
            error_keywords.append('STATUS_MISMATCH')
        
        incident['entities']['error_keywords'] = error_keywords
        
        return incident


class IncidentAnalyzer:
    """Main analyzer combining all components"""
    
    def __init__(self):
        self.retriever = Retriever()
        self.db = get_db()
        self.parser = LogParser()
    
    def analyze_log_line(self, log_line: str) -> Dict[str, Any]:
        """Complete analysis pipeline for a single log line"""
        
        # Step 1: Parse log
        incident = self.parser.parse_log_line(log_line)
        if not incident:
            return {'error': 'Not an error/warning log line'}
        
        # Step 2: Query database for current state
        db_context = self._get_database_context(incident['entities'])
        
        # Step 3: Build RAG query and search knowledge base
        rag_query = self._build_rag_query(log_line, incident, db_context)
        kb_results = self.retriever.search(rag_query, top_k=3)
        
        # Step 4: Generate AI analysis
        analysis = self._generate_analysis(log_line, incident, db_context, kb_results)
        
        return {
            'incident': incident,
            'database_context': db_context,
            'knowledge_base_results': kb_results,
            'analysis': analysis
        }
    
    def _get_database_context(self, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """Query database for all entities found in log"""
        context = {}
        
        # Get container details
        for container_no in entities.get('containers', []):
            try:
                context[f'container_{container_no}'] = self.db.get_container_details(container_no)
            except Exception as e:
                context[f'container_{container_no}'] = {'error': str(e)}
        
        # Get vessel advice
        for vessel_name in entities.get('vessels', []):
            try:
                context[f'vessel_{vessel_name}'] = self.db.get_vessel_advice_status(vessel_name)
            except Exception as e:
                context[f'vessel_{vessel_name}'] = {'error': str(e)}
        
        return context
    
    def _build_rag_query(self, log_line: str, incident: Dict, db_context: Dict) -> str:
        """Build intelligent search query for knowledge base"""
        query_parts = []
        
        # Add error keywords
        query_parts.extend(incident['entities'].get('error_keywords', []))
        
        # Add message types
        query_parts.extend(incident['entities'].get('message_types', []))
        
        # Add specific error text from log
        if 'segment missing' in log_line.lower():
            query_parts.append('missing segment')
        if 'duplicate' in log_line.lower():
            query_parts.append('duplicate entry')
        if 'timeout' in log_line.lower():
            query_parts.append('connection timeout')
        
        # Add context from database if there are EDI errors
        for key, value in db_context.items():
            if 'container_' in key and isinstance(value, dict):
                if value.get('edi_errors_count', 0) > 0:
                    edi_msgs = value.get('edi_messages', [])
                    if edi_msgs:
                        error_msg = edi_msgs[0]
                        if error_msg.get('error_text'):
                            query_parts.append(error_msg['error_text'])
        
        return ' '.join(query_parts) if query_parts else log_line
    
    def _generate_analysis(self, log_line: str, incident: Dict, 
                          db_context: Dict, kb_results: Dict) -> Dict[str, Any]:
        """Generate AI-powered analysis using all context"""
        
        # Build comprehensive prompt
        prompt = self._build_analysis_prompt(log_line, incident, db_context, kb_results)
        
        # Get AI response
        try:
            ai_response = generate_answer(prompt)
            
            # Parse response into structured format
            analysis = self._parse_ai_response(ai_response)
            analysis['raw_response'] = ai_response
            
            return analysis
            
        except Exception as e:
            return {
                'error': f'AI analysis failed: {str(e)}',
                'fallback_analysis': self._fallback_analysis(incident, db_context)
            }
    
    def _build_analysis_prompt(self, log_line: str, incident: Dict,
                               db_context: Dict, kb_results: Dict) -> str:
        """Build comprehensive prompt for AI"""
        
        # Format database context
        db_summary = self._format_db_context(db_context)
        
        # Format KB results
        kb_summary = self._format_kb_results(kb_results)
        
        prompt = f"""You are a Level 2 operations engineer for PORTNET, Singapore's maritime port system.
Analyze this incident and provide actionable recommendations.

=== INCIDENT LOG ===
{log_line}

Timestamp: {incident.get('timestamp', 'Unknown')}
Severity: {incident['severity']}
Entities found:
- Containers: {', '.join(incident['entities'].get('containers', [])) or 'None'}
- Vessels: {', '.join(incident['entities'].get('vessels', [])) or 'None'}
- EDI Message Types: {', '.join(incident['entities'].get('message_types', [])) or 'None'}
- Error Keywords: {', '.join(incident['entities'].get('error_keywords', [])) or 'None'}

=== CURRENT SYSTEM STATE (Database) ===
{db_summary}

=== HISTORICAL KNOWLEDGE (Past Cases & KB) ===
{kb_summary}

=== REQUIRED OUTPUT ===
Provide your analysis in this exact format:

ROOT CAUSE:
[One clear sentence describing the root cause]

TECHNICAL DETAILS:
[2-3 sentences explaining what went wrong technically]

IMMEDIATE ACTIONS:
1. [First action with specific details]
2. [Second action with specific details]
3. [Third action if needed]

BUSINESS IMPACT:
[One sentence on operational impact]

ESCALATION:
[Who to escalate to if not resolved in 30 minutes]

CONFIDENCE:
[Your confidence level: HIGH/MEDIUM/LOW]
"""
        
        return prompt
    
    def _format_db_context(self, db_context: Dict) -> str:
        """Format database context for prompt"""
        if not db_context:
            return "No database context available."
        
        lines = []
        for key, value in db_context.items():
            if isinstance(value, dict) and 'error' in value:
                lines.append(f"{key}: {value['error']}")
                continue
            
            if 'container_' in key:
                container = value.get('container', {})
                if container:
                    lines.append(f"\nContainer {container.get('cntr_no')}:")
                    lines.append(f"  Status: {container.get('status')}")
                    lines.append(f"  Vessel: {container.get('vessel_name', 'N/A')}")
                    lines.append(f"  Route: {container.get('origin_port')} → {container.get('destination_port')}")
                    
                    edi_errors = value.get('edi_errors_count', 0)
                    if edi_errors > 0:
                        lines.append(f"  ⚠️ EDI Errors: {edi_errors} recent errors")
                        recent_error = value.get('edi_messages', [{}])[0]
                        if recent_error.get('error_text'):
                            lines.append(f"    Last error: {recent_error['error_text']}")
                    
                    recent_events = value.get('api_events', [])[:3]
                    if recent_events:
                        lines.append(f"  Recent events:")
                        for evt in recent_events:
                            lines.append(f"    - {evt.get('event_type')} at {evt.get('event_ts')}")
            
            elif 'vessel_' in key:
                lines.append(f"\n{key}:")
                lines.append(f"  Active advice records: {value.get('active_count', 0)}")
                if value.get('has_conflict'):
                    lines.append(f"  ⚠️ CONFLICT: Multiple active records detected!")
        
        return '\n'.join(lines) if lines else "No relevant database data found."
    
    def _format_kb_results(self, kb_results: Dict) -> str:
        """Format knowledge base results for prompt"""
        lines = []
        
        cases = kb_results.get('cases', [])
        if cases:
            lines.append("PAST CASES:")
            for i, case in enumerate(cases[:3], 1):
                lines.append(f"{i}. {case.get('text', '')[:200]}...")
                lines.append(f"   (Similarity: {case.get('_score', 0):.2f})")
        
        knowledge = kb_results.get('knowledge', [])
        if knowledge:
            lines.append("\nKNOWLEDGE BASE:")
            for i, kb in enumerate(knowledge[:3], 1):
                lines.append(f"{i}. {kb.get('text', '')[:200]}...")
                lines.append(f"   (Similarity: {kb.get('_score', 0):.2f})")
        
        return '\n'.join(lines) if lines else "No relevant historical knowledge found."
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        sections = {
            'root_cause': '',
            'technical_details': '',
            'immediate_actions': [],
            'business_impact': '',
            'escalation': '',
            'confidence': 'MEDIUM'
        }
        
        current_section = None
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Detect section headers
            if 'ROOT CAUSE:' in line.upper():
                current_section = 'root_cause'
                continue
            elif 'TECHNICAL DETAILS:' in line.upper():
                current_section = 'technical_details'
                continue
            elif 'IMMEDIATE ACTIONS:' in line.upper():
                current_section = 'immediate_actions'
                continue
            elif 'BUSINESS IMPACT:' in line.upper():
                current_section = 'business_impact'
                continue
            elif 'ESCALATION:' in line.upper():
                current_section = 'escalation'
                continue
            elif 'CONFIDENCE:' in line.upper():
                current_section = 'confidence'
                continue
            
            # Add content to current section
            if current_section and line:
                if current_section == 'immediate_actions':
                    # Extract numbered actions
                    action_match = re.match(r'^\d+\.\s*(.+)$', line)
                    if action_match:
                        sections['immediate_actions'].append(action_match.group(1))
                elif current_section == 'confidence':
                    # Extract confidence level
                    for level in ['HIGH', 'MEDIUM', 'LOW']:
                        if level in line.upper():
                            sections['confidence'] = level
                            break
                else:
                    # Add text to string sections
                    if sections[current_section]:
                        sections[current_section] += ' ' + line
                    else:
                        sections[current_section] = line
        
        return sections
    
    def _fallback_analysis(self, incident: Dict, db_context: Dict) -> Dict[str, Any]:
        """Provide basic analysis if AI fails"""
        return {
            'root_cause': f"Error detected: {', '.join(incident['entities'].get('error_keywords', ['Unknown']))}",
            'technical_details': 'AI analysis unavailable. Manual investigation required.',
            'immediate_actions': [
                'Check database state for affected entities',
                'Review recent EDI messages and API events',
                'Contact relevant stakeholders'
            ],
            'business_impact': 'Potential service disruption',
            'escalation': 'Escalate to Level 3 support',
            'confidence': 'LOW'
        }
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        try:
            return {
                'recent_edi_errors': self.db.get_recent_edi_errors(limit=10),
                'container_status_summary': self._get_status_summary()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_status_summary(self) -> Dict[str, int]:
        """Get container status summary"""
        try:
            containers = self.db.get_all_containers_status()
            summary = {}
            for container in containers:
                status = container.get('status', 'UNKNOWN')
                summary[status] = summary.get(status, 0) + 1
            return summary
        except Exception as e:
            return {'error': str(e)}