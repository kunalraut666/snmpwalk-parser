"""
SNMP Parser CLI - Command Line Interface for SNMP operations
"""

import argparse
import sys
import json
import csv
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import your package modules
try:
    from snmpwalk_parser.snmp_runner import SNMPRunner
    from snmpwalk_parser.core import SNMPParser
    from snmpwalk_parser.models import SNMPWalkResult, SNMPError
except ImportError:
    # For development/testing
    from snmpwalk_parser.snmp_runner import SNMPRunner
    from snmpwalk_parser.core import SNMPParser
    from snmpwalk_parser.models import SNMPWalkResult, SNMPError


class SNMPCLIColors:
    """ANSI color codes for CLI output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class SNMPCLI:
    """Main CLI class for SNMP operations."""
    
    def __init__(self):
        self.runner = SNMPRunner()
        self.parser = SNMPParser()
        self.colors = SNMPCLIColors()
    
    def colorize(self, text: str, color: str) -> str:
        """Add color to text if stdout is a terminal."""
        if sys.stdout.isatty():
            return f"{color}{text}{self.colors.ENDC}"
        return text
    
    def print_header(self, text: str):
        """Print colored header."""
        print(self.colorize(f"\n{text}", self.colors.HEADER + self.colors.BOLD))
        print(self.colorize("=" * len(text), self.colors.HEADER))
    
    def print_success(self, text: str):
        """Print success message."""
        print(self.colorize(f"✓ {text}", self.colors.OKGREEN))
    
    def print_error(self, text: str):
        """Print error message."""
        print(self.colorize(f"✗ {text}", self.colors.FAIL), file=sys.stderr)
    
    def print_warning(self, text: str):
        """Print warning message."""
        print(self.colorize(f"⚠ {text}", self.colors.WARNING))
    
    def print_info(self, text: str):
        """Print info message."""
        print(self.colorize(f"ℹ {text}", self.colors.OKBLUE))


def create_parser():
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description='SNMP Parser CLI - Advanced SNMP operations toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic snmpwalk
  snmpwalk-parser walk 192.168.1.1 -c public

  # Walk specific OID
  snmpwalk-parser walk 192.168.1.1 -c public -o 1.3.6.1.2.1.1

  # Get specific OIDs
  snmpwalk-parser get 192.168.1.1 -c public -o sysDescr.0 sysName.0

  # Bulk walk for faster operations
  snmpwalk-parser bulk 192.168.1.1 -c public -o 1.3.6.1.2.1.2

  # Parse existing snmpwalk output
  snmpwalk-parser parse -f snmpwalk_output.txt

  # Discover SNMP hosts in network
  snmpwalk-parser discover 192.168.1.0/24 -c public

  # Parallel walk on multiple hosts
  snmpwalk-parser parallel -H 192.168.1.1 192.168.1.2 192.168.1.3 -c public

  # Export results to different formats
  snmpwalk-parser walk 192.168.1.1 -c public --output results.json --format json
  snmpwalk-parser walk 192.168.1.1 -c public --output results.csv --format csv
        """
    )
    
    # Global options
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Enable verbose output')
    parser.add_argument('--version', action='version', version='SNMP Parser CLI 1.0.0')
    parser.add_argument('--no-color', action='store_true', 
                       help='Disable colored output')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Walk command
    walk_parser = subparsers.add_parser('walk', help='Perform SNMP walk')
    walk_parser.add_argument('host', help='Target host (IP or hostname)')
    walk_parser.add_argument('-c', '--community', default='public', 
                           help='SNMP community string (default: public)')
    walk_parser.add_argument('-o', '--oid', default='', 
                           help='Starting OID (default: empty for full walk)')
    walk_parser.add_argument('-V', '--snmp-version', choices=['1', '2c', '3'], 
                           default='2c', help='SNMP version (default: 2c)')
    walk_parser.add_argument('-t', '--timeout', type=int, default=30, 
                           help='Timeout in seconds (default: 30)')
    walk_parser.add_argument('-r', '--retries', type=int, default=3, 
                           help='Number of retries (default: 3)')
    walk_parser.add_argument('--output', '-f', help='Output file path')
    walk_parser.add_argument('--format', choices=['json', 'csv', 'table'], 
                           default='table', help='Output format (default: table)')
    walk_parser.add_argument('--show-system', action='store_true', 
                           help='Show system information')
    walk_parser.add_argument('--show-interfaces', action='store_true', 
                           help='Show interface information')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Perform SNMP get')
    get_parser.add_argument('host', help='Target host (IP or hostname)')
    get_parser.add_argument('-c', '--community', default='public', 
                          help='SNMP community string')
    get_parser.add_argument('-o', '--oids', nargs='+', required=True, 
                          help='OIDs to retrieve')
    get_parser.add_argument('-V', '--snmp-version', choices=['1', '2c', '3'], 
                          default='2c', help='SNMP version')
    get_parser.add_argument('-t', '--timeout', type=int, default=30, 
                          help='Timeout in seconds')
    get_parser.add_argument('--output', '-f', help='Output file path')
    get_parser.add_argument('--format', choices=['json', 'csv', 'table'], 
                          default='table', help='Output format')
    
    # Bulk command
    bulk_parser = subparsers.add_parser('bulk', help='Perform SNMP bulk walk')
    bulk_parser.add_argument('host', help='Target host (IP or hostname)')
    bulk_parser.add_argument('-c', '--community', default='public', 
                           help='SNMP community string')
    bulk_parser.add_argument('-o', '--oid', default='', 
                           help='Starting OID')
    bulk_parser.add_argument('-V', '--snmp-version', choices=['2c', '3'], 
                           default='2c', help='SNMP version (bulk requires 2c or 3)')
    bulk_parser.add_argument('-m', '--max-repetitions', type=int, default=10, 
                           help='Max repetitions (default: 10)')
    bulk_parser.add_argument('-t', '--timeout', type=int, default=30, 
                           help='Timeout in seconds')
    bulk_parser.add_argument('--output', '-f', help='Output file path')
    bulk_parser.add_argument('--format', choices=['json', 'csv', 'table'], 
                           default='table', help='Output format')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse existing SNMP output')
    parse_parser.add_argument('-f', '--file', required=True, 
                            help='Input file containing SNMP output')
    parse_parser.add_argument('--output', help='Output file path')
    parse_parser.add_argument('--format', choices=['json', 'csv', 'table'], 
                            default='table', help='Output format')
    parse_parser.add_argument('--filter', help='Filter entries by OID pattern (regex)')
    parse_parser.add_argument('--show-system', action='store_true', 
                            help='Show system information')
    parse_parser.add_argument('--show-interfaces', action='store_true', 
                            help='Show interface information')
    
    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover SNMP hosts')
    discover_parser.add_argument('network', help='Network to scan (CIDR notation)')
    discover_parser.add_argument('-c', '--community', default='public', 
                               help='SNMP community string')
    discover_parser.add_argument('-t', '--timeout', type=int, default=5, 
                               help='Timeout per host (default: 5)')
    discover_parser.add_argument('--output', '-f', help='Output file path')
    discover_parser.add_argument('--format', choices=['json', 'table'], 
                               default='table', help='Output format')
    
    # Parallel command
    parallel_parser = subparsers.add_parser('parallel', help='Parallel SNMP operations')
    parallel_parser.add_argument('-H', '--hosts', nargs='+', required=True, 
                               help='List of hosts to query')
    parallel_parser.add_argument('-c', '--community', default='public', 
                               help='SNMP community string')
    parallel_parser.add_argument('-o', '--oid', default='', 
                               help='Starting OID')
    parallel_parser.add_argument('-V', '--snmp-version', choices=['1', '2c', '3'], 
                               default='2c', help='SNMP version')
    parallel_parser.add_argument('-w', '--workers', type=int, default=10, 
                               help='Number of parallel workers (default: 10)')
    parallel_parser.add_argument('--output', '-f', help='Output file path')
    parallel_parser.add_argument('--format', choices=['json', 'csv', 'table'], 
                               default='table', help='Output format')
    
    return parser


def format_table_output(entries: List, title: str = "SNMP Results"):
    """Format entries as a table."""
    if not entries:
        return "No data to display"
    
    # Determine if we have SNMPEntry objects or dictionaries
    if hasattr(entries[0], 'to_dict'):
        rows = [entry.to_dict() for entry in entries]
    else:
        rows = entries
    
    if not rows:
        return "No data to display"
    
    # Get headers
    headers = list(rows[0].keys())
    
    # Calculate column widths
    widths = {}
    for header in headers:
        widths[header] = len(header)
        for row in rows:
            widths[header] = max(widths[header], len(str(row.get(header, ''))))
    
    # Build table
    output = f"\n{title}\n"
    output += "=" * len(title) + "\n"
    
    # Header row
    header_row = " | ".join(header.ljust(widths[header]) for header in headers)
    output += header_row + "\n"
    output += "-" * len(header_row) + "\n"
    
    # Data rows
    for row in rows:
        data_row = " | ".join(str(row.get(header, '')).ljust(widths[header]) for header in headers)
        output += data_row + "\n"
    
    return output


def save_output(data: Any, filepath: str, format: str, cli: SNMPCLI):
    """Save data to file in specified format."""
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'json':
            with open(filepath, 'w') as f:
                if hasattr(data, 'to_json'):
                    f.write(data.to_json())
                else:
                    json.dump(data, f, indent=2, default=str)
        
        elif format == 'csv':
            with open(filepath, 'w', newline='') as f:
                if hasattr(data, 'entries'):
                    # SNMPWalkResult object
                    if data.entries:
                        writer = csv.DictWriter(f, fieldnames=data.entries[0].to_dict().keys())
                        writer.writeheader()
                        for entry in data.entries:
                            writer.writerow(entry.to_dict())
                elif isinstance(data, list):
                    # List of entries
                    if data:
                        if hasattr(data[0], 'to_dict'):
                            rows = [item.to_dict() for item in data]
                        else:
                            rows = data
                        
                        if rows:
                            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                            writer.writeheader()
                            writer.writerows(rows)
        
        cli.print_success(f"Output saved to {filepath}")
        
    except Exception as e:
        cli.print_error(f"Failed to save output: {e}")


def handle_walk_command(args, cli: SNMPCLI):
    """Handle walk command."""
    cli.print_header(f"SNMP Walk: {args.host}")
    
    try:
        # Configure runner
        runner = SNMPRunner(timeout=args.timeout, retries=args.retries)
        
        # Execute walk
        cli.print_info(f"Executing SNMP walk on {args.host}...")
        result = runner.run_snmpwalk(
            host=args.host,
            community=args.community,
            oid=args.oid,
            version=args.snmp_version,
            timeout=args.timeout,
            retries=args.retries
        )
        
        cli.print_success(f"Retrieved {result.get_entry_count()} entries")
        
        # Display results
        if args.format == 'table':
            if args.show_system and result.system_info:
                print(format_table_output([result.system_info], "System Information"))
            
            if args.show_interfaces:
                interfaces = cli.parser.get_interface_info(result.entries)
                if interfaces:
                    print(format_table_output(interfaces, "Interface Information"))
            
            if not args.show_system and not args.show_interfaces:
                print(format_table_output(result.entries[:20], "SNMP Entries (showing first 20)"))
                if len(result.entries) > 20:
                    cli.print_info(f"... and {len(result.entries) - 20} more entries")
        
        elif args.format == 'json':
            print(result.to_json())
        
        # Save output if requested
        if args.output:
            save_output(result, args.output, args.format, cli)
        
    except Exception as e:
        cli.print_error(f"Walk failed: {e}")
        return 1
    
    return 0


def handle_get_command(args, cli: SNMPCLI):
    """Handle get command."""
    cli.print_header(f"SNMP Get: {args.host}")
    
    try:
        runner = SNMPRunner(timeout=args.timeout)
        
        cli.print_info(f"Getting OIDs: {', '.join(args.oids)}")
        result = runner.run_snmpget(
            host=args.host,
            community=args.community,
            oids=args.oids,
            version=args.snmp_version,
            timeout=args.timeout
        )
        
        cli.print_success(f"Retrieved {result.get_entry_count()} entries")
        
        # Display results
        if args.format == 'table':
            print(format_table_output(result.entries, "SNMP Get Results"))
        elif args.format == 'json':
            print(result.to_json())
        
        # Save output if requested
        if args.output:
            save_output(result, args.output, args.format, cli)
        
    except Exception as e:
        cli.print_error(f"Get failed: {e}")
        return 1
    
    return 0


def handle_bulk_command(args, cli: SNMPCLI):
    """Handle bulk command."""
    cli.print_header(f"SNMP Bulk Walk: {args.host}")
    
    try:
        runner = SNMPRunner(timeout=args.timeout)
        
        cli.print_info(f"Executing bulk walk on {args.host}...")
        result = runner.run_snmpbulkwalk(
            host=args.host,
            community=args.community,
            oid=args.oid,
            version=args.snmp_version,
            max_repetitions=args.max_repetitions,
            timeout=args.timeout
        )
        
        cli.print_success(f"Retrieved {result.get_entry_count()} entries")
        
        # Display results
        if args.format == 'table':
            print(format_table_output(result.entries[:20], "SNMP Bulk Walk Results (showing first 20)"))
            if len(result.entries) > 20:
                cli.print_info(f"... and {len(result.entries) - 20} more entries")
        elif args.format == 'json':
            print(result.to_json())
        
        # Save output if requested
        if args.output:
            save_output(result, args.output, args.format, cli)
        
    except Exception as e:
        cli.print_error(f"Bulk walk failed: {e}")
        return 1
    
    return 0


def handle_parse_command(args, cli: SNMPCLI):
    """Handle parse command."""
    cli.print_header(f"Parsing SNMP Output: {args.file}")
    
    try:
        # Read file
        with open(args.file, 'r') as f:
            content = f.read()
        
        # Parse content
        entries = cli.parser.parse_snmpwalk_output(content)
        
        # Apply filter if specified
        if args.filter:
            entries = cli.parser.filter_by_oid_pattern(entries, args.filter)
        
        cli.print_success(f"Parsed {len(entries)} entries")
        
        # Display results
        if args.format == 'table':
            if args.show_system:
                system_info = cli.parser.get_system_info(entries)
                if system_info:
                    print(format_table_output([system_info], "System Information"))
            
            if args.show_interfaces:
                interfaces = cli.parser.get_interface_info(entries)
                if interfaces:
                    print(format_table_output(interfaces, "Interface Information"))
            
            if not args.show_system and not args.show_interfaces:
                print(format_table_output(entries[:20], "Parsed SNMP Entries (showing first 20)"))
                if len(entries) > 20:
                    cli.print_info(f"... and {len(entries) - 20} more entries")
        
        elif args.format == 'json':
            result = {
                'file': args.file,
                'entries': [entry.to_dict() for entry in entries],
                'count': len(entries)
            }
            print(json.dumps(result, indent=2))
        
        # Save output if requested
        if args.output:
            save_output(entries, args.output, args.format, cli)
        
    except Exception as e:
        cli.print_error(f"Parse failed: {e}")
        return 1
    
    return 0


def handle_discover_command(args, cli: SNMPCLI):
    """Handle discover command."""
    cli.print_header(f"SNMP Discovery: {args.network}")
    
    try:
        runner = SNMPRunner(timeout=args.timeout)
        
        cli.print_info(f"Discovering SNMP hosts in {args.network}...")
        hosts = runner.discover_snmp_hosts(
            network=args.network,
            community=args.community,
            timeout=args.timeout
        )
        
        cli.print_success(f"Found {len(hosts)} SNMP-enabled hosts")
        
        # Display results
        if args.format == 'table':
            host_data = [{'host': host} for host in hosts]
            print(format_table_output(host_data, "Discovered SNMP Hosts"))
        elif args.format == 'json':
            result = {
                'network': args.network,
                'hosts': hosts,
                'count': len(hosts)
            }
            print(json.dumps(result, indent=2))
        
        # Save output if requested
        if args.output:
            save_output(hosts, args.output, args.format, cli)
        
    except Exception as e:
        cli.print_error(f"Discovery failed: {e}")
        return 1
    
    return 0


def handle_parallel_command(args, cli: SNMPCLI):
    """Handle parallel command."""
    cli.print_header(f"Parallel SNMP Walk: {len(args.hosts)} hosts")
    
    try:
        runner = SNMPRunner()
        
        cli.print_info(f"Executing parallel walk on {len(args.hosts)} hosts...")
        results = runner.run_parallel_snmpwalk(
            hosts=args.hosts,
            community=args.community,
            oid=args.oid,
            version=args.snmp_version,
            max_workers=args.workers
        )
        
        # Count successful results
        successful = sum(1 for r in results.values() if isinstance(r, SNMPWalkResult))
        failed = len(results) - successful
        
        cli.print_success(f"Completed: {successful} successful, {failed} failed")
        
        # Display results
        if args.format == 'table':
            summary_data = []
            for host, result in results.items():
                if isinstance(result, SNMPWalkResult):
                    summary_data.append({
                        'host': host,
                        'status': 'Success',
                        'entries': result.get_entry_count(),
                        'tables': result.get_table_count()
                    })
                else:
                    summary_data.append({
                        'host': host,
                        'status': 'Failed',
                        'entries': 0,
                        'tables': 0
                    })
            
            print(format_table_output(summary_data, "Parallel Walk Results"))
        
        elif args.format == 'json':
            # Convert results to JSON-serializable format
            json_results = {}
            for host, result in results.items():
                if isinstance(result, SNMPWalkResult):
                    json_results[host] = result.to_dict()
                else:
                    json_results[host] = {'error': str(result)}
            
            print(json.dumps(json_results, indent=2))
        
        # Save output if requested
        if args.output:
            save_output(results, args.output, args.format, cli)
        
    except Exception as e:
        cli.print_error(f"Parallel walk failed: {e}")
        return 1
    
    return 0


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Initialize CLI
    cli = SNMPCLI()
    
    # Disable colors if requested
    if args.no_color:
        cli.colors = type('NoColors', (), {attr: '' for attr in dir(cli.colors) if not attr.startswith('_')})()
    
    # Handle commands
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'walk':
            return handle_walk_command(args, cli)
        elif args.command == 'get':
            return handle_get_command(args, cli)
        elif args.command == 'bulk':
            return handle_bulk_command(args, cli)
        elif args.command == 'parse':
            return handle_parse_command(args, cli)
        elif args.command == 'discover':
            return handle_discover_command(args, cli)
        elif args.command == 'parallel':
            return handle_parallel_command(args, cli)
        else:
            cli.print_error(f"Unknown command: {args.command}")
            return 1
    
    except KeyboardInterrupt:
        cli.print_warning("Operation cancelled by user")
        return 130
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            cli.print_error(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())