#!/usr/bin/env python3
"""
Excel Data Ingestion Script for BigQuery Network Incident Agent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools import (
    check_table_exists,
    create_table_if_not_exists,
    ingest_excel_data,
    ingest_sample_data,
    get_incident_statistics
)

def setup_and_ingest():
    """Setup table and ingest data."""
    print("BigQuery Network Incidents - Table Setup and Data Ingestion")
    print("=" * 60)
    
    # Step 1: Check if table exists
    print("\n1. Checking if table exists...")
    try:
        exists = check_table_exists()
        if exists:
            print("✓ Table already exists")
        else:
            print("✗ Table does not exist")
    except Exception as e:
        print(f"❌ Error checking table: {e}")
        return False
    
    # Step 2: Create table if needed
    print("\n2. Creating table if necessary...")
    try:
        result = create_table_if_not_exists()
        print(f"✓ {result}")
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False
    
    # Step 3: Check for Excel file and ingest
    excel_file = "use_case_1_network_incident_logs.xlsx"
    print(f"\n3. Looking for Excel file: {excel_file}")
    
    if os.path.exists(excel_file):
        print(f"✓ Found Excel file: {excel_file}")
        try:
            result = ingest_excel_data(excel_file)
            print(f"✓ {result}")
        except Exception as e:
            print(f"❌ Error ingesting Excel data: {e}")
            # Fall back to sample data
            print("\n   Falling back to sample data...")
            try:
                result = ingest_sample_data()
                print(f"✓ {result}")
            except Exception as e:
                print(f"❌ Error ingesting sample data: {e}")
                return False
    else:
        print(f"✗ Excel file not found: {excel_file}")
        print("   Using sample data instead...")
        try:
            result = ingest_sample_data()
            print(f"✓ {result}")
        except Exception as e:
            print(f"❌ Error ingesting sample data: {e}")
            return False
    
    # Step 4: Verify the setup
    print("\n4. Verifying setup...")
    try:
        stats = get_incident_statistics()
        print(f"✓ Setup verification:")
        print(stats)
    except Exception as e:
        print(f"❌ Error verifying setup: {e}")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\nYour BigQuery table is ready with incident data.")
    print("You can now use the BigQuery agent to query and analyze incidents.")
    
    return True

if __name__ == "__main__":
    success = setup_and_ingest()
    
    if success:
        print("\n" + "=" * 60)
        print("Next steps:")
        print("1. Test queries using: python test.py")
        print("2. Use the agent in your application")
        print("3. The table structure is ready for additional data")
    else:
        print("\n❌ Setup failed. Please check your BigQuery permissions and try again.")
        sys.exit(1)