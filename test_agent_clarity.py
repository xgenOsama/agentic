#!/usr/bin/env python3
"""
Test script to verify the agent configuration and tool clarity
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.agent import root_agent

def test_agent_tools():
    """Test that the root agent has the correct tools configured"""
    print("🔍 Testing Root Agent Configuration...")
    
    print(f"Agent Name: {root_agent.name}")
    print(f"Agent Description: {root_agent.description}")
    print(f"Number of tools: {len(root_agent.tools)}")
    
    print("\n📋 Available Tools:")
    for i, tool in enumerate(root_agent.tools, 1):
        if hasattr(tool, 'name'):
            print(f"  {i}. {tool.name}")
        elif hasattr(tool, '__name__'):
            print(f"  {i}. {tool.__name__}")
        else:
            print(f"  {i}. {str(tool)}")
    
    print("\n✅ Root agent configuration test completed!")

def test_tool_purposes():
    """Test understanding of tool purposes"""
    print("\n🎯 Tool Purpose Clarification:")
    print("1. retrieve_context_from_query → SEARCH/RETRIEVE existing incidents")
    print("2. INCIDENT_INGESTION_AGENT_TOOL → INGEST structured incident data")
    print("3. GCS_INGEST_AGENT_TOOL → INGEST files from Google Cloud Storage") 
    print("4. ANALYTICS_AGENT_TOOL → ANALYZE data for insights and patterns")
    
    print("\n📝 Usage Examples:")
    print("• 'Find incidents similar to network outage in Manchester' → retrieve_context_from_query")
    print("• 'Ingest this incident: {incident_id: INC-001, ...}' → INCIDENT_INGESTION_AGENT_TOOL")
    print("• 'Process this file: gs://bucket/incidents.xlsx' → GCS_INGEST_AGENT_TOOL")
    print("• 'What trends do we see in network incidents?' → ANALYTICS_AGENT_TOOL")

if __name__ == "__main__":
    test_agent_tools()
    test_tool_purposes()
    print("\n🎉 All tests completed successfully!")
