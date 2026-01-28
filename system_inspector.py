#!/usr/bin/env python3
"""
System Inspector Script

This script provides detailed information about the current system state,
including running processes, background services, resource usage, and system
information. Useful for understanding what might affect performance measurements.

Usage:
    python system_inspector.py

Requirements:
    pip install -r requirements.txt
"""

import time
import psutil
import platform
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple


def get_system_overview() -> Dict:
    """Get basic system information."""
    try:
        import psutil
    except ImportError:
        return {"error": "psutil not available"}

    info = {}

    # Basic system info
    info['hostname'] = platform.node()
    info['os'] = platform.system() + " " + platform.release()
    info['platform'] = platform.platform()
    info['python_version'] = sys.version.split()[0]
    info['psutil_version'] = psutil.__version__

    # CPU info
    info['cpu_count_logical'] = psutil.cpu_count(logical=True)
    info['cpu_count_physical'] = psutil.cpu_count(logical=False)
    try:
        cpu_freq = psutil.cpu_freq()
        info['cpu_freq_current'] = f"{cpu_freq.current:.0f}MHz" if cpu_freq else "N/A"
        info['cpu_freq_max'] = f"{cpu_freq.max:.0f}MHz" if cpu_freq else "N/A"
    except:
        info['cpu_freq_current'] = "N/A"
        info['cpu_freq_max'] = "N/A"

    # Memory info
    mem = psutil.virtual_memory()
    info['memory_total'] = f"{mem.total / (1024**3):.1f}GB"
    info['memory_available'] = f"{mem.available / (1024**3):.1f}GB"
    info['memory_used_percent'] = f"{mem.percent:.1f}%"

    # Disk info
    disk = psutil.disk_usage('/')
    info['disk_total'] = f"{disk.total / (1024**3):.1f}GB"
    info['disk_free'] = f"{disk.free / (1024**3):.1f}GB"
    info['disk_used_percent'] = f"{disk.percent:.1f}%"

    # Network info
    net = psutil.net_io_counters()
    info['network_bytes_sent'] = f"{net.bytes_sent / (1024**2):.1f}MB"
    info['network_bytes_recv'] = f"{net.bytes_recv / (1024**2):.1f}MB"

    return info


def get_resource_breakdown() -> Dict:
    """Get detailed resource consumption breakdown."""
    try:
        import psutil
    except ImportError:
        return {"error": "psutil not available"}

    breakdown = {}

    # Get all processes with detailed info
    processes = []
    total_cpu = 0
    total_memory = 0
    total_memory_bytes = 0

    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'memory_info', 'status']):
        try:
            info = proc.info
            if info['cpu_percent'] is not None and info['memory_percent'] is not None:
                cpu_usage = info['cpu_percent']
                memory_percent = info['memory_percent']
                memory_info = info.get('memory_info')

                processes.append({
                    'pid': info['pid'],
                    'name': info['name'] or 'Unknown',
                    'username': info['username'] or 'Unknown',
                    'cpu_percent': cpu_usage,
                    'memory_percent': memory_percent,
                    'memory_rss': memory_info.rss if memory_info else 0,
                    'status': info['status']
                })

                total_cpu += cpu_usage
                total_memory += memory_percent
                if memory_info:
                    total_memory_bytes += memory_info.rss

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Sort by CPU usage
    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)

    breakdown['processes'] = processes[:20]  # Top 20
    breakdown['total_cpu_used'] = total_cpu
    breakdown['total_memory_used_percent'] = total_memory
    breakdown['total_memory_used_bytes'] = total_memory_bytes

    # System totals
    system_memory = psutil.virtual_memory()
    breakdown['system_memory_total'] = system_memory.total
    breakdown['system_cpu_cores'] = psutil.cpu_count(logical=True)

    return breakdown
    """Get top processes by CPU and memory usage."""
    processes = []

    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
        try:
            info = proc.info
            if info['cpu_percent'] is not None and info['memory_percent'] is not None:
                processes.append({
                    'pid': info['pid'],
                    'name': info['name'] or 'Unknown',
                    'username': info['username'] or 'Unknown',
                    'cpu_percent': info['cpu_percent'],
                    'memory_percent': info['memory_percent'],
                    'status': info['status']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Sort by CPU usage first, then memory
    processes.sort(key=lambda x: (x['cpu_percent'], x['memory_percent']), reverse=True)
    return processes[:limit]


def get_background_services() -> List[Dict]:
    """Get information about background services/daemons."""
    services = []

    # On macOS, look for launchd services
    if platform.system() == 'Darwin':
        try:
            # Get launchctl list output
            import subprocess
            result = subprocess.run(['launchctl', 'list'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines[:20]:  # Limit to first 20
                    parts = line.split()
                    if len(parts) >= 3:
                        services.append({
                            'pid': parts[0] if parts[0] != '-' else 'N/A',
                            'status': parts[1],
                            'name': ' '.join(parts[2:])
                        })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            services.append({'error': 'Could not retrieve launchd services'})

    # On Linux, look for systemd services
    elif platform.system() == 'Linux':
        try:
            import subprocess
            result = subprocess.run(['systemctl', 'list-units', '--type=service', '--state=running'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[-20:]:  # Get last 20 lines (most recent)
                    if line.strip() and not line.startswith('UNIT'):
                        parts = line.split()
                        if len(parts) >= 4:
                            services.append({
                                'unit': parts[0],
                                'load': parts[1],
                                'active': parts[2],
                                'sub': parts[3],
                                'description': ' '.join(parts[4:]) if len(parts) > 4 else ''
                            })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            services.append({'error': 'Could not retrieve systemd services'})

    return services


def get_network_connections() -> List[Dict]:
    """Get current network connections."""
    connections = []

    try:
        for conn in psutil.net_connections(kind='inet')[:20]:  # Limit to 20
            connections.append({
                'fd': conn.fd,
                'family': str(conn.family),
                'type': str(conn.type),
                'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else 'N/A',
                'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else 'N/A',
                'status': conn.status,
                'pid': conn.pid or 'N/A'
            })
    except psutil.AccessDenied:
        connections.append({'error': 'Access denied to network connections'})

    return connections


def print_system_overview(info: Dict):
    """Print system overview information."""
    print("SYSTEM OVERVIEW")
    print("=" * 50)

    if "error" in info:
        print(f"Error: {info['error']}")
        return

    print(f"Hostname: {info.get('hostname', 'N/A')}")
    print(f"OS: {info.get('os', 'N/A')}")
    print(f"Platform: {info.get('platform', 'N/A')}")
    print(f"Python: {info.get('python_version', 'N/A')}")
    print(f"psutil: {info.get('psutil_version', 'N/A')}")
    print()

    print("HARDWARE:")
    print(f"CPU Cores: {info.get('cpu_count_physical', 'N/A')} physical, {info.get('cpu_count_logical', 'N/A')} logical")
    print(f"CPU Frequency: {info.get('cpu_freq_current', 'N/A')} (max: {info.get('cpu_freq_max', 'N/A')})")
    print(f"Memory: {info.get('memory_used_percent', 'N/A')} used ({info.get('memory_available', 'N/A')} available of {info.get('memory_total', 'N/A')})")
    print(f"Disk: {info.get('disk_used_percent', 'N/A')} used ({info.get('disk_free', 'N/A')} free of {info.get('disk_total', 'N/A')})")
    print()

    print("NETWORK:")
    print(f"Bytes Sent: {info.get('network_bytes_sent', 'N/A')}")
    print(f"Bytes Received: {info.get('network_bytes_recv', 'N/A')}")
    print()


def analyze_resource_consumption(breakdown: Dict):
    """Analyze and print detailed resource consumption analysis."""
    print("RESOURCE CONSUMPTION ANALYSIS")
    print("=" * 80)

    if "error" in breakdown:
        print(f"Error: {breakdown['error']}")
        return

    processes = breakdown['processes']
    total_cpu_used = breakdown['total_cpu_used']
    total_memory_used_percent = breakdown['total_memory_used_percent']
    total_memory_used_bytes = breakdown['total_memory_used_bytes']
    system_memory_total = breakdown['system_memory_total']
    system_cpu_cores = breakdown['system_cpu_cores']

    print("OVERALL SYSTEM LOAD:")
    print(f"Total CPU Usage: {total_cpu_used:.1f}% of {system_cpu_cores * 100}% available")
    print(f"Total Memory Usage: {total_memory_used_percent:.1f}% ({total_memory_used_bytes / (1024**3):.1f}GB of {system_memory_total / (1024**3):.1f}GB)")
    print()

    print("TOP RESOURCE CONSUMERS:")
    print("-" * 80)
    print(f"{'Process':<25} {'CPU%':<6} {'Mem%':<6} {'Mem(MB)':<8} {'Contribution'}")
    print("-" * 80)

    for proc in processes[:10]:  # Show top 10
        mem_mb = proc['memory_rss'] / (1024**2) if proc['memory_rss'] else 0
        cpu_contrib = (proc['cpu_percent'] / total_cpu_used * 100) if total_cpu_used > 0 else 0
        mem_contrib = (proc['memory_percent'] / total_memory_used_percent * 100) if total_memory_used_percent > 0 else 0

        name = proc['name'][:24] if len(proc['name']) > 24 else proc['name']
        print(f"{name:<25} {proc['cpu_percent']:<6.1f} {proc['memory_percent']:<6.1f} {mem_mb:<8.0f} CPU:{cpu_contrib:.1f}%, Mem:{mem_contrib:.1f}%")

    print()
    print("PERFORMANCE IMPACT ANALYSIS:")
    print("-" * 80)

    # CPU Analysis
    if total_cpu_used < 20:
        cpu_status = "LOW - System has plenty of CPU headroom"
    elif total_cpu_used < 70:
        cpu_status = "MODERATE - Some CPU pressure, may affect performance"
    else:
        cpu_status = "HIGH - CPU bottleneck likely affecting performance"

    # Memory Analysis
    if total_memory_used_percent < 50:
        mem_status = "LOW - Ample memory available"
    elif total_memory_used_percent < 80:
        mem_status = "MODERATE - Memory pressure may cause swapping"
    else:
        mem_status = "HIGH - Memory bottleneck, likely causing performance issues"

    print(f"CPU Load: {cpu_status}")
    print(f"Memory Load: {mem_status}")
    print()

    # Recommendations
    print("RECOMMENDATIONS:")
    if total_cpu_used > 50:
        print("- Consider closing CPU-intensive applications before benchmarking")
    if total_memory_used_percent > 70:
        print("- High memory usage may cause swapping - close memory-intensive apps")
    if len([p for p in processes if p['cpu_percent'] > 10]) > 3:
        print("- Multiple high-CPU processes detected - may interfere with measurements")

    print(f"- System has {system_cpu_cores} CPU cores total")
    print(f"- {len(processes)} processes monitored")
    print()


def print_background_services(services: List[Dict]):
    """Print background services information."""
    print("BACKGROUND SERVICES")
    print("=" * 80)

    if not services:
        print("No background services information available.")
        print()
        return

    if "error" in services[0]:
        print(f"Error: {services[0]['error']}")
        print()
        return

    if platform.system() == 'Darwin':
        print(f"{'PID':<10} {'Status':<8} {'Service Name'}")
        print("-" * 80)
        for service in services:
            name = service['name'][:50] if len(service['name']) > 50 else service['name']
            print(f"{service['pid']:<10} {service['status']:<8} {name}")
    elif platform.system() == 'Linux':
        print(f"{'Unit':<30} {'Load':<8} {'Active':<8} {'Sub':<8} {'Description'}")
        print("-" * 80)
        for service in services:
            unit = service['unit'][:29] if len(service['unit']) > 29 else service['unit']
            desc = service['description'][:30] if len(service['description']) > 30 else service['description']
            print(f"{unit:<30} {service['load']:<8} {service['active']:<8} {service['sub']:<8} {desc}")
    print()


def print_network_connections(connections: List[Dict]):
    """Print network connections information."""
    print("NETWORK CONNECTIONS")
    print("=" * 80)

    if not connections:
        print("No network connections found.")
        print()
        return

    if "error" in connections[0]:
        print(f"Error: {connections[0]['error']}")
        print()
        return

    print(f"{'PID':<8} {'Local Address':<22} {'Remote Address':<22} {'Status':<12}")
    print("-" * 80)

    for conn in connections:
        local = conn.get('local_addr', 'N/A')[:21]  # Truncate long addresses
        remote = conn.get('remote_addr', 'N/A')[:21]
        status = conn.get('status', 'N/A')[:11]
        print(f"{conn.get('pid', 'N/A'):<8} {local:<22} {remote:<22} {status:<12}")
    print()


def save_inspection_report():
    """Save the inspection report to a file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"system_inspection_{timestamp}.txt"
    filepath = os.path.join("inspection_reports", filename)

    # Create directory if it doesn't exist
    os.makedirs("inspection_reports", exist_ok=True)

    # Redirect stdout to file
    original_stdout = sys.stdout
    with open(filepath, 'w') as f:
        sys.stdout = f

        print(f"System Inspection Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()

        # Get and print all information
        overview = get_system_overview()
        print_system_overview(overview)

        breakdown = get_resource_breakdown()
        analyze_resource_consumption(breakdown)

        services = get_background_services()
        print_background_services(services)

        connections = get_network_connections()
        print_network_connections(connections)

        print("Report saved successfully.")

    sys.stdout = original_stdout
    print(f"Inspection report saved to: {filepath}")


def main():
    """Main function to run the system inspection."""
    print("System Inspector - Detailed System State Analysis")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check if psutil is available
    try:
        import psutil
    except ImportError:
        print("Error: psutil library not found. Please run: pip install -r requirements.txt")
        return

    # Get and display system information
    overview = get_system_overview()
    print_system_overview(overview)

    breakdown = get_resource_breakdown()
    analyze_resource_consumption(breakdown)

    services = get_background_services()
    print_background_services(services)

    connections = get_network_connections()
    print_network_connections(connections)

    # Save report
    save_inspection_report()

    print("System inspection complete. Use this information to understand")
    print("what processes and services might affect your performance measurements.")


if __name__ == "__main__":
    main()