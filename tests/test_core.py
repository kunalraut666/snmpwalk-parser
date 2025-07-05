#!/usr/bin/env python3
"""
Usage examples and test cases for the enhanced SNMP parser package.
"""

from snmpwalk_parser.core import SNMPParser
from snmpwalk_parser.snmp_runner import SNMPRunner
from snmpwalk_parser.models import SNMPWalkResult
import json

def example_basic_usage():
    """Basic usage example."""
    print("=== Basic Usage Example ===")
    
    # Sample SNMP walk output
    sample_output = """
    SNMPv2-MIB::sysDescr.0 = STRING: Linux router 5.4.0-74-generic
    SNMPv2-MIB::sysUpTime.0 = Timeticks: (12345678) 1 day, 10:17:36.78
    SNMPv2-MIB::sysContact.0 = STRING: admin@example.com
    SNMPv2-MIB::sysName.0 = STRING: router01
    SNMPv2-MIB::sysLocation.0 = STRING: Data Center Room A
    IF-MIB::ifDescr.1 = STRING: lo
    IF-MIB::ifDescr.2 = STRING: eth0
    IF-MIB::ifSpeed.1 = Gauge32: 10000000
    IF-MIB::ifSpeed.2 = Gauge32: 1000000000
    IF-MIB::ifOperStatus.1 = INTEGER: up(1)
    IF-MIB::ifOperStatus.2 = INTEGER: up(1)
    """
    
    # Parse the output
    parser = SNMPParser()
    entries = parser.parse_snmpwalk_output(sample_output)
    
    print(f"Parsed {len(entries)} entries:")
    for entry in entries[:3]:  # Show first 3
        print(f"  OID: {entry.oid}")
        print(f"  Key: {entry.key}")
        print(f"  Index: {entry.index}")
        print(f"  Type: {entry.type}")
        print(f"  Value: {entry.value}")
        print(f"  Raw: {entry.raw_value}")
        print()
    
    # Group by tables
    tables = parser.group_by_table(entries)
    print(f"Found {len(tables)} tables:")
    for table_name, table in tables.items():
        print(f"  {table_name}: {len(table)} entries")
    
    # Extract system info
    system_info = parser.get_system_info(entries)
    print(f"\nSystem Info:")
    for key, value in system_info.items():
        print(f"  {key}: {value}")

def example_advanced_parsing():
    """Advanced parsing example with different OID formats."""
    print("\n=== Advanced Parsing Example ===")
    
    # Mixed format SNMP output
    mixed_output = """
    .1.3.6.1.2.1.1.1.0 = STRING: "Cisco IOS Software"
    iso.3.6.1.2.1.1.2.0 = OID: .1.3.6.1.4.1.9.1.1
    enterprises.9.9.48.1.1.1.5.1 = Counter32: 1234567890
    SNMPv2-MIB::sysObjectID.0 = OID: SNMPv2-SMI::enterprises.9.1.1
    HOST-RESOURCES-MIB::hrSystemUptime.0 = Timeticks: (987654321) 114 days, 5:29:03.21
    """
    
    parser = SNMPParser()
    entries = parser.parse_snmpwalk_output(mixed_output)
    
    print(f"Parsed {len(entries)} entries with mixed formats:")
    for entry in entries:
        print(f"  {entry.oid} = {entry.type}: {entry.value}")
        print(f"    Key: {entry.key}, Index: {entry.index}")
        print()

def example_snmp_runner():
    """SNMP runner example (requires actual SNMP target)."""
    print("\n=== SNMP Runner Example ===")
    
    # Initialize runner
    runner = SNMPRunner(timeout=10, retries=2)
    
    # Example target - replace with actual SNMP-enabled device
    target_host = "192.168.1.1"  # Replace with real IP
    community = "public"
    
    try:
        # Run SNMP walk
        result = runner.run_snmpwalk(
            host=target_host,
            community=community,
            oid="1.3.6.1.2.1.1"  # System MIB
        )
        
        print(f"SNMP walk results for {target_host}:")
        print(f"  Total entries: {result.get_entry_count()}")
        print(f"  Total tables: {result.get_table_count()}")
        print(f"  Tables: {', '.join(result.get_table_names())}")
        
        # Show system info
        if result.system_info:
            print(f"\nSystem Information:")
            for key, value in result.system_info.items():
                print(f"  {key}: {value}")
        
        # Export to file
        result.export_to_file("snmp_result.json", "json")
        print("\nResults exported to snmp_result.json")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This example requires a real SNMP-enabled device.")

def example_parallel_queries():
    """Parallel SNMP queries example."""
    print("\n=== Parallel Queries Example ===")
    
    runner = SNMPRunner()
    
    # Example hosts - replace with actual SNMP-enabled devices
    hosts = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
    
    try:
        results = runner.run_parallel_snmpwalk(
            hosts=hosts,
            community="public",
            oid="1.3.6.1.2.1.1.1.0",  # sysDescr
            max_workers=5
        )
        
        print(f"Parallel query results for {len(hosts)} hosts:")
        for host, result in results.items():
            if isinstance(result, SNMPWalkResult):
                print(f"  {host}: {result.get_entry_count()} entries")
                if result.system_info:
                    desc = result.system_info.get('system_description', 'N/A')
                    print(f"    Description: {desc}")
            else:
                print(f"  {host}: Error - {result.message}")
    
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This example requires real SNMP-enabled devices.")

def example_filtering_and_analysis():
    """Example of filtering and analyzing SNMP data."""
    print("\n=== Filtering and Analysis Example ===")
    
    # Sample interface data
    interface_data = """
    IF-MIB::ifIndex.1 = INTEGER: 1
    IF-MIB::ifIndex.2 = INTEGER: 2
    IF-MIB::ifIndex.3 = INTEGER: 3
    IF-MIB::ifDescr.1 = STRING: lo
    IF-MIB::ifDescr.2 = STRING: eth0
    IF-MIB::ifDescr.3 = STRING: wlan0
    IF-MIB::ifType.1 = INTEGER: softwareLoopback(24)
    IF-MIB::ifType.2 = INTEGER: ethernetCsmacd(6)
    IF-MIB::ifType.3 = INTEGER: ieee80211(71)
    IF-MIB::ifSpeed.1 = Gauge32: 10000000
    IF-MIB::ifSpeed.2 = Gauge32: 1000000000
    IF-MIB::ifSpeed.3 = Gauge32: 54000000
    IF-MIB::ifOperStatus.1 = INTEGER: up(1)
    IF-MIB::ifOperStatus.2 = INTEGER: up(1)
    IF-MIB::ifOperStatus.3 = INTEGER: down(2)
    IF-MIB::ifInOctets.1 = Counter32: 1000000
    IF-MIB::ifInOctets.2 = Counter32: 500000000
    IF-MIB::ifInOctets.3 = Counter32: 0
    IF-MIB::ifOutOctets.1 = Counter32: 1000000
    IF-MIB::ifOutOctets.2 = Counter32: 400000000
    IF-MIB::ifOutOctets.3 = Counter32: 0
    """
    
    parser = SNMPParser()
    entries = parser.parse_snmpwalk_output(interface_data)
    
    print(f"Total entries: {len(entries)}")
    
    # Filter by OID pattern
    speed_entries = parser.filter_by_oid_pattern(entries, r'ifSpeed')
    print(f"Speed entries: {len(speed_entries)}")
    
    # Group by table
    tables = parser.group_by_table(entries)
    
    # Analyze interface table
    if_table = tables.get('ifDescr')
    if if_table:
        print(f"\nInterface descriptions ({len(if_table)} entries):")
        for entry in if_table:
            print(f"  Interface {entry.index}: {entry.value}")
    
    # Extract interface info
    interface_info = parser.get_interface_info(entries)
    print(f"\nInterface summary:")
    for iface in interface_info:
        print(f"  Interface {iface['index']}: {iface.get('description', 'N/A')}")
        if 'speed' in iface:
            speed_mbps = int(iface['speed']) / 1000000
            print(f"    Speed: {speed_mbps} Mbps")
        if 'status' in iface:
            print(f"    Status: {iface['status']}")

def example_data_export():
    """Example of exporting data in different formats."""
    print("\n=== Data Export Example ===")
    
    # Create sample result
    result = SNMPWalkResult(
        host="192.168.1.1",
        community="public",
        oid="1.3.6.1.2.1.1"
    )
    
    # Add some sample entries
    from snmpwalk_parser.models import SNMPEntry
    
    entries = [
        SNMPEntry("sysDescr.0", "sysDescr", "0", "STRING", "Linux Router"),
        SNMPEntry("sysUpTime.0", "sysUpTime", "0", "TIMETICKS", 
                 {"ticks": 12345678, "time_string": "1 day, 10:17:36.78", "seconds": 123456.78}),
        SNMPEntry("sysContact.0", "sysContact", "0", "STRING", "admin@example.com"),
    ]
    
    for entry in entries:
        result.add_entry(entry)
    
    # Export to JSON
    with open("example_output.json", "w") as f:
        f.write(result.to_json())
    print("Exported to example_output.json")
    
    # Export to CSV
    result.export_to_file("example_output.csv", "csv")
    print("Exported to example_output.csv")
    
    # Show summary
    summary = result.get_summary()
    print(f"\nSummary:")
    print(f"  Host: {summary['host']}")
    print(f"  Entries: {summary['total_entries']}")
    print(f"  Tables: {summary['total_tables']}")
    print(f"  Types: {summary['entry_types']}")

def example_error_handling():
    """Example of error handling and validation."""
    print("\n=== Error Handling Example ===")
    
    runner = SNMPRunner()
    
    # Test various error conditions
    test_cases = [
        ("", "public", "Invalid host"),
        ("192.168.1.1", "", "Invalid community"),
        ("192.168.1.1", "public", "Invalid version"),
        ("invalid-ip-address", "public", "Invalid IP format"),
    ]
    
    for i, (host, community, description) in enumerate(test_cases[:3]):  # Test first 3
        try:
            if i == 2:  # Test invalid version
                result = runner.run_snmpwalk(host, community, version="invalid")
            else:
                result = runner.run_snmpwalk(host, community)
            print(f"  {description}: Unexpected success")
        except Exception as e:
            print(f"  {description}: Caught expected error - {e}")

def run_all_examples():
    """Run all examples."""
    print("SNMP Parser Package - Usage Examples")
    print("=" * 50)
    
    example_basic_usage()
    example_advanced_parsing()
    example_filtering_and_analysis()
    example_data_export()
    example_error_handling()
    
    # These require actual SNMP devices
    print("\n" + "=" * 50)
    print("NOTE: The following examples require actual SNMP-enabled devices:")
    print("- example_snmp_runner()")
    print("- example_parallel_queries()")
    print("Replace IP addresses with real SNMP targets to test.")

if __name__ == "__main__":
    run_all_examples()