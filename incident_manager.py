#!/usr/bin/env python3
"""
PORTNET AI Incident Management System
=====================================

Main orchestrator for Level 2 Operations AI - integrates all components:
- Log file monitoring and parsing
- Database state correlation
- RAG-based knowledge retrieval
- AI-powered root cause analysis
- Escalation recommendations
- Auto-generated incident summaries
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

# Add backend modules to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.core.analyzer import IncidentAnalyzer, LogParser
from backend.db.connector import get_db
from backend.ai.retriever import Retriever
from backend.ai.generator import generate_answer, make_prompt

class SeverityLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM" 
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class IncidentStatus(Enum):
    NEW = "NEW"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"

@dataclass
class IncidentTicket:
    """Structured incident ticket"""
    ticket_id: str
    timestamp: datetime
    severity: SeverityLevel
    status: IncidentStatus
    source_log: str
    raw_log_line: str
    
    # Analysis results
    root_cause: Optional[str] = None
    technical_details: Optional[str] = None
    immediate_actions: List[str] = None
    business_impact: Optional[str] = None
    escalation_target: Optional[str] = None
    confidence: Optional[str] = None
    
    # Context
    affected_containers: List[str] = None
    affected_vessels: List[str] = None
    related_systems: List[str] = None
    
    # Timing
    time_to_detect: Optional[float] = None
    time_to_analyze: Optional[float] = None
    
    def __post_init__(self):
        if self.immediate_actions is None:
            self.immediate_actions = []
        if self.affected_containers is None:
            self.affected_containers = []
        if self.affected_vessels is None:
            self.affected_vessels = []
        if self.related_systems is None:
            self.related_systems = []


class PortnetIncidentManager:
    """
    Main AI-powered incident management system for PORTNET
    """
    
    def __init__(self):
        print("🚢 Initializing PORTNET AI Incident Management System...")
        
        # Initialize components
        self.analyzer = IncidentAnalyzer()
        self.db = get_db()
        self.parser = LogParser()
        
        # Configuration
        self.log_directory = Path(__file__).parent / "data" / "logs"
        self.tickets = {}  # ticket_id -> IncidentTicket
        self.auto_escalate_threshold = timedelta(minutes=30)
        
        # Escalation contacts
        self.escalation_contacts = {
            "EDI_SPECIALIST": "Level 3 EDI Support Team",
            "DATABASE_ADMIN": "Database Operations Team",
            "NETWORK_TEAM": "Network Infrastructure Team", 
            "VESSEL_OPERATIONS": "Vessel Operations Manager",
            "DUTY_MANAGER": "Duty Operations Manager"
        }
        
        print("✅ PORTNET AI System initialized successfully")
    
    def monitor_logs(self, duration_minutes: int = 5) -> List[IncidentTicket]:
        """
        Monitor log files for new incidents
        """
        print(f"\n🔍 Monitoring logs for {duration_minutes} minutes...")
        
        discovered_incidents = []
        log_files = list(self.log_directory.glob("*.log"))
        
        for log_file in log_files:
            print(f"   Scanning {log_file.name}...")
            
            try:
                incidents = self._scan_log_file(log_file)
                discovered_incidents.extend(incidents)
                print(f"   Found {len(incidents)} incidents in {log_file.name}")
                
            except Exception as e:
                print(f"   ⚠️ Error scanning {log_file.name}: {e}")
        
        print(f"📊 Total incidents discovered: {len(discovered_incidents)}")
        return discovered_incidents
    
    def _scan_log_file(self, log_file: Path) -> List[IncidentTicket]:
        """Scan a single log file for incidents"""
        incidents = []
        
        try:
            with open(log_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Use the log parser to check if this is an incident
                    parsed_incident = self.parser.parse_log_line(line)
                    if parsed_incident:
                        ticket = self._create_incident_ticket(
                            log_file.name, line, parsed_incident, line_num
                        )
                        incidents.append(ticket)
                        
        except Exception as e:
            print(f"Error reading {log_file}: {e}")
        
        return incidents
    
    def _create_incident_ticket(self, source_log: str, log_line: str, 
                               parsed_incident: Dict, line_num: int) -> IncidentTicket:
        """Create a structured incident ticket"""
        
        ticket_id = f"INC-{int(time.time())}-{line_num}"
        
        # Map severity
        severity_map = {
            'LOW': SeverityLevel.LOW,
            'MEDIUM': SeverityLevel.MEDIUM,
            'HIGH': SeverityLevel.HIGH
        }
        severity = severity_map.get(parsed_incident.get('severity', 'MEDIUM'), SeverityLevel.MEDIUM)
        
        # Extract timestamp
        timestamp_str = parsed_incident.get('timestamp')
        if timestamp_str:
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            except:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()
        
        ticket = IncidentTicket(
            ticket_id=ticket_id,
            timestamp=timestamp,
            severity=severity,
            status=IncidentStatus.NEW,
            source_log=source_log,
            raw_log_line=log_line,
            affected_containers=parsed_incident['entities'].get('containers', []),
            affected_vessels=parsed_incident['entities'].get('vessels', []),
            related_systems=parsed_incident['entities'].get('message_types', [])
        )
        
        return ticket
    
    def analyze_incident(self, ticket: IncidentTicket) -> IncidentTicket:
        """
        Perform comprehensive AI analysis of an incident
        """
        print(f"\n🔬 Analyzing incident {ticket.ticket_id}...")
        start_time = time.time()
        
        ticket.status = IncidentStatus.INVESTIGATING
        
        try:
            # Get full analysis from the analyzer
            analysis_result = self.analyzer.analyze_log_line(ticket.raw_log_line)
            
            if 'error' in analysis_result:
                print(f"   ⚠️ Analysis error: {analysis_result['error']}")
                ticket.root_cause = "Analysis failed - manual investigation required"
                ticket.confidence = "LOW"
            else:
                # Extract analysis details
                analysis = analysis_result.get('analysis', {})
                
                ticket.root_cause = analysis.get('root_cause', '')
                ticket.technical_details = analysis.get('technical_details', '')
                ticket.immediate_actions = analysis.get('immediate_actions', [])
                ticket.business_impact = analysis.get('business_impact', '')
                ticket.escalation_target = analysis.get('escalation', '')
                ticket.confidence = analysis.get('confidence', 'MEDIUM')
                
                # Update severity based on analysis
                if ticket.confidence == 'HIGH' and 'CRITICAL' in analysis.get('business_impact', '').upper():
                    ticket.severity = SeverityLevel.CRITICAL
                elif 'timeout' in ticket.root_cause.lower() or 'error' in ticket.root_cause.lower():
                    if ticket.severity == SeverityLevel.MEDIUM:
                        ticket.severity = SeverityLevel.HIGH
            
            ticket.time_to_analyze = time.time() - start_time
            ticket.status = IncidentStatus.RESOLVED if ticket.confidence == 'HIGH' else IncidentStatus.INVESTIGATING
            
            print(f"   ✅ Analysis complete ({ticket.time_to_analyze:.2f}s)")
            print(f"   Root cause: {ticket.root_cause}")
            print(f"   Confidence: {ticket.confidence}")
            
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            ticket.root_cause = f"Analysis system error: {str(e)}"
            ticket.confidence = "LOW"
            ticket.escalation_target = "DUTY_MANAGER"
        
        return ticket
    
    def generate_escalation_summary(self, ticket: IncidentTicket) -> str:
        """
        Generate escalation summary for management
        """
        print(f"📋 Generating escalation summary for {ticket.ticket_id}...")
        
        context = {
            "cases": [],
            "knowledge": []
        }
        
        # Try to get related context for escalation
        try:
            if ticket.root_cause:
                retriever = Retriever()
                search_results = retriever.search(ticket.root_cause, top_k=2)
                context = search_results
        except Exception as e:
            print(f"   ⚠️ Could not retrieve context: {e}")
        
        escalation_prompt = f"""Generate a concise escalation summary for PORTNET Operations Management.

INCIDENT DETAILS:
- Ticket ID: {ticket.ticket_id}
- Timestamp: {ticket.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
- Severity: {ticket.severity.value}
- Source: {ticket.source_log}
- Affected Containers: {', '.join(ticket.affected_containers) or 'None'}
- Affected Vessels: {', '.join(ticket.affected_vessels) or 'None'}

ANALYSIS:
- Root Cause: {ticket.root_cause or 'Under investigation'}
- Business Impact: {ticket.business_impact or 'Assessment pending'}
- AI Confidence: {ticket.confidence or 'UNKNOWN'}

ACTIONS TAKEN:
{chr(10).join(f'- {action}' for action in ticket.immediate_actions) if ticket.immediate_actions else '- Analysis in progress'}

Generate a 3-4 sentence executive summary suitable for operations management escalation.
Focus on business impact, timeline, and next steps.
"""
        
        try:
            summary = generate_answer(escalation_prompt)
            print(f"   ✅ Escalation summary generated")
            return summary
        except Exception as e:
            print(f"   ⚠️ Could not generate AI summary: {e}")
            return f"""
ESCALATION REQUIRED - {ticket.ticket_id}
Severity: {ticket.severity.value} | Time: {ticket.timestamp.strftime('%H:%M')}
Issue: {ticket.root_cause or 'System incident detected'}
Impact: {ticket.business_impact or 'Potential service disruption'}
Recommend: Immediate Level 3 investigation required
            """.strip()
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get dashboard data for operations center
        """
        print("\n📊 Generating dashboard data...")
        
        try:
            # Get database statistics
            db_stats = self.analyzer.get_dashboard_stats()
            
            # Count tickets by status
            ticket_counts = {
                'NEW': 0,
                'INVESTIGATING': 0, 
                'RESOLVED': 0,
                'ESCALATED': 0
            }
            
            for ticket in self.tickets.values():
                ticket_counts[ticket.status.value] += 1
            
            # Recent incidents summary
            recent_tickets = sorted(
                self.tickets.values(), 
                key=lambda t: t.timestamp,
                reverse=True
            )[:5]
            
            dashboard = {
                'timestamp': datetime.now().isoformat(),
                'system_status': 'OPERATIONAL',
                'active_incidents': ticket_counts,
                'database_stats': db_stats,
                'recent_incidents': [
                    {
                        'ticket_id': t.ticket_id,
                        'severity': t.severity.value,
                        'status': t.status.value,
                        'root_cause': t.root_cause or 'Analyzing...',
                        'timestamp': t.timestamp.isoformat()
                    }
                    for t in recent_tickets
                ],
                'system_health': {
                    'edi_error_rate': len(db_stats.get('recent_edi_errors', [])),
                    'containers_monitored': sum(db_stats.get('container_status_summary', {}).values()),
                    'analysis_system': 'ONLINE',
                    'knowledge_base': 'ONLINE'
                }
            }
            
            print(f"   ✅ Dashboard data prepared")
            return dashboard
            
        except Exception as e:
            print(f"   ⚠️ Dashboard generation error: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'system_status': 'DEGRADED',
                'error': str(e)
            }
    
    def run_incident_response_cycle(self, duration_minutes: int = 10) -> Dict[str, Any]:
        """
        Run a complete incident response cycle
        """
        print(f"\n🚨 Starting PORTNET AI Incident Response Cycle ({duration_minutes}min)")
        print("=" * 60)
        
        cycle_start = time.time()
        
        # Step 1: Monitor and discover incidents
        discovered_incidents = self.monitor_logs(duration_minutes)
        
        # Step 2: Analyze each incident
        analyzed_tickets = []
        for incident in discovered_incidents:
            analyzed_ticket = self.analyze_incident(incident)
            self.tickets[analyzed_ticket.ticket_id] = analyzed_ticket
            analyzed_tickets.append(analyzed_ticket)
        
        # Step 3: Generate escalations for critical/high severity incidents
        escalations = []
        for ticket in analyzed_tickets:
            if ticket.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
                escalation = self.generate_escalation_summary(ticket)
                escalations.append({
                    'ticket_id': ticket.ticket_id,
                    'summary': escalation,
                    'target': self.escalation_contacts.get(
                        ticket.escalation_target, 
                        "DUTY_MANAGER"
                    )
                })
        
        # Step 4: Generate dashboard
        dashboard = self.get_dashboard_data()
        
        cycle_time = time.time() - cycle_start
        
        # Summary report
        summary = {
            'cycle_duration': cycle_time,
            'incidents_discovered': len(discovered_incidents),
            'incidents_analyzed': len(analyzed_tickets),
            'escalations_generated': len(escalations),
            'tickets': [asdict(ticket) for ticket in analyzed_tickets],
            'escalations': escalations,
            'dashboard': dashboard
        }
        
        print(f"\n📈 CYCLE COMPLETE")
        print(f"   Duration: {cycle_time:.2f}s")
        print(f"   Incidents: {len(discovered_incidents)} discovered, {len(analyzed_tickets)} analyzed")
        print(f"   Escalations: {len(escalations)} generated")
        print(f"   System Status: {dashboard.get('system_status', 'UNKNOWN')}")
        
        return summary
    
    def generate_incident_report(self, ticket_ids: List[str] = None) -> str:
        """
        Generate comprehensive incident report
        """
        if ticket_ids:
            tickets = [self.tickets[tid] for tid in ticket_ids if tid in self.tickets]
        else:
            tickets = list(self.tickets.values())
        
        if not tickets:
            return "No incidents to report"
        
        # Sort by severity and timestamp
        tickets.sort(key=lambda t: (t.severity.value, t.timestamp), reverse=True)
        
        report = f"""
PORTNET AI INCIDENT MANAGEMENT REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================

EXECUTIVE SUMMARY:
- Total Incidents: {len(tickets)}
- Critical: {sum(1 for t in tickets if t.severity == SeverityLevel.CRITICAL)}
- High: {sum(1 for t in tickets if t.severity == SeverityLevel.HIGH)}
- Medium: {sum(1 for t in tickets if t.severity == SeverityLevel.MEDIUM)}
- Low: {sum(1 for t in tickets if t.severity == SeverityLevel.LOW)}

DETAILED INCIDENTS:
"""
        
        for i, ticket in enumerate(tickets[:10], 1):  # Top 10 incidents
            report += f"""
{i}. {ticket.ticket_id} [{ticket.severity.value}]
   Time: {ticket.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
   Source: {ticket.source_log}
   Root Cause: {ticket.root_cause or 'Under investigation'}
   Impact: {ticket.business_impact or 'Assessment pending'}
   Status: {ticket.status.value}
   Confidence: {ticket.confidence or 'N/A'}
   Containers: {', '.join(ticket.affected_containers) or 'None'}
   Vessels: {', '.join(ticket.affected_vessels) or 'None'}
   
   Immediate Actions:
   {chr(10).join(f'   - {action}' for action in ticket.immediate_actions) if ticket.immediate_actions else '   - None specified'}
"""
        
        return report


def main():
    """Main entry point for incident management system"""
    manager = PortnetIncidentManager()
    
    # Run incident response cycle
    results = manager.run_incident_response_cycle(duration_minutes=5)
    
    # Generate report
    report = manager.generate_incident_report()
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save full results as JSON
    results_file = Path(f"incident_analysis_{timestamp}.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Save human-readable report
    report_file = Path(f"incident_report_{timestamp}.txt")
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n💾 Results saved:")
    print(f"   JSON data: {results_file}")
    print(f"   Report: {report_file}")
    
    return results


if __name__ == "__main__":
    main()
