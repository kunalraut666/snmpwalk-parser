from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
import json

@dataclass
class SNMPEntry:
    """Represents a single SNMP entry from snmpwalk output."""
    oid: str
    key: str
    index: str
    type: str
    value: Any
    raw_value: str = ""
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.raw_value:
            self.raw_value = str(self.value)
    
    def is_numeric_oid(self) -> bool:
        """Check if OID is in numeric format."""
        return self.oid.startswith('.') or self.oid.startswith('iso.')
    
    def is_named_oid(self) -> bool:
        """Check if OID is in named format."""
        return '::' in self.oid
    
    def get_table_name(self) -> str:
        """Get the table name from the OID."""
        if self.is_named_oid():
            return self.oid.split('::')[0]
        return self.key.split('.')[0] if '.' in self.key else self.key
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'oid': self.oid,
            'key': self.key,
            'index': self.index,
            'type': self.type,
            'value': self.value,
            'raw_value': self.raw_value
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

@dataclass
class SNMPTable:
    """Represents a collection of SNMP entries forming a table."""
    name: str
    entries: List[SNMPEntry] = field(default_factory=list)
    
    def __len__(self) -> int:
        """Return number of entries in the table."""
        return len(self.entries)
    
    def __iter__(self):
        """Make table iterable."""
        return iter(self.entries)
    
    def add_entry(self, entry: SNMPEntry):
        """Add an entry to the table."""
        self.entries.append(entry)
    
    def get_by_index(self, index: str) -> Optional[SNMPEntry]:
        """Get entry by index."""
        for entry in self.entries:
            if entry.index == index:
                return entry
        return None
    
    def get_indices(self) -> List[str]:
        """Get all indices in the table."""
        return [entry.index for entry in self.entries]
    
    def get_values(self) -> List[Any]:
        """Get all values in the table."""
        return [entry.value for entry in self.entries]
    
    def get_types(self) -> List[str]:
        """Get all types in the table."""
        return list(set(entry.type for entry in self.entries))
    
    def filter_by_type(self, snmp_type: str) -> List[SNMPEntry]:
        """Filter entries by SNMP type."""
        return [entry for entry in self.entries if entry.type == snmp_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert table to dictionary."""
        return {
            'name': self.name,
            'count': len(self.entries),
            'entries': [entry.to_dict() for entry in self.entries]
        }
    
    def to_json(self) -> str:
        """Convert table to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def to_csv_rows(self) -> List[Dict[str, Any]]:
        """Convert table to CSV-ready rows."""
        return [entry.to_dict() for entry in self.entries]

@dataclass
class SNMPWalkResult:
    """Complete result of an SNMP walk operation."""
    host: str
    community: str
    oid: str
    entries: List[SNMPEntry] = field(default_factory=list)
    tables: Dict[str, SNMPTable] = field(default_factory=dict)
    system_info: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.timestamp:
            from datetime import datetime
            self.timestamp = datetime.now().isoformat()
    
    def get_entry_count(self) -> int:
        """Get total number of entries."""
        return len(self.entries)
    
    def get_table_count(self) -> int:
        """Get number of tables."""
        return len(self.tables)
    
    def get_table_names(self) -> List[str]:
        """Get all table names."""
        return list(self.tables.keys())
    
    def get_table(self, name: str) -> Optional[SNMPTable]:
        """Get table by name."""
        return self.tables.get(name)
    
    def add_entry(self, entry: SNMPEntry):
        """Add an entry to the result."""
        self.entries.append(entry)
        
        # Update tables
        table_name = entry.get_table_name()
        if table_name not in self.tables:
            self.tables[table_name] = SNMPTable(name=table_name)
        self.tables[table_name].add_entry(entry)
    
    def filter_by_oid_pattern(self, pattern: str) -> List[SNMPEntry]:
        """Filter entries by OID pattern."""
        import re
        regex = re.compile(pattern)
        return [entry for entry in self.entries if regex.search(entry.oid)]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        types = {}
        for entry in self.entries:
            types[entry.type] = types.get(entry.type, 0) + 1
        
        return {
            'host': self.host,
            'community': self.community,
            'oid': self.oid,
            'timestamp': self.timestamp,
            'total_entries': len(self.entries),
            'total_tables': len(self.tables),
            'table_names': list(self.tables.keys()),
            'entry_types': types
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'host': self.host,
            'community': self.community,
            'oid': self.oid,
            'timestamp': self.timestamp,
            'entries': [entry.to_dict() for entry in self.entries],
            'tables': {name: table.to_dict() for name, table in self.tables.items()},
            'system_info': self.system_info,
            'summary': self.get_summary()
        }
    
    def to_json(self) -> str:
        """Convert result to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def export_to_file(self, filename: str, format: str = 'json'):
        """Export result to file."""
        if format.lower() == 'json':
            with open(filename, 'w') as f:
                f.write(self.to_json())
        elif format.lower() == 'csv':
            import csv
            with open(filename, 'w', newline='') as f:
                if self.entries:
                    writer = csv.DictWriter(f, fieldnames=self.entries[0].to_dict().keys())
                    writer.writeheader()
                    for entry in self.entries:
                        writer.writerow(entry.to_dict())
        else:
            raise ValueError(f"Unsupported format: {format}")

@dataclass
class SNMPError:
    """Represents an SNMP error."""
    code: int
    message: str
    details: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of the error."""
        return f"SNMP Error {self.code}: {self.message}"