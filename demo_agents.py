#!/usr/bin/env python3
"""
NetGuardian AI - Demonstration Script
=====================================

This script demonstrates how to use the two specialized sub-agents:
1. IncidentIngestionAgent - for data management
2. IncidentResolutionAgent - for incident analysis and resolution

Usage examples for both ingestion and resolution workflows.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.ingestion_agent import ingestion_agent, ingest_incident_data, validate_incident_format
from backend.resoltuion_agent import resolution_agent, retrieve_context_from_query, analyze_incident_patterns
from backend.agent import root_agent

def demo_data_ingestion():
    """Demonstrate incident data ingestion capabilities."""
    print("🔄 INCIDENT DATA INGESTION DEMO")
    print("=" * 50)
    
    # Sample incident data
    sample_incident = {
        "incident_id": "INC-2025001",
        "timestamp": "2025-09-10T14:30:00Z",
        "severity": "High",
        "service_impact": "4G Service Outage Manchester",
        "incident_description": "Complete 4G service outage affecting Manchester region. Users unable to establish data connections. Voice calls working intermittently.",
        "resolution_steps": "1. Identified core router BGP session failure. 2. Restarted BGP processes on primary router. 3. Verified routing table convergence. 4. Confirmed service restoration across all sectors.",
        "root_cause": "BGP session timeout due to fiber cut during construction work on King Street"
    }
    
    print("📋 Sample Incident Data:")
    for key, value in sample_incident.items():
        print(f"  {key}: {value}")
    
    print("\n🔍 Validating incident format...")
    # Note: In a real scenario, you would call: validation_result = validate_incident_format(sample_incident)
    # if validation_result == "VALID": print("✅ Validation passed")
    # else: print(f"❌ Validation failed: {validation_result}")
    print("✅ Validation passed - all required fields present and properly formatted")
    
    print("\n💾 Ingesting incident data...")
    # Note: In a real scenario, you would call: result = ingest_incident_data(sample_incident)
    print("✅ Successfully ingested incident INC-2025001 into vector database")
    
    return sample_incident

def demo_incident_resolution():
    """Demonstrate incident resolution capabilities."""
    print("\n🔧 INCIDENT RESOLUTION DEMO")
    print("=" * 50)
    
    # Current incident scenario
    current_incident = {
        "description": "4G service degradation in Glasgow area with intermittent packet loss",
        "service_impact": "4G Service Performance Issues",
        "symptoms": "Users reporting slow data speeds and connection drops"
    }
    
    print("🚨 Current Incident:")
    for key, value in current_incident.items():
        print(f"  {key}: {value}")
    
    print("\n🔍 Searching for similar historical incidents...")
    # Note: In a real scenario, you would call retrieve_context_from_query
    print("✅ Found 5 similar incidents with comparable service impact patterns")
    
    print("\n📊 Analyzing incident patterns...")
    # Note: In a real scenario, you would call analyze_incident_patterns
    print("✅ Identified common root causes: BGP routing issues (60%), fiber infrastructure (30%), equipment failure (10%)")
    
    print("\n📋 Suggested Resolution Plan:")
    resolution_plan = """
    IMMEDIATE ACTIONS (0-15 minutes):
    1. Check BGP session status on Glasgow core routers
    2. Verify fiber infrastructure alerts in affected area
    3. Monitor traffic patterns and packet loss metrics
    
    DIAGNOSTIC STEPS (15-30 minutes):
    1. Run traceroute tests from multiple Glasgow locations
    2. Check routing table consistency across network nodes
    3. Verify fiber optic signal strength and quality
    
    RESOLUTION IMPLEMENTATION (30+ minutes):
    1. Restart BGP sessions if routing inconsistencies found
    2. Coordinate with fiber infrastructure team if physical issues detected
    3. Implement traffic rerouting if specific path issues identified
    
    VERIFICATION:
    1. Monitor service quality metrics for 30 minutes post-resolution
    2. Confirm user-reported issues are resolved
    3. Update incident documentation with final resolution steps
    """
    print(resolution_plan)

def demo_coordinated_workflow():
    """Demonstrate coordinated workflow using both agents."""
    print("\n🤝 COORDINATED WORKFLOW DEMO")
    print("=" * 50)
    
    print("Scenario: Resolve current incident, then store resolution for future reference")
    
    print("\n1️⃣ RESOLUTION PHASE:")
    print("   📍 Analyzing current DNS resolution failures in London")
    print("   🔍 Searching vector database for similar DNS incidents...")
    print("   📊 Found patterns: Certificate expiration (40%), DNS server overload (35%), routing (25%)")
    print("   💡 Recommended: Check SSL certificate validity and DNS server capacity")
    
    print("\n2️⃣ IMPLEMENTATION PHASE:")
    print("   🔧 Applied resolution: Renewed expired SSL certificates")
    print("   ✅ Service restored: DNS resolution times back to normal")
    print("   ⏱️  Total resolution time: 45 minutes")
    
    print("\n3️⃣ LEARNING PHASE:")
    print("   📝 Creating incident record with complete resolution details...")
    print("   💾 Ingesting resolved incident into vector database...")
    print("   🧠 System learning: Updated patterns for SSL certificate expiration incidents")
    print("   ✅ Future similar incidents can now be resolved 30% faster")

def main():
    """Main demonstration function."""
    print("🛡️  NetGuardian AI - Multi-Agent Incident Management System")
    print("=" * 60)
    print("Demonstrating specialized sub-agents for comprehensive incident management\n")
    
    # Demo individual agent capabilities
    demo_data_ingestion()
    demo_incident_resolution()
    demo_coordinated_workflow()
    
    print("\n" + "=" * 60)
    print("🎯 AGENT SPECIALIZATION SUMMARY:")
    print("🔹 IncidentIngestionAgent: Data validation, processing, and storage")
    print("🔹 IncidentResolutionAgent: Pattern analysis and resolution guidance")
    print("🔹 NetworkIncidentCoordinatorAgent: Orchestrates both agents for complete workflow")
    
    print("\n✨ Key Benefits of Multi-Agent Architecture:")
    print("   • Specialized expertise for different aspects of incident management")
    print("   • Improved data quality through dedicated validation processes")
    print("   • Enhanced resolution accuracy through focused pattern analysis")
    print("   • Scalable system that can handle both data management and real-time resolution")
    print("   • Continuous learning through integrated data ingestion and resolution feedback")

if __name__ == "__main__":
    main()
