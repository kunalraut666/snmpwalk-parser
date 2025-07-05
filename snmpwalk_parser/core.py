import re
from typing import List, Dict, Any, Optional, Union
from snmpwalk_parser.models import SNMPEntry, SNMPTable
import ipaddress

class SNMPParser:
    """Enhanced SNMP parser with multiple output format support."""
    
    def __init__(self):
        # Multiple regex patterns for different snmpwalk output formats
        self.patterns = [
            # Standard format: OID = TYPE: VALUE
            re.compile(r'(?P<oid>[\w\-\.]+(?:::[\w\-\.]+)?(?:\.\d+)*)\s*=\s*(?P<type>\w+):\s*(?P<value>.*?)(?:\s*$)', re.MULTILINE),
            
            # Numeric OID format: .1.3.6.1.2.1.1.1.0 = STRING: "value"
            re.compile(r'(?P<oid>\.[\d\.]+)\s*=\s*(?P<type>\w+):\s*(?P<value>.*?)(?:\s*$)', re.MULTILINE),
            
            # Mixed format with quotes: iso.3.6.1.2.1.1.1.0 = STRING: "System Description"
            re.compile(r'(?P<oid>(?:iso|enterprises|[\w\-]+)[\.\w\-]*(?:\.\d+)*)\s*=\s*(?P<type>\w+):\s*(?P<value>.*?)(?:\s*$)', re.MULTILINE),
            
            # No space format: OID=TYPE:VALUE
            re.compile(r'(?P<oid>[\w\-\.]+(?:::[\w\-\.]+)?(?:\.\d+)*)\s*=\s*(?P<type>\w+):\s*(?P<value>.*?)(?:\s*$)', re.MULTILINE)
        ]
        
        # Common SNMP type mappings
        self.type_processors = {
            'STRING': self._process_string,
            'INTEGER': self._process_integer,
            'COUNTER': self._process_counter,
            'COUNTER32': self._process_counter,
            'COUNTER64': self._process_counter,
            'GAUGE': self._process_gauge,
            'GAUGE32': self._process_gauge,
            'TIMETICKS': self._process_timeticks,
            'IPADDRESS': self._process_ip_address,
            'OBJECTIDENTIFIER': self._process_oid,
            'OCTETSTRING': self._process_octet_string,
            'BITS': self._process_bits,
            'OPAQUE': self._process_opaque,
        }

    def parse_snmpwalk_output(self, text: str) -> List[SNMPEntry]:
        """Parse snmpwalk output with enhanced pattern matching."""
        result = []
        
        for line in text.strip().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            entry = self._parse_line(line)
            if entry:
                result.append(entry)
        
        return result

    def _parse_line(self, line: str) -> Optional[SNMPEntry]:
        """Parse a single line using multiple regex patterns."""
        for pattern in self.patterns:
            match = pattern.match(line)
            if match:
                try:
                    return self._create_entry(match)
                except Exception as e:
                    # Log error but continue parsing
                    print(f"Warning: Failed to parse line '{line}': {e}")
                    continue
        
        return None

    def _create_entry(self, match) -> SNMPEntry:
        """Create SNMPEntry from regex match."""
        full_oid = match.group('oid')
        value_type = match.group('type').upper()
        raw_value = match.group('value').strip()
        
        # Process the value based on type
        processed_value = self._process_value(value_type, raw_value)
        
        # Extract key and index from OID
        key, index = self._extract_key_index(full_oid)
        
        return SNMPEntry(
            oid=full_oid,
            key=key,
            index=index,
            type=value_type,
            value=processed_value,
            raw_value=raw_value
        )

    def _extract_key_index(self, oid: str) -> tuple[str, str]:
        """Extract key and index from OID."""
        if '::' in oid:
            # Named OID format
            parts = oid.split('::')
            if len(parts) >= 2:
                key_part = parts[1]
                if '.' in key_part:
                    key, index = key_part.rsplit('.', 1)
                    return key, index
                return key_part, '0'
        else:
            # Numeric OID format
            parts = oid.split('.')
            if len(parts) > 1:
                return '.'.join(parts[:-1]), parts[-1]
        
        return oid, '0'

    def _process_value(self, value_type: str, raw_value: str) -> Any:
        """Process value based on SNMP type."""
        processor = self.type_processors.get(value_type, self._process_default)
        return processor(raw_value)

    def _process_string(self, value: str) -> str:
        """Process STRING type."""
        # Remove quotes if present
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        return value

    def _process_integer(self, value: str) -> int:
        """Process INTEGER type."""
        # Handle enumerated values like "up(1)" or "active(1)"
        if '(' in value and ')' in value:
            # Extract number from parentheses
            match = re.search(r'\((\d+)\)', value)
            if match:
                return int(match.group(1))
        
        # Handle simple integers
        try:
            return int(value)
        except ValueError:
            return 0

    def _process_counter(self, value: str) -> int:
        """Process COUNTER/COUNTER32/COUNTER64 types."""
        try:
            return int(value)
        except ValueError:
            return 0

    def _process_gauge(self, value: str) -> int:
        """Process GAUGE/GAUGE32 types."""
        try:
            return int(value)
        except ValueError:
            return 0

    def _process_timeticks(self, value: str) -> Dict[str, Union[int, str]]:
        """Process TIMETICKS type."""
        # Format: (12345) 2:03:45.67
        match = re.match(r'\((\d+)\)\s*(.*)', value)
        if match:
            ticks = int(match.group(1))
            time_str = match.group(2)
            return {
                'ticks': ticks,
                'time_string': time_str,
                'seconds': ticks / 100  # Convert to seconds
            }
        return {'ticks': 0, 'time_string': value, 'seconds': 0}

    def _process_ip_address(self, value: str) -> str:
        """Process IPADDRESS type."""
        try:
            # Validate IP address
            ipaddress.ip_address(value)
            return value
        except ValueError:
            return value

    def _process_oid(self, value: str) -> str:
        """Process OBJECTIDENTIFIER type."""
        return value

    def _process_octet_string(self, value: str) -> str:
        """Process OCTETSTRING type."""
        # Handle hex strings
        if value.startswith('0x'):
            return value
        return self._process_string(value)

    def _process_bits(self, value: str) -> str:
        """Process BITS type."""
        return value

    def _process_opaque(self, value: str) -> str:
        """Process OPAQUE type."""
        return value

    def _process_default(self, value: str) -> str:
        """Default processor for unknown types."""
        return value

    def group_by_table(self, entries: List[SNMPEntry]) -> Dict[str, SNMPTable]:
        """Group entries by table (base key)."""
        tables = {}
        
        for entry in entries:
            if entry.key not in tables:
                tables[entry.key] = SNMPTable(
                    name=entry.key,
                    entries=[]
                )
            tables[entry.key].entries.append(entry)
        
        return tables

    def filter_by_oid_pattern(self, entries: List[SNMPEntry], pattern: str) -> List[SNMPEntry]:
        """Filter entries by OID pattern."""
        regex = re.compile(pattern)
        return [entry for entry in entries if regex.search(entry.oid)]

    def get_system_info(self, entries: List[SNMPEntry]) -> Dict[str, Any]:
        """Extract common system information."""
        system_info = {}
        
        # Common system OIDs
        system_oids = {
            'sysDescr': 'system_description',
            'sysUpTime': 'system_uptime',
            'sysContact': 'system_contact',
            'sysName': 'system_name',
            'sysLocation': 'system_location',
            'sysServices': 'system_services'
        }
        
        for entry in entries:
            for oid_key, info_key in system_oids.items():
                if oid_key in entry.oid:
                    system_info[info_key] = entry.value
        
        return system_info

    def get_interface_info(self, entries: List[SNMPEntry]) -> List[Dict[str, Any]]:
        """Extract interface information."""
        interfaces = {}
        
        for entry in entries:
            if 'ifIndex' in entry.oid or 'ifDescr' in entry.oid or 'ifSpeed' in entry.oid:
                if entry.index not in interfaces:
                    interfaces[entry.index] = {'index': entry.index}
                
                if 'ifDescr' in entry.oid:
                    interfaces[entry.index]['description'] = entry.value
                elif 'ifSpeed' in entry.oid:
                    interfaces[entry.index]['speed'] = entry.value
                elif 'ifOperStatus' in entry.oid:
                    interfaces[entry.index]['status'] = entry.value
        
        return list(interfaces.values())

    def parse_file(self, file_path: str):
        """Parses SNMP output from a file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return self.parse_snmpwalk_output(content)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to parse file: {file_path}\nError: {e}")
        
# Convenience function for backward compatibility
def parse_snmpwalk_output(text: str) -> List[SNMPEntry]:
    """Parse snmpwalk output - backward compatible function."""
    parser = SNMPParser()
    return parser.parse_snmpwalk_output(text)