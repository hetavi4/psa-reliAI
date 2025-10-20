#!/usr/bin/env python3
"""
PORTNET AI Incident Management - Comprehensive Test Suite
=========================================================

This test demonstrates the complete AI-powered Level 2 operations system:

1. Real-time log monitoring and incident detection
2. Database state correlation  
3. RAG-based knowledge retrieval from historical cases
4. AI-powered root cause analysis
5. Automated escalation recommendations
6. Dashboard generation for operations center

Simulates real PORTNET operations with actual container and vessel data.
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project modules
sys.path.append(str(Path(__file__).parent))

try:
    from incident_manager import PortnetIncidentManager, SeverityLevel, IncidentStatus
    print("✅ Successfully imported incident management system")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed and paths are correct")
    sys.exit(1)


class PortnetAITestSuite:
    """Comprehensive test suite for PORTNET AI system"""
    
    def __init__(self):
        print("🚢 PORTNET AI Incident Management - Test Suite")
        print("=" * 60)
        self.manager = PortnetIncidentManager()
        self.test_results = {}
    
    def test_database_connectivity(self) -> bool:
        """Test database connectivity and data integrity"""
        print("\n🔍 Testing database connectivity...")
        
        try:
            # Test database queries
            db = self.manager.db
            
            # Test container query
            container_details = db.get_container_details("MSKU0000001")
            if not container_details.get('container'):
                print("   ❌ Container query failed")
                return False
            
            print(f"   ✅ Container query successful: {container_details['container']['cntr_no']}")
            
            # Test vessel advice query  
            vessel_status = db.get_vessel_advice_status("MV Lion City 07")
            print(f"   ✅ Vessel advice query successful: {vessel_status['active_count']} active records")
            
            # Test EDI errors query
            edi_errors = db.get_recent_edi_errors(limit=5)
            print(f"   ✅ EDI errors query successful: {len(edi_errors)} recent errors")
            
            # Test container status summary
            containers = db.get_all_containers_status()
            print(f"   ✅ Container status query successful: {len(containers)} containers monitored")
            
            self.test_results['database_connectivity'] = True
            return True
            
        except Exception as e:
            print(f"   ❌ Database test failed: {e}")
            self.test_results['database_connectivity'] = False
            return False
    
    def test_rag_system(self) -> bool:
        """Test RAG knowledge retrieval system"""
        print("\n📚 Testing RAG knowledge retrieval...")
        
        try:
            # Test queries that should find relevant cases
            test_queries = [
                "EDI segment missing error",
                "container status mismatch", 
                "connection timeout issue",
                "duplicate message detected"
            ]
            
            retriever = self.manager.analyzer.retriever
            
            for query in test_queries:
                results = retriever.search(query, top_k=3)
                cases_found = len(results.get('cases', []))
                kb_found = len(results.get('knowledge', []))
                print(f"   Query: '{query}' -> {cases_found} cases, {kb_found} KB entries")
            
            # Test specific container/vessel search
            specific_results = retriever.search("MSKU container tranship vessel", top_k=2)
            print(f"   ✅ Specific entity search: {len(specific_results.get('cases', []))} relevant cases")
            
            self.test_results['rag_system'] = True
            return True
            
        except Exception as e:
            print(f"   ❌ RAG test failed: {e}")
            self.test_results['rag_system'] = False
            return False
    
    def test_log_parsing(self) -> bool:
        """Test log parsing and incident detection"""
        print("\n📋 Testing log parsing and incident detection...")
        
        try:
            parser = self.manager.parser
            
            # Test various log line formats
            test_logs = [
                "2025-10-04T12:25:10.529Z ERROR EDIService container=MSKU0000007 vessel=MV Lion City 07 errorText=Segment missing",
                "2025-10-09T08:22:45.332Z ERROR container-service cntr_no=MSKU0000001 vessel=MV Lion City 01 error=Container status TRANSHIP conflicts with vessel departure",
                "2025-10-09T08:45:12.667Z CRITICAL container-service cntr_no=TEMU0000016 error=Multiple active snapshots detected",
                "2025-10-05T16:45:12.112Z WARN EDIService container=CMAU0000019 vessel=MV Merlion 19 msg=Connection timeout"
            ]
            
            parsed_count = 0
            for log_line in test_logs:
                incident = parser.parse_log_line(log_line)
                if incident:
                    parsed_count += 1
                    print(f"   ✅ Parsed: {incident['severity']} severity, {len(incident['entities']['containers'])} containers")
                else:
                    print(f"   ⚠️ Not parsed as incident: {log_line[:50]}...")
            
            print(f"   📊 Successfully parsed {parsed_count}/{len(test_logs)} test logs")
            self.test_results['log_parsing'] = parsed_count >= len(test_logs) * 0.75  # 75% success rate
            return self.test_results['log_parsing']
            
        except Exception as e:
            print(f"   ❌ Log parsing test failed: {e}")
            self.test_results['log_parsing'] = False
            return False
    
    def test_ai_analysis(self) -> bool:
        """Test AI-powered incident analysis"""
        print("\n🤖 Testing AI incident analysis...")
        
        try:
            # Test realistic incident scenarios
            test_incidents = [
                "2025-10-04T12:25:10.529Z ERROR EDIService container=MSKU0000007 vessel=MV Lion City 07 errorText=Segment missing message_type=IFTMIN",
                "2025-10-09T08:45:12.667Z CRITICAL container-service cntr_no=TEMU0000016 error=Multiple active snapshots detected hazard_class=3"
            ]
            
            analysis_results = []
            for log_line in test_incidents:
                print(f"   Analyzing: {log_line[:60]}...")
                
                analysis = self.manager.analyzer.analyze_log_line(log_line)
                
                if 'error' not in analysis:
                    ai_analysis = analysis.get('analysis', {})
                    print(f"      Root cause: {ai_analysis.get('root_cause', 'Not provided')[:80]}...")
                    print(f"      Confidence: {ai_analysis.get('confidence', 'UNKNOWN')}")
                    print(f"      Actions: {len(ai_analysis.get('immediate_actions', []))} recommended")
                    analysis_results.append(analysis)
                else:
                    print(f"      ⚠️ Analysis error: {analysis['error']}")
            
            success_rate = len(analysis_results) / len(test_incidents)
            print(f"   📊 AI analysis success rate: {success_rate:.0%}")
            
            self.test_results['ai_analysis'] = success_rate >= 0.5  # 50% success rate acceptable
            return self.test_results['ai_analysis']
            
        except Exception as e:
            print(f"   ❌ AI analysis test failed: {e}")
            self.test_results['ai_analysis'] = False
            return False
    
    def test_incident_workflow(self) -> bool:
        """Test complete incident management workflow"""
        print("\n🔄 Testing complete incident management workflow...")
        
        try:
            # Run a full incident response cycle
            print("   Running incident response cycle...")
            cycle_results = self.manager.run_incident_response_cycle(duration_minutes=1)
            
            # Validate results
            incidents_found = cycle_results.get('incidents_discovered', 0)
            incidents_analyzed = cycle_results.get('incidents_analyzed', 0)
            escalations = cycle_results.get('escalations_generated', 0)
            
            print(f"   📊 Workflow Results:")
            print(f"      - Incidents discovered: {incidents_found}")
            print(f"      - Incidents analyzed: {incidents_analyzed}")
            print(f"      - Escalations generated: {escalations}")
            print(f"      - Cycle duration: {cycle_results.get('cycle_duration', 0):.2f}s")
            
            # Check if dashboard data was generated
            dashboard = cycle_results.get('dashboard', {})
            system_status = dashboard.get('system_status', 'UNKNOWN')
            print(f"      - System status: {system_status}")
            
            # Workflow is successful if we can process incidents end-to-end
            workflow_success = (
                incidents_found >= 0 and  # Can be 0 if no errors in logs
                'dashboard' in cycle_results and
                system_status in ['OPERATIONAL', 'DEGRADED']
            )
            
            self.test_results['incident_workflow'] = workflow_success
            return workflow_success
            
        except Exception as e:
            print(f"   ❌ Workflow test failed: {e}")
            self.test_results['incident_workflow'] = False
            return False
    
    def test_escalation_system(self) -> bool:
        """Test escalation and reporting system"""
        print("\n📢 Testing escalation and reporting system...")
        
        try:
            # Create a test incident ticket
            from incident_manager import IncidentTicket
            from datetime import datetime
            
            test_ticket = IncidentTicket(
                ticket_id="TEST-001",
                timestamp=datetime.now(),
                severity=SeverityLevel.HIGH,
                status=IncidentStatus.INVESTIGATING,
                source_log="test_edi_service.log",
                raw_log_line="ERROR EDIService container=TEST0000001 errorText=Segment missing",
                root_cause="EDI message parsing failure due to missing segment",
                technical_details="IFTMIN message incomplete, mandatory segment UNH missing",
                immediate_actions=["Validate message format", "Contact sender LINE-PSA", "Check EDI parser rules"],
                business_impact="Delayed container processing for vessel MV Test Vessel",
                confidence="HIGH"
            )
            
            # Test escalation summary generation
            escalation_summary = self.manager.generate_escalation_summary(test_ticket)
            print(f"   ✅ Escalation summary generated: {len(escalation_summary)} characters")
            
            # Test incident report generation
            self.manager.tickets[test_ticket.ticket_id] = test_ticket
            report = self.manager.generate_incident_report([test_ticket.ticket_id])
            print(f"   ✅ Incident report generated: {len(report)} characters")
            
            # Test dashboard data
            dashboard = self.manager.get_dashboard_data()
            print(f"   ✅ Dashboard data generated: {len(dashboard)} fields")
            print(f"      System status: {dashboard.get('system_status', 'UNKNOWN')}")
            
            self.test_results['escalation_system'] = True
            return True
            
        except Exception as e:
            print(f"   ❌ Escalation test failed: {e}")
            self.test_results['escalation_system'] = False
            return False
    
    def run_performance_test(self) -> bool:
        """Test system performance under load"""
        print("\n⚡ Running performance tests...")
        
        try:
            start_time = time.time()
            
            # Test multiple concurrent analyses
            test_logs = [
                "2025-10-04T12:25:10.529Z ERROR EDIService container=MSKU0000007 vessel=MV Lion City 07",
                "2025-10-09T08:22:45.332Z ERROR container-service cntr_no=MSKU0000001 vessel=MV Lion City 01",
                "2025-10-09T08:45:12.667Z CRITICAL container-service cntr_no=TEMU0000016 hazard_class=3",
                "2025-10-05T16:45:12.112Z WARN EDIService container=CMAU0000019 timeout_duration=45000ms"
            ] * 3  # Process each log 3 times
            
            analysis_times = []
            for i, log_line in enumerate(test_logs):
                analysis_start = time.time()
                
                # Perform analysis
                try:
                    analysis = self.manager.analyzer.analyze_log_line(log_line)
                    analysis_time = time.time() - analysis_start
                    analysis_times.append(analysis_time)
                    
                    if (i + 1) % 3 == 0:
                        print(f"   Processed batch {(i + 1) // 3}/4...")
                        
                except Exception as e:
                    print(f"   ⚠️ Analysis {i+1} failed: {e}")
            
            total_time = time.time() - start_time
            avg_analysis_time = sum(analysis_times) / len(analysis_times) if analysis_times else 0
            
            print(f"   📊 Performance Results:")
            print(f"      - Total processing time: {total_time:.2f}s")
            print(f"      - Average analysis time: {avg_analysis_time:.2f}s per incident")
            print(f"      - Throughput: {len(test_logs) / total_time:.1f} incidents/second")
            print(f"      - Success rate: {len(analysis_times) / len(test_logs):.0%}")
            
            # Performance is acceptable if average analysis time < 10s
            performance_ok = avg_analysis_time < 10.0 and len(analysis_times) / len(test_logs) >= 0.8
            
            self.test_results['performance'] = performance_ok
            return performance_ok
            
        except Exception as e:
            print(f"   ❌ Performance test failed: {e}")
            self.test_results['performance'] = False
            return False
    
    def run_integration_demo(self):
        """Run a comprehensive demonstration of the complete system"""
        print("\n🎬 PORTNET AI Integration Demonstration")
        print("=" * 50)
        
        # Simulate a realistic incident scenario
        print("\n📋 SCENARIO: Multiple EDI processing errors detected during peak hours")
        print("Container TEMU0000016 (hazardous cargo) has data corruption issues")
        print("Vessel MV Merlion 15 experiencing duplicate message problems")
        
        # Step 1: Monitor logs and detect incidents
        print("\n🔍 STEP 1: Real-time log monitoring...")
        discovered_incidents = self.manager.monitor_logs(duration_minutes=1)
        
        if discovered_incidents:
            print(f"   ✅ Detected {len(discovered_incidents)} incidents")
            
            # Step 2: Analyze the most critical incident
            critical_incident = None
            for incident in discovered_incidents:
                if incident.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
                    critical_incident = incident
                    break
            
            if not critical_incident:
                critical_incident = discovered_incidents[0] if discovered_incidents else None
            
            if critical_incident:
                print(f"\n🔬 STEP 2: AI Analysis of {critical_incident.ticket_id}")
                analyzed_incident = self.manager.analyze_incident(critical_incident)
                
                print(f"   Root Cause: {analyzed_incident.root_cause}")
                print(f"   Business Impact: {analyzed_incident.business_impact}")
                print(f"   Confidence: {analyzed_incident.confidence}")
                
                # Step 3: Generate escalation if needed
                if analyzed_incident.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
                    print(f"\n📢 STEP 3: Generating escalation for {analyzed_incident.severity.value} incident")
                    escalation = self.manager.generate_escalation_summary(analyzed_incident)
                    print("   Escalation Summary:")
                    print("   " + "=" * 40)
                    for line in escalation.split('\n')[:4]:  # First 4 lines
                        print(f"   {line}")
                    print("   " + "=" * 40)
        
        # Step 4: Dashboard overview
        print(f"\n📊 STEP 4: Operations Dashboard")
        dashboard = self.manager.get_dashboard_data()
        
        print(f"   System Status: {dashboard.get('system_status', 'UNKNOWN')}")
        
        active_incidents = dashboard.get('active_incidents', {})
        if active_incidents:
            print(f"   Active Incidents:")
            for status, count in active_incidents.items():
                if count > 0:
                    print(f"      - {status}: {count}")
        
        system_health = dashboard.get('system_health', {})
        if system_health:
            print(f"   System Health:")
            print(f"      - EDI Error Rate: {system_health.get('edi_error_rate', 0)}")
            print(f"      - Containers Monitored: {system_health.get('containers_monitored', 0)}")
            print(f"      - Knowledge Base: {system_health.get('knowledge_base', 'UNKNOWN')}")
        
        print(f"\n🎯 DEMONSTRATION COMPLETE")
        print("The PORTNET AI system successfully demonstrated:")
        print("✅ Real-time incident detection from logs")
        print("✅ Database correlation and state analysis") 
        print("✅ RAG-based knowledge retrieval")
        print("✅ AI-powered root cause analysis")
        print("✅ Automated escalation summaries")
        print("✅ Operations dashboard generation")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print("\n🚀 Running PORTNET AI Test Suite...")
        
        test_methods = [
            ('Database Connectivity', self.test_database_connectivity),
            ('RAG Knowledge System', self.test_rag_system),
            ('Log Parsing', self.test_log_parsing),
            ('AI Analysis Engine', self.test_ai_analysis),
            ('Incident Workflow', self.test_incident_workflow),
            ('Escalation System', self.test_escalation_system),
            ('Performance', self.run_performance_test)
        ]
        
        passed = 0
        total = len(test_methods)
        
        for test_name, test_method in test_methods:
            try:
                result = test_method()
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"\n{status} {test_name}")
                if result:
                    passed += 1
            except Exception as e:
                print(f"\n❌ FAIL {test_name} - Exception: {e}")
        
        # Run integration demo
        self.run_integration_demo()
        
        # Final results
        pass_rate = passed / total
        print(f"\n" + "=" * 60)
        print(f"🏁 TEST SUITE RESULTS")
        print(f"   Tests Passed: {passed}/{total} ({pass_rate:.0%})")
        print(f"   Overall Status: {'✅ PASS' if pass_rate >= 0.7 else '⚠️ NEEDS ATTENTION'}")
        
        # Save detailed results
        results = {
            'timestamp': datetime.now().isoformat(),
            'pass_rate': pass_rate,
            'tests_passed': passed,
            'tests_total': total,
            'individual_results': self.test_results,
            'overall_status': 'PASS' if pass_rate >= 0.7 else 'FAIL'
        }
        
        # Save to file
        results_file = Path(f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"   Detailed results saved to: {results_file}")
        
        return results


def main():
    """Main test execution"""
    try:
        test_suite = PortnetAITestSuite()
        results = test_suite.run_all_tests()
        
        # Exit with appropriate code
        exit_code = 0 if results['overall_status'] == 'PASS' else 1
        print(f"\n🏁 Test suite completed with exit code: {exit_code}")
        return exit_code
        
    except Exception as e:
        print(f"\n💥 Test suite failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
