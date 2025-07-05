# SNMP Parser Documentation

[![PyPI version](https://badge.fury.io/py/snmpwalk-parser.svg)](https://badge.fury.io/py/snmpwalk-parser)
[![Python versions](https://img.shields.io/pypi/pyversions/snmpwalk-parser.svg)](https://pypi.org/project/snmpwalk-parser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python package for parsing and analyzing SNMP walk outputs with advanced features for network discovery, parallel operations, and structured data export.

🔧 This tool is focused on parsing actual SNMP command-line output — not compiling MIBs.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Components](#core-components)
- [CLI Usage](#cli-usage)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Advanced Usage](#advanced-usage)
- [Contributing](#contributing)
- [License](#license)

## Features

### 🔍 **Comprehensive SNMP Operations**
- Parse standard and numeric SNMP walk outputs
- Execute live SNMP operations (walk, get, bulk walk)
- Support for SNMP v1, v2c, and v3
- Parallel SNMP operations across multiple hosts
- Network discovery for SNMP-enabled devices

### 📊 **Data Processing & Analysis**
- Group results by SNMP tables (ifTable, ipAddrTable, etc.)
- Extract system information automatically
- Filter entries by OID patterns
- Support for all standard SNMP data types

### 💾 **Export & Integration**
- Export to JSON, CSV formats
- Structured data models for easy integration
- Command-line interface for automation
- File-based parsing for offline analysis

### ⚡ **Performance & Reliability**
- Concurrent execution with ThreadPoolExecutor
- Retry mechanisms with exponential backoff
- Timeout handling and error recovery
- Memory-efficient parsing for large datasets

## Installation

### Requirements
- Python 3.8 or higher
- SNMP tools (snmpwalk, snmpget, snmpset, snmpbulkwalk) for live operations

### Install from PyPI

```bash
pip install snmpwalk-parser
```

### Install from Source

```bash
git clone https://github.com/kunalraut666/snmpwalk-parser.git
cd snmpwalk-parser
pip install -e .
```

### Install SNMP Tools (Optional)

For live SNMP operations, install the SNMP utilities:

**Ubuntu/Debian:**
```bash
sudo apt-get install snmp snmp-mibs-downloader
```

**CentOS/RHEL:**
```bash
sudo yum install net-snmp-utils
```

**macOS:**
```bash
brew install net-snmp
```

## Quick Start

### Basic Parsing

```python
from snmpwalk_parser import SNMPParser

# Parse SNMP output from file
parser = SNMPParser()
entries = parser.parse_file("snmpwalk_output.txt")

# Display results
for entry in entries[:5]:  # Show first 5 entries
    print(f"OID: {entry.oid}")
    print(f"Value: {entry.value}")
    print(f"Type: {entry.type}")
    print("---")
```

### Live SNMP Operations

```python
from snmpwalk_parser import SNMPRunner

# Initialize SNMP runner
runner = SNMPRunner()

# Perform SNMP walk
result = runner.run_snmpwalk(
    host="192.168.1.1",
    community="public",
    oid="1.3.6.1.2.1.1"  # System information
)

print(f"Retrieved {result.get_entry_count()} entries")
print(f"System info: {result.system_info}")
```

### Export Results

```python
# Export to JSON
result.export_to_file("output.json", "json")

# Export to CSV
result.export_to_file("output.csv", "csv")

# Get as dictionary
data = result.to_dict()
```

## Core Components

### SNMPParser Class

The core parsing engine that processes SNMP walk outputs.

```python
from snmpwalk_parser.core import SNMPParser

parser = SNMPParser()

# Parse text output
entries = parser.parse_snmpwalk_output(snmp_text)

# Parse from file
entries = parser.parse_file("output.txt")

# Group by tables
tables = parser.group_by_table(entries)

# Extract system information
system_info = parser.get_system_info(entries)

# Get interface information
interfaces = parser.get_interface_info(entries)
```

### SNMPRunner Class

Handles live SNMP operations with advanced features.

```python
from snmpwalk_parser.snmp_runner import SNMPRunner

# Initialize with custom settings
runner = SNMPRunner(timeout=30, retries=3)

# SNMP Walk
result = runner.run_snmpwalk("192.168.1.1", "public")

# SNMP Get
result = runner.run_snmpget("192.168.1.1", "public", ["sysDescr.0", "sysName.0"])

# SNMP Bulk Walk (faster for large tables)
result = runner.run_snmpbulkwalk("192.168.1.1", "public", "1.3.6.1.2.1.2")

# Parallel operations
hosts = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
results = runner.run_parallel_snmpwalk(hosts, "public")

# Network discovery
discovered_hosts = runner.discover_snmp_hosts("192.168.1.0/24", "public")
```

### Data Models

#### SNMPEntry

Represents a single SNMP entry.

```python
from snmpwalk_parser.models import SNMPEntry

entry = SNMPEntry(
    oid="1.3.6.1.2.1.1.1.0",
    key="sysDescr",
    index="0",
    type="STRING",
    value="Linux server 5.4.0",
    raw_value='"Linux server 5.4.0"'
)

# Check OID format
print(entry.is_numeric_oid())  # True
print(entry.is_named_oid())    # False

# Get table name
print(entry.get_table_name())  # "sysDescr"

# Convert to dictionary
data = entry.to_dict()
```

#### SNMPWalkResult

Container for complete SNMP walk results.

```python
from snmpwalk_parser.models import SNMPWalkResult

result = SNMPWalkResult(
    host="192.168.1.1",
    community="public",
    oid="1.3.6.1.2.1"
)

# Add entries
for entry in parsed_entries:
    result.add_entry(entry)

# Access data
print(f"Total entries: {result.get_entry_count()}")
print(f"Tables found: {result.get_table_names()}")
print(f"System info: {result.system_info}")

# Get summary
summary = result.get_summary()
```

## CLI Usage

The package includes a comprehensive command-line interface for all operations.

### Installation

The CLI is automatically available after installing the package:

```bash
snmpwalk-parser --help
```

### Commands

#### SNMP Walk

```bash
# Basic walk
snmpwalk-parser walk 192.168.1.1 -c public

# Walk specific OID
snmpwalk-parser walk 192.168.1.1 -c public -o 1.3.6.1.2.1.1

# Save to file
snmpwalk-parser walk 192.168.1.1 -c public --output results.json --format json

# Show system information
snmpwalk-parser walk 192.168.1.1 -c public --show-system

# Show interface information
snmpwalk-parser walk 192.168.1.1 -c public --show-interfaces
```

#### SNMP Get

```bash
# Get specific OIDs
snmpwalk-parser get 192.168.1.1 -c public -o sysDescr.0 sysName.0

# Export to CSV
snmpwalk-parser get 192.168.1.1 -c public -o sysDescr.0 --output system.csv --format csv
```

#### Bulk Walk

```bash
# Bulk walk for better performance
snmpwalk-parser bulk 192.168.1.1 -c public -o 1.3.6.1.2.1.2

# Custom repetitions
snmpwalk-parser bulk 192.168.1.1 -c public -o 1.3.6.1.2.1.2 -m 25
```

#### Parse Existing Output

```bash
# Parse saved SNMP output
snmpwalk-parser parse -f snmpwalk_output.txt

# Filter by pattern
snmpwalk-parser parse -f output.txt --filter "ifDescr.*"

# Export parsed data
snmpwalk-parser parse -f output.txt --output parsed.json --format json
```

#### Network Discovery

```bash
# Discover SNMP hosts
snmpwalk-parser discover 192.168.1.0/24 -c public

# Custom timeout
snmpwalk-parser discover 10.0.0.0/16 -c public -t 10

# Save discovered hosts
snmpwalk-parser discover 192.168.1.0/24 -c public --output hosts.json
```

#### Parallel Operations

```bash
# Parallel walk on multiple hosts
snmpwalk-parser parallel -H 192.168.1.1 192.168.1.2 192.168.1.3 -c public

# Custom worker count
snmpwalk-parser parallel -H 192.168.1.{1..10} -c public -w 20

# Export results
snmpwalk-parser parallel -H 192.168.1.1 192.168.1.2 -c public --output parallel.json
```

### Global Options

```bash
# Verbose output
snmpwalk-parser walk 192.168.1.1 -c public -v

# Disable colors
snmpwalk-parser walk 192.168.1.1 -c public --no-color

# Custom timeout and retries
snmpwalk-parser walk 192.168.1.1 -c public -t 60 -r 5

# SNMP version
snmpwalk-parser walk 192.168.1.1 -c public -V 1
```

## API Reference

### SNMPParser Methods

#### `parse_snmpwalk_output(text: str) -> List[SNMPEntry]`
Parse SNMP walk output text.

**Parameters:**
- `text`: Raw SNMP walk output

**Returns:**
- List of SNMPEntry objects

#### `parse_file(file_path: str) -> List[SNMPEntry]`
Parse SNMP output from file.

**Parameters:**
- `file_path`: Path to file containing SNMP output

**Returns:**
- List of SNMPEntry objects

#### `group_by_table(entries: List[SNMPEntry]) -> Dict[str, SNMPTable]`
Group entries by SNMP table.

**Parameters:**
- `entries`: List of SNMPEntry objects

**Returns:**
- Dictionary mapping table names to SNMPTable objects

#### `get_system_info(entries: List[SNMPEntry]) -> Dict[str, Any]`
Extract system information from entries.

**Parameters:**
- `entries`: List of SNMPEntry objects

**Returns:**
- Dictionary with system information

### SNMPRunner Methods

#### `run_snmpwalk(host, community, oid, version, timeout, retries) -> SNMPWalkResult`
Execute SNMP walk operation.

**Parameters:**
- `host`: Target host IP or hostname
- `community`: SNMP community string (default: "public")
- `oid`: Starting OID (default: "" for full walk)
- `version`: SNMP version ("1", "2c", "3", default: "2c")
- `timeout`: Timeout in seconds (optional)
- `retries`: Number of retries (optional)

**Returns:**
- SNMPWalkResult object

#### `run_snmpget(host, community, oids, version, timeout) -> SNMPWalkResult`
Execute SNMP get operation.

**Parameters:**
- `host`: Target host
- `community`: SNMP community string
- `oids`: List of OIDs to retrieve
- `version`: SNMP version (default: "2c")
- `timeout`: Timeout in seconds (optional)

**Returns:**
- SNMPWalkResult object

#### `run_parallel_snmpwalk(hosts, community, oid, version, max_workers) -> Dict`
Execute parallel SNMP walks.

**Parameters:**
- `hosts`: List of host addresses
- `community`: SNMP community string
- `oid`: Starting OID (default: "")
- `version`: SNMP version (default: "2c")
- `max_workers`: Number of parallel workers (default: 10)

**Returns:**
- Dictionary mapping hosts to results

#### `discover_snmp_hosts(network, community, timeout) -> List[str]`
Discover SNMP-enabled hosts in network.

**Parameters:**
- `network`: Network in CIDR notation (e.g., "192.168.1.0/24")
- `community`: SNMP community string
- `timeout`: Timeout per host (default: 5)

**Returns:**
- List of discovered host addresses

## Examples

### Example 1: Network Interface Analysis

```python
from snmpwalk_parser import SNMPRunner, SNMPParser

runner = SNMPRunner()
parser = SNMPParser()

# Get interface table
result = runner.run_snmpwalk("192.168.1.1", "public", "1.3.6.1.2.1.2")

# Extract interface information
interfaces = parser.get_interface_info(result.entries)

for iface in interfaces:
    print(f"Interface {iface['index']}: {iface.get('description', 'N/A')}")
    print(f"  Speed: {iface.get('speed', 'Unknown')}")
    print(f"  Status: {iface.get('status', 'Unknown')}")
```

### Example 2: System Monitoring

```python
import json
from snmpwalk_parser import SNMPRunner

def monitor_systems(hosts, community="public"):
    runner = SNMPRunner()
    
    # Get system information from all hosts
    results = runner.run_parallel_snmpwalk(
        hosts=hosts,
        community=community,
        oid="1.3.6.1.2.1.1"  # System MIB
    )
    
    monitoring_data = {}
    
    for host, result in results.items():
        if hasattr(result, 'system_info'):
            monitoring_data[host] = {
                'system_description': result.system_info.get('system_description'),
                'system_uptime': result.system_info.get('system_uptime'),
                'system_name': result.system_info.get('system_name'),
                'system_location': result.system_info.get('system_location')
            }
        else:
            monitoring_data[host] = {'error': str(result)}
    
    return monitoring_data

# Monitor multiple systems
hosts = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
data = monitor_systems(hosts)

# Save monitoring data
with open("monitoring_report.json", "w") as f:
    json.dump(data, f, indent=2)
```

### Example 3: Network Discovery and Inventory

```python
from snmpwalk_parser import SNMPRunner
import csv

def network_inventory(network, community="public"):
    runner = SNMPRunner()
    
    print(f"Discovering devices in {network}...")
    hosts = runner.discover_snmp_hosts(network, community)
    
    print(f"Found {len(hosts)} SNMP-enabled devices")
    
    inventory = []
    
    for host in hosts:
        try:
            # Get system information
            result = runner.run_snmpwalk(host, community, "1.3.6.1.2.1.1")
            
            device_info = {
                'ip_address': host,
                'system_description': result.system_info.get('system_description', 'Unknown'),
                'system_name': result.system_info.get('system_name', 'Unknown'),
                'system_location': result.system_info.get('system_location', 'Unknown'),
                'system_contact': result.system_info.get('system_contact', 'Unknown'),
                'uptime': result.system_info.get('system_uptime', 'Unknown')
            }
            
            inventory.append(device_info)
            print(f"✓ {host}: {device_info['system_description'][:50]}...")
            
        except Exception as e:
            print(f"✗ {host}: Failed - {e}")
    
    return inventory

# Perform network inventory
devices = network_inventory("192.168.1.0/24")

# Export to CSV
with open("network_inventory.csv", "w", newline="") as f:
    if devices:
        writer = csv.DictWriter(f, fieldnames=devices[0].keys())
        writer.writeheader()
        writer.writerows(devices)

print(f"Inventory saved to network_inventory.csv ({len(devices)} devices)")
```

### Example 4: Custom SNMP Data Processing

```python
from snmpwalk_parser import SNMPParser
import re

def analyze_interface_utilization(snmp_file):
    parser = SNMPParser()
    entries = parser.parse_file(snmp_file)
    
    # Filter interface-related entries
    interface_entries = parser.filter_by_oid_pattern(entries, r"1\.3\.6\.1\.2\.1\.2\.2\.1\.")
    
    # Group by interface index
    interfaces = {}
    for entry in interface_entries:
        index = entry.index
        if index not in interfaces:
            interfaces[index] = {}
        
        # Map OID to readable names
        oid_map = {
            '2': 'description',
            '3': 'type',
            '5': 'speed',
            '8': 'oper_status',
            '10': 'in_octets',
            '16': 'out_octets',
            '13': 'in_discards',
            '19': 'out_discards',
            '14': 'in_errors',
            '20': 'out_errors'
        }
        
        oid_suffix = entry.oid.split('.')[-2]
        if oid_suffix in oid_map:
            interfaces[index][oid_map[oid_suffix]] = entry.value
    
    # Calculate utilization (simplified example)
    for idx, iface in interfaces.items():
        if 'in_octets' in iface and 'out_octets' in iface and 'speed' in iface:
            try:
                total_octets = int(iface['in_octets']) + int(iface['out_octets'])
                speed_bps = int(iface['speed'])
                
                # This is a simplified calculation - real utilization needs time sampling
                print(f"Interface {idx} ({iface.get('description', 'Unknown')}):")
                print(f"  Speed: {speed_bps:,} bps")
                print(f"  Total octets: {total_octets:,}")
                print(f"  Status: {iface.get('oper_status', 'Unknown')}")
                print()
            except (ValueError, TypeError):
                continue

# Analyze interface data
analyze_interface_utilization("interface_walk.txt")
```

## Advanced Usage

### Custom SNMP Types Processing

```python
from snmpwalk_parser.core import SNMPParser

class CustomSNMPParser(SNMPParser):
    def __init__(self):
        super().__init__()
        # Add custom type processors
        self.type_processors['CUSTOM_TYPE'] = self._process_custom_type
    
    def _process_custom_type(self, value: str):
        # Custom processing logic
        return f"processed_{value}"

# Use custom parser
parser = CustomSNMPParser()
entries = parser.parse_file("custom_output.txt")
```

### Batch Processing

```python
from snmpwalk_parser import SNMPRunner
from concurrent.futures import ThreadPoolExecutor
import glob

def process_network_batch(network_configs):
    """Process multiple networks in parallel."""
    runner = SNMPRunner()
    
    def process_network(config):
        network = config['network']
        community = config['community']
        
        hosts = runner.discover_snmp_hosts(network, community)
        results = runner.run_parallel_snmpwalk(hosts, community)
        
        return {
            'network': network,
            'hosts_found': len(hosts),
            'successful_queries': sum(1 for r in results.values() 
                                    if hasattr(r, 'entries')),
            'results': results
        }
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_network, config) 
                  for config in network_configs]
        return [future.result() for future in futures]

# Process multiple networks
networks = [
    {'network': '192.168.1.0/24', 'community': 'public'},
    {'network': '192.168.2.0/24', 'community': 'private'},
    {'network': '10.0.0.0/24', 'community': 'public'}
]

results = process_network_batch(networks)
```

### Error Handling and Logging

```python
import logging
from snmpwalk_parser import SNMPRunner, SNMPError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def robust_snmp_query(host, community, max_attempts=3):
    runner = SNMPRunner(timeout=30, retries=2)
    
    for attempt in range(max_attempts):
        try:
            result = runner.run_snmpwalk(host, community)
            logger.info(f"Successfully queried {host} on attempt {attempt + 1}")
            return result
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {host}: {e}")
            if attempt == max_attempts - 1:
                logger.error(f"All attempts failed for {host}")
                return SNMPError(code=1, message=str(e), details=f"Host: {host}")
    
    return None

# Use robust querying
result = robust_snmp_query("192.168.1.1", "public")
if isinstance(result, SNMPError):
    print(f"Query failed: {result}")
else:
    print(f"Query successful: {result.get_entry_count()} entries")
```

## Performance Optimization

### Memory Efficient Processing

```python
from snmpwalk_parser import SNMPParser

def process_large_file_efficiently(file_path, chunk_size=1000):
    """Process large SNMP files in chunks to optimize memory usage."""
    parser = SNMPParser()
    
    with open(file_path, 'r') as f:
        lines = []
        for line in f:
            lines.append(line.strip())
            
            if len(lines) >= chunk_size:
                # Process chunk
                chunk_text = '\n'.join(lines)
                entries = parser.parse_snmpwalk_output(chunk_text)
                
                # Process entries (e.g., save to database, analyze, etc.)
                yield entries
                
                lines = []  # Reset for next chunk
        
        # Process remaining lines
        if lines:
            chunk_text = '\n'.join(lines)
            entries = parser.parse_snmpwalk_output(chunk_text)
            yield entries

# Process large file
for chunk_entries in process_large_file_efficiently("large_snmp_output.txt"):
    print(f"Processed chunk with {len(chunk_entries)} entries")
```

### Optimized Parallel Operations

```python
from snmpwalk_parser import SNMPRunner
import asyncio
from concurrent.futures import ThreadPoolExecutor

class OptimizedSNMPRunner:
    def __init__(self, max_workers=50):
        self.runner = SNMPRunner()
        self.max_workers = max_workers
    
    async def query_hosts_async(self, hosts, community, oid=""):
        loop = asyncio.get_event_loop()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            tasks = [
                loop.run_in_executor(
                    executor, 
                    self.runner.run_snmpwalk, 
                    host, community, oid
                )
                for host in hosts
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
        return dict(zip(hosts, results))

# Usage
async def main():
    optimizer = OptimizedSNMPRunner(max_workers=100)
    hosts = [f"192.168.1.{i}" for i in range(1, 255)]
    
    results = await optimizer.query_hosts_async(hosts, "public")
    
    successful = sum(1 for r in results.values() if not isinstance(r, Exception))
    print(f"Successfully queried {successful}/{len(hosts)} hosts")

# Run async operation
# asyncio.run(main())
```

[![Watch Demo](https://img.shields.io/badge/Watch-Demo-orange)](https://www.youtube.com/watch?v=NYHgoyZdDkc)

## Contributing

We welcome contributions! Please see our contributing guidelines:

### Development Setup

```bash
# Clone repository
git clone https://github.com/kunalraut666/snmpwalk-parser.git
cd snmpwalk-parser

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest tests/

# Run linting
flake8 src/
black src/

# Generate documentation
cd docs
make html
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=snmpwalk_parser

# Run specific test categories
pytest tests/test_parser.py
pytest tests/test_runner.py
pytest tests/test_cli.py
```

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Ensure all tests pass: `pytest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## Changelog

### Version 1.0.0
- Initial release
- Basic SNMP parsing functionality
- Live SNMP operations
- CLI interface
- Parallel processing
- Network discovery

### Version 1.1.0 (Planned)
- SNMP v3 authentication support
- Advanced filtering options
- Database integration
- Web interface
- Performance optimizations

## License

This project is licensed under the MIT License — see the [LICENSE](https://github.com/kunalraut666/snmpwalk-parser/blob/main/LICENSE) file for details.


## Support

- **Documentation**: https://snmpwalk-parser.readthedocs.io
- **Issues**: https://github.com/kunalraut666/snmpwalk-parser/issues
- **PyPI**: https://pypi.org/project/snmpwalk-parser/
- **Repository**: https://github.com/kunalraut666/snmpwalk-parser

---

*Made with ❤️ by [Kunal Raut](https://github.com/kunalraut666)*