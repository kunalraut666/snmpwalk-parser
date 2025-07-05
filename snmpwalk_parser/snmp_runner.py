import subprocess
import shutil
import ipaddress
from typing import Optional, List, Dict, Any, Union
from snmpwalk_parser.models import SNMPWalkResult, SNMPError
from snmpwalk_parser.core import SNMPParser
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class SNMPRunner:
    """Enhanced SNMP runner with advanced features."""
    
    def __init__(self, timeout: int = 30, retries: int = 3):
        """Initialize SNMP runner."""
        self.timeout = timeout
        self.retries = retries
        self.parser = SNMPParser()
        self._check_snmp_tools()
    
    def _check_snmp_tools(self):
        """Check if SNMP tools are available."""
        tools = ['snmpwalk', 'snmpget', 'snmpset', 'snmpbulkwalk']
        missing = []
        
        for tool in tools:
            if not shutil.which(tool):
                missing.append(tool)
        
        if missing:
            print(f"Warning: Missing SNMP tools: {', '.join(missing)}")
    
    def run_snmpwalk(self, 
                     host: str, 
                     community: str = 'public',
                     oid: str = '',
                     version: str = '2c',
                     timeout: Optional[int] = None,
                     retries: Optional[int] = None) -> SNMPWalkResult:
        """Enhanced snmpwalk with better error handling and result processing."""
        
        # Validate inputs
        self._validate_inputs(host, community, version)
        
        timeout = timeout or self.timeout
        retries = retries or self.retries
        
        # Build command
        cmd = self._build_snmpwalk_command(host, community, oid, version, timeout)
        
        # Execute with retries
        output = self._execute_with_retries(cmd, retries)
        
        # Parse output
        entries = self.parser.parse_snmpwalk_output(output)
        
        # Create result
        result = SNMPWalkResult(
            host=host,
            community=community,
            oid=oid
        )
        
        for entry in entries:
            result.add_entry(entry)
        
        # Extract system info
        result.system_info = self.parser.get_system_info(entries)
        
        return result
    
    def run_snmpget(self,
                   host: str,
                   community: str = 'public',
                   oids: Union[str, List[str]] = '',
                   version: str = '2c',
                   timeout: Optional[int] = None) -> SNMPWalkResult:
        """Run snmpget for specific OIDs."""
        
        self._validate_inputs(host, community, version)
        
        if isinstance(oids, str):
            oids = [oids] if oids else []
        
        timeout = timeout or self.timeout
        
        cmd = ['snmpget', f'-v{version}', '-c', community, '-t', str(timeout), host]
        cmd.extend(oids)
        
        output = self._execute_command(cmd)
        entries = self.parser.parse_snmpwalk_output(output)
        
        result = SNMPWalkResult(
            host=host,
            community=community,
            oid=','.join(oids)
        )
        
        for entry in entries:
            result.add_entry(entry)
        
        return result
    
    def run_snmpbulkwalk(self,
                        host: str,
                        community: str = 'public',
                        oid: str = '',
                        version: str = '2c',
                        max_repetitions: int = 10,
                        timeout: Optional[int] = None) -> SNMPWalkResult:
        """Run snmpbulkwalk for faster bulk operations."""
        
        if version == '1':
            # SNMPv1 doesn't support bulk, fallback to regular walk
            return self.run_snmpwalk(host, community, oid, version, timeout)
        
        self._validate_inputs(host, community, version)
        
        timeout = timeout or self.timeout
        
        cmd = [
            'snmpbulkwalk',
            f'-v{version}',
            '-c', community,
            '-t', str(timeout),
            '-Cr', str(max_repetitions),
            host
        ]
        
        if oid:
            cmd.append(oid)
        
        output = self._execute_command(cmd)
        entries = self.parser.parse_snmpwalk_output(output)
        
        result = SNMPWalkResult(
            host=host,
            community=community,
            oid=oid
        )
        
        for entry in entries:
            result.add_entry(entry)
        
        result.system_info = self.parser.get_system_info(entries)
        
        return result
    
    def run_parallel_snmpwalk(self,
                             hosts: List[str],
                             community: str = 'public',
                             oid: str = '',
                             version: str = '2c',
                             max_workers: int = 10) -> Dict[str, Union[SNMPWalkResult, SNMPError]]:
        """Run snmpwalk on multiple hosts in parallel."""
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_host = {
                executor.submit(self.run_snmpwalk, host, community, oid, version): host
                for host in hosts
            }
            
            # Collect results
            for future in as_completed(future_to_host):
                host = future_to_host[future]
                try:
                    result = future.result()
                    results[host] = result
                except Exception as e:
                    results[host] = SNMPError(
                        code=1,
                        message=str(e),
                        details=f"Failed to query host {host}"
                    )
        
        return results
    
    def discover_snmp_hosts(self,
                           network: str,
                           community: str = 'public',
                           timeout: int = 5) -> List[str]:
        """Discover SNMP-enabled hosts in a network."""
        
        try:
            net = ipaddress.ip_network(network, strict=False)
        except ValueError:
            raise ValueError(f"Invalid network: {network}")
        
        hosts = []
        
        def check_host(host_ip):
            try:
                result = self.run_snmpwalk(
                    str(host_ip),
                    community,
                    'sysDescr',
                    timeout=timeout
                )
                if result.get_entry_count() > 0:
                    return str(host_ip)
            except:
                pass
            return None
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            future_to_host = {
                executor.submit(check_host, host): host
                for host in net.hosts()
            }
            
            for future in as_completed(future_to_host):
                result = future.result()
                if result:
                    hosts.append(result)
        
        return hosts
    
    def _validate_inputs(self, host: str, community: str, version: str):
        """Validate input parameters."""
        if not host:
            raise ValueError("Host cannot be empty")
        
        if not community:
            raise ValueError("Community cannot be empty")
        
        if version not in ['1', '2c', '3']:
            raise ValueError(f"Invalid SNMP version: {version}")
        
        # Basic IP/hostname validation
        try:
            ipaddress.ip_address(host)
        except ValueError:
            # Not an IP, assume hostname - basic validation
            if not host.replace('.', '').replace('-', '').replace('_', '').isalnum():
                raise ValueError(f"Invalid host: {host}")
    
    def _build_snmpwalk_command(self, host: str, community: str, oid: str, version: str, timeout: int) -> List[str]:
        """Build snmpwalk command."""
        cmd = [
            'snmpwalk',
            f'-v{version}',
            '-c', community,
            '-t', str(timeout),
            '-r', str(self.retries),
            '-On',  # Numeric OIDs
            '-Oq',  # Quick print
            host
        ]
        
        if oid:
            cmd.append(oid)
        
        return cmd
    
    def _execute_with_retries(self, cmd: List[str], retries: int) -> str:
        """Execute command with retries."""
        last_error = None
        
        for attempt in range(retries + 1):
            try:
                return self._execute_command(cmd)
            except RuntimeError as e:
                last_error = e
                if attempt < retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
        
        raise last_error
    
    def _execute_command(self, cmd: List[str]) -> str:
        """Execute command and return output."""
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                raise RuntimeError(f"SNMP command failed: {error_msg}")
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"SNMP command timed out after {self.timeout} seconds")
        except Exception as e:
            raise RuntimeError(f"SNMP command error: {str(e)}")

# Convenience functions for backward compatibility
def run_snmpwalk(host: str, community: str, oid: str = '', version: str = '2c') -> str:
    """Run snmpwalk - backward compatible function."""
    runner = SNMPRunner()
    result = runner.run_snmpwalk(host, community, oid, version)
    return result.to_json()

def run_snmpget(host: str, community: str, oids: Union[str, List[str]], version: str = '2c') -> str:
    """Run snmpget - convenience function."""
    runner = SNMPRunner()
    result = runner.run_snmpget(host, community, oids, version)
    return result.to_json()