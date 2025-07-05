# snmpwalk-parser

A comprehensive and extensible SNMP parsing library built in Python. It provides a high-level API and CLI for converting raw SNMP command-line output into structured data for easy inspection, transformation, and export. Designed specifically to parse raw outputs from `snmpwalk`, `snmpget`, and `snmpbulkwalk`, not MIB files.


[![PyPI version](https://img.shields.io/pypi/v/snmpwalk-parser)](https://pypi.org/project/snmpwalk-parser/)
[![Python versions](https://img.shields.io/pypi/pyversions/snmpwalk-parser)](https://pypi.org/project/snmpwalk-parser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/personalized-badge/snmpwalk-parser?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads)](https://pepy.tech/project/snmpwalk-parser)



---

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Python Usage](#-python-usage)
- [CLI Usage](#-cli-usage)
- [Configuration](#-configuration)
- [Output Formats](#-output-formats)
- [Advanced Usage](#-advanced-usage)
- [Examples](#-examples)
- [Testing](#-testing)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

---

## ✨ Features

- 📄 **Raw SNMP Output Parsing**: Parses saved output from `snmpwalk`, `snmpget`, and `snmpbulkwalk` — unlike tools like `pysmi`, this focuses on interpreting command-line SNMP results, not compiling MIBs.
- 🔍 **Multi-format Support**: Parse output from `snmpwalk`, `snmpget`, and `snmpbulkwalk`
- 📊 **Smart Analysis**: Automatically extract system info and interface summaries
- 🗂️ **Table Organization**: Group entries into SNMP tables for better structure
- 🧵 **Parallel Processing**: Multi-threaded SNMP walk over multiple hosts
- 🔁 **Robust Operations**: Retry and timeout support for flaky SNMP agents
- 🧪 **CLI Tool**: Built-in command-line interface for quick parsing
- 📤 **Export Options**: Clean JSON, CSV, and XML export support
- 🔌 **Extensible**: Clean architecture with modular parsing logic
- 🎯 **MIB Support**: Built-in support for common MIBs (IF-MIB, SNMPv2-MIB, etc.)
- 📈 **Performance**: Optimized for large SNMP datasets

---

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install snmpwalk-parser
```

### From Source

```bash
git clone https://github.com/kunalraut/snmpwalk-parser.git
cd snmpwalk-parser
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/kunalraut/snmpwalk-parser.git
cd snmpwalk-parser
pip install -e .[dev]
```

### Requirements

- Python 3.7+
- Net-SNMP tools (for live SNMP operations)
- Required Python packages: `click`, `pandas`, `pyyaml`

---

## 🚀 Quick Start

### Parse existing SNMP output

```python
from snmpwalk_parser import SNMPParser

# Parse saved SNMP output
parser = SNMPParser()
result = parser.parse_file("snmp_output.txt")
print(result.to_json())
```

### Run live SNMP walk

```python
from snmpwalk_parser.runner import SNMPRunner

runner = SNMPRunner(timeout=5)
result = runner.run_snmpwalk("192.168.1.1", community="public", oid="sysName")
print(result.system_info)
```

---

## 🐍 Python Usage

### Basic SNMP Operations

#### SNMP Walk
```python
from snmpwalk_parser.runner import SNMPRunner

runner = SNMPRunner(timeout=5, retries=3)
result = runner.run_snmpwalk(
    host="192.168.1.1",
    community="public",
    oid="1.3.6.1.2.1.1"  # System MIB
)

# Access parsed data
print(f"System Name: {result.system_info.get('system_name')}")
print(f"Total Entries: {len(result.entries)}")
```

#### SNMP Get
```python
result = runner.run_snmpget(
    host="192.168.1.1",
    community="public",
    oids=["sysDescr.0", "sysUpTime.0", "sysContact.0"]
)

for entry in result.entries:
    print(f"{entry.key}: {entry.value}")
```

#### SNMP Bulk Walk
```python
result = runner.run_snmpbulkwalk(
    host="192.168.1.1",
    community="public",
    oid="ifTable",
    max_repetitions=25
)
```

### Parallel Operations

```python
hosts = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
results = runner.run_parallel_snmpwalk(
    hosts,
    community="public",
    oid="sysDescr",
    max_workers=5
)

for host, result in results.items():
    if result.success:
        print(f"{host}: {result.system_info}")
    else:
        print(f"{host}: Error - {result.error}")
```

### Advanced Parsing

```python
from snmpwalk_parser import SNMPParser

parser = SNMPParser()
result = parser.parse_file("large_snmp_output.txt")

# Access interface information
interfaces = result.get_interfaces()
for interface in interfaces:
    print(f"Interface {interface.index}: {interface.description}")
    print(f"  Status: {interface.admin_status}/{interface.oper_status}")
    print(f"  Speed: {interface.speed} bps")

# Access SNMP tables
tables = result.get_tables()
for table_name, entries in tables.items():
    print(f"\nTable: {table_name}")
    for entry in entries:
        print(f"  {entry.index}: {entry.value}")
```

---

## 💻 CLI Usage

### Parse Files

```bash
# Parse saved SNMP output
snmpwalk-parser parse sample_output.txt --format json

# Parse with custom output file
snmpwalk-parser parse input.txt --output result.json --format json

# Parse multiple files
snmpwalk-parser parse *.txt --format csv --output combined.csv
```

### Live SNMP Operations

```bash
# Basic SNMP walk
snmpwalk-parser walk --host 192.168.1.1 --community public --oid sysDescr

# SNMP walk with custom parameters
snmpwalk-parser walk \
  --host 192.168.1.1 \
  --community public \
  --oid ifTable \
  --version 2c \
  --timeout 10 \
  --retries 3

# SNMP get multiple OIDs
snmpwalk-parser get \
  --host 192.168.1.1 \
  --community public \
  --oids sysDescr.0 sysUpTime.0 sysContact.0

# Bulk walk with custom parameters
snmpwalk-parser bulk \
  --host 192.168.1.1 \
  --community public \
  --oid ifTable \
  --max-repetitions 25
```

## 🎥 Demo

[![Watch the demo](https://img.youtube.com/vi/NYHgoyZdDkc/0.jpg)](https://www.youtube.com/watch?v=NYHgoyZdDkc)

👉 **Click the thumbnail above or [watch on YouTube](https://www.youtube.com/watch?v=NYHgoyZdDkc)**  


### Parallel Operations

```bash
# Walk multiple hosts
snmpwalk-parser multi-walk \
  --hosts 192.168.1.1,192.168.1.2,192.168.1.3 \
  --community public \
  --oid sysDescr \
  --workers 5 \
  --output results.json
```

### Advanced CLI Options

```bash
# Enable verbose logging
snmpwalk-parser walk --host 192.168.1.1 --community public --oid sysDescr --verbose

# Save raw SNMP output
snmpwalk-parser walk --host 192.168.1.1 --community public --oid ifTable --save-raw raw_output.txt

# Use configuration file
snmpwalk-parser walk --config config.yaml
```

---

## ⚙️ Configuration

### Configuration File

Create a `config.yaml` file:

```yaml
snmp:
  version: "2c"
  timeout: 10
  retries: 3
  community: "public"

parsing:
  group_tables: true
  extract_interfaces: true
  resolve_names: true

output:
  format: "json"
  indent: 2
  include_raw: false

hosts:
  - name: "router1"
    host: "192.168.1.1"
    community: "public"
  - name: "switch1"
    host: "192.168.1.2"
    community: "private"
```

### Environment Variables

```bash
export SNMP_COMMUNITY="public"
export SNMP_VERSION="2c"
export SNMP_TIMEOUT=10
export SNMP_RETRIES=3
```

---

## 📊 Output Formats

### JSON Output
```json
{
  "host": "192.168.1.1",
  "timestamp": "2024-01-15T10:30:00Z",
  "success": true,
  "entries": [
    {
      "oid": "IF-MIB::ifDescr.1",
      "key": "ifDescr",
      "index": "1",
      "type": "STRING",
      "value": "eth0",
      "raw_oid": "1.3.6.1.2.1.2.2.1.2.1"
    }
  ],
  "system_info": {
    "system_name": "Router1",
    "system_description": "Cisco IOS Software",
    "system_uptime": "12 days, 3:45:21",
    "system_contact": "admin@example.com"
  },
  "interfaces": [
    {
      "index": "1",
      "description": "eth0",
      "type": "ethernetCsmacd",
      "mtu": 1500,
      "speed": 1000000000,
      "admin_status": "up",
      "oper_status": "up"
    }
  ],
  "tables": {
    "ifTable": [...],
    "ipAddrTable": [...]
  }
}
```

### CSV Output
```csv
host,oid,key,index,type,value,timestamp
192.168.1.1,IF-MIB::ifDescr.1,ifDescr,1,STRING,eth0,2024-01-15T10:30:00Z
192.168.1.1,IF-MIB::ifType.1,ifType,1,INTEGER,6,2024-01-15T10:30:00Z
```

### XML Output
```xml
<?xml version="1.0" encoding="UTF-8"?>
<snmp_result>
  <host>192.168.1.1</host>
  <timestamp>2024-01-15T10:30:00Z</timestamp>
  <entries>
    <entry>
      <oid>IF-MIB::ifDescr.1</oid>
      <key>ifDescr</key>
      <index>1</index>
      <type>STRING</type>
      <value>eth0</value>
    </entry>
  </entries>
</snmp_result>
```

---

## 🔧 Advanced Usage

### Custom Parsing Rules

```python
from snmpwalk_parser import SNMPParser
from snmpwalk_parser.parsers import BaseParser

class CustomParser(BaseParser):
    def parse_entry(self, line):
        # Custom parsing logic
        return super().parse_entry(line)

parser = SNMPParser(custom_parsers=[CustomParser()])
```

### Filtering and Transformation

```python
result = runner.run_snmpwalk("192.168.1.1", community="public", oid="ifTable")

# Filter interfaces by type
ethernet_interfaces = result.filter_interfaces(lambda iface: iface.type == "ethernetCsmacd")

# Transform data
transformed = result.transform(
    lambda entry: {
        "name": entry.key,
        "value": entry.value,
        "timestamp": entry.timestamp
    }
)
```

### Custom Export

```python
# Export with custom formatting
result.export_to_file("custom_output.json", format="json", options={
    "indent": 4,
    "sort_keys": True,
    "include_metadata": True
})

# Export specific tables
result.export_tables(["ifTable", "ipAddrTable"], "interfaces.csv", format="csv")
```

---

## 📚 Examples

### Network Monitoring

```python
from snmpwalk_parser.runner import SNMPRunner
import time

runner = SNMPRunner()

def monitor_interfaces(host, community):
    while True:
        result = runner.run_snmpwalk(host, community, "ifTable")
        
        for interface in result.get_interfaces():
            if interface.oper_status == "down":
                print(f"ALERT: Interface {interface.description} is down!")
        
        time.sleep(300)  # Check every 5 minutes

monitor_interfaces("192.168.1.1", "public")
```

### Bulk Device Discovery

```python
import ipaddress
from concurrent.futures import ThreadPoolExecutor

def discover_devices(network, community):
    hosts = [str(ip) for ip in ipaddress.IPv4Network(network).hosts()]
    
    def check_host(host):
        try:
            result = runner.run_snmpget(host, community, ["sysDescr.0"])
            return host, result.entries[0].value if result.entries else None
        except:
            return host, None
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(check_host, hosts))
    
    return {host: desc for host, desc in results if desc}

devices = discover_devices("192.168.1.0/24", "public")
for host, description in devices.items():
    print(f"{host}: {description}")
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=snmpwalk_parser

# Run specific test file
pytest tests/test_parser.py

# Run with verbose output
pytest -v

# Run integration tests (requires SNMP agent)
pytest tests/integration/
```

### Generate Coverage Report

```bash
# Generate HTML coverage report
coverage html

# Generate XML coverage report
coverage xml

# View coverage in terminal
coverage report
```

### Test Configuration

Create a `pytest.ini` file:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --strict-markers --cov=snmpwalk_parser --cov-report=term-missing
markers =
    integration: marks tests as integration tests
    slow: marks tests as slow running
```

---

## 📖 Documentation

- **Full Documentation**: https://snmpwalk-parser.readthedocs.io/

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/snmpwalk-parser.git
cd snmpwalk-parser

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Making Changes

1. **Create a branch**: `git checkout -b feature/your-feature-name`
2. **Make your changes**: Follow the existing code style
3. **Add tests**: Ensure your changes are tested
4. **Run tests**: `pytest`
5. **Run linting**: `pre-commit run --all-files`
6. **Update documentation**: If needed
7. **Commit changes**: Use clear, descriptive commit messages
8. **Push and create PR**: Submit a pull request with description

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings for public functions
- Maximum line length: 88 characters (Black formatter)

### Reporting Issues

- Use GitHub Issues
- Include Python version, OS, and package version
- Provide minimal reproduction example
- Include error messages and stack traces

---

## 🔧 Troubleshooting

### Common Issues

**SNMP timeout errors:**
```bash
# Increase timeout and retries
snmpwalk-parser walk --host 192.168.1.1 --community public --oid sysDescr --timeout 30 --retries 5
```

**Permission denied errors:**
```bash
# Check SNMP community string
snmpwalk -v2c -c public 192.168.1.1 sysDescr.0

# Verify host connectivity
ping 192.168.1.1
```

**Large output parsing:**
```python
# Use streaming parser for large files
from snmpwalk_parser import StreamingParser

parser = StreamingParser()
for result in parser.parse_file_streaming("large_output.txt"):
    process_result(result)
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging
runner = SNMPRunner(debug=True)
```

### Performance Tips

- Use `snmpbulkwalk` for large tables
- Implement proper error handling
- Use connection pooling for multiple hosts
- Consider caching for repeated queries

---

---

## 🆚 Comparison with pysmi / pysnmp

While tools like [`pysmi`](https://github.com/etingof/pysmi) and [`pysnmp`](https://github.com/etingof/pysnmp) focus on MIB compilation and low-level SNMP protocol handling respectively, `snmpwalk-parser` is purpose-built for **parsing real-world SNMP command-line outputs** like those produced by `snmpwalk`, `snmpget`, and `snmpbulkwalk`.

| Feature | pysmi | snmpwalk-parser |
|--------|-------|------------------|
| MIB file compilation | ✅ | ❌ |
| Parses `snmpwalk` command output | ❌ | ✅ |
| CLI-based parsing & export | ❌ | ✅ |
| System/interface summary | ❌ | ✅ |
| Network discovery & parallel walk | ❌ | ✅ |

Use this tool when you're dealing with actual `snmpwalk` results and want them in structured formats (JSON, CSV, XML), not MIB files.



## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Kunal Raut

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙌 Acknowledgements

- Built using `snmpwalk`/`snmpget` tools from [Net-SNMP](http://www.net-snmp.org/)
- Inspired by real-world operational tooling needs for NMS and OSS teams
- Special thanks to the Python SNMP community
- Contributors and users who provide feedback and improvements

---

## 🔗 Links

- 📦 **PyPI**: https://pypi.org/project/snmpwalk-parser/
- 🐙 **GitHub**: https://github.com/kunalraut666/snmpwalk-parser
- 📚 **Documentation**: https://snmpwalk-parser.readthedocs.io/
- 🐛 **Issues**: https://github.com/kunalraut666/snmpwalk-parser/issues
- 💬 **Discussions**: https://github.com/kunalraut666/snmpwalk-parser/discussions

---

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/kunalraut/snmpwalk-parser?style=social)
![GitHub forks](https://img.shields.io/github/forks/kunalraut/snmpwalk-parser?style=social)
![GitHub issues](https://img.shields.io/github/issues/kunalraut/snmpwalk-parser)
![GitHub pull requests](https://img.shields.io/github/issues-pr/kunalraut/snmpwalk-parser)

---

## ⭐ Support

If you find this project helpful:

- 🌟 **Star** this repo
- 🧑‍💻 Contribute code or ideas
- 🐛 Report issues / suggest features
- 📣 Share with your team


**🗣️ Spread the word**: Share this project with your network operations and development teams!

**🤝 Get involved**: Join our community and help make SNMP parsing easier for everyone!