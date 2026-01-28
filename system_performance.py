#!/usr/bin/env python3
"""
System Performance Baseline Measurement Script

This script establishes a clear and reliable understanding of laptop performance by measuring:
- CPU usage (system-wide)
- Memory consumption
- Execution time for workloads

It distinguishes idle behavior from load-induced behavior, captures peak resource usage,
and ensures measurements are reproducible and meaningful.

Usage:
    python system_performance.py

Requirements:
    pip install -r requirements.txt
"""

import time
import threading
import statistics
import os
import platform
import sys
from typing import List, Tuple
from datetime import datetime


def get_system_specs() -> dict:
    """Get system specifications for logging."""
    try:
        import psutil
    except ImportError:
        return {"error": "psutil not available"}

    specs = {}

    # OS Information
    specs['os'] = platform.system() + " " + platform.release()
    specs['platform'] = platform.platform()

    # CPU Information
    specs['cpu_count'] = psutil.cpu_count(logical=True)
    specs['cpu_count_physical'] = psutil.cpu_count(logical=False)
    try:
        cpu_freq = psutil.cpu_freq()
        specs['cpu_freq_current'] = f"{cpu_freq.current:.0f}MHz" if cpu_freq else "N/A"
        specs['cpu_freq_max'] = f"{cpu_freq.max:.0f}MHz" if cpu_freq else "N/A"
    except:
        specs['cpu_freq_current'] = "N/A"
        specs['cpu_freq_max'] = "N/A"

    # Memory Information
    mem = psutil.virtual_memory()
    specs['memory_total'] = f"{mem.total / (1024**3):.1f}GB"

    # Python Information
    specs['python_version'] = sys.version.split()[0]

    # psutil version
    specs['psutil_version'] = psutil.__version__

    return specs


def get_system_metrics() -> Tuple[float, float]:
    """
    Get current system CPU and memory usage.

    Returns:
        Tuple of (cpu_percent, memory_percent)
    """
    try:
        import psutil
    except ImportError:
        print("Error: psutil library not found. Please run: pip install -r requirements.txt")
        return 0.0, 0.0
    cpu_percent = psutil.cpu_percent(interval=None)  # Instantaneous
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    return cpu_percent, memory_percent


def measure_idle_baseline(duration_seconds: int = 10, sample_interval: float = 1.0) -> dict:
    """
    Measure system metrics during idle period.

    This establishes a baseline of system behavior when not under load.
    We sample over a period to account for natural system fluctuations.

    Args:
        duration_seconds: How long to measure (default 10s for stability)
        sample_interval: Time between samples (1s to balance accuracy and overhead)

    Returns:
        Dict with average and peak metrics, plus raw samples for analysis
    """
    print(f"Measuring idle baseline for {duration_seconds} seconds...")
    cpu_samples = []
    memory_samples = []

    start_time = time.time()
    while time.time() - start_time < duration_seconds:
        cpu, mem = get_system_metrics()
        cpu_samples.append(cpu)
        memory_samples.append(mem)
        time.sleep(sample_interval)

    return {
        'average_cpu': statistics.mean(cpu_samples),
        'peak_cpu': max(cpu_samples),
        'average_memory': statistics.mean(memory_samples),
        'peak_memory': max(memory_samples),
        'cpu_samples': cpu_samples,  # Keep raw data for potential further analysis
        'memory_samples': memory_samples
    }


def cpu_intensive_task() -> int:
    """
    Reproducible CPU-intensive task: Calculate primes up to a limit.

    This task is designed to be computationally intensive enough to stress the CPU
    for a measurable duration (1-2 seconds on typical hardware), allowing us to
    observe system behavior under load.

    Returns:
        Number of primes found
    """
    limit = 200000  
    primes = []
    for num in range(2, limit + 1):
        is_prime = True
        for i in range(2, int(num**0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return len(primes)


def run_load_test() -> dict:
    """
    Run CPU-intensive task while monitoring system metrics.

    This function runs the workload in a separate thread while continuously
    monitoring system resources. The high-frequency sampling (every 500ms)
    ensures we capture peak usage during the task execution.

    Returns:
        Dict with execution time and metrics during load
    """
    print("Running CPU-intensive load test...")

    cpu_samples = []
    memory_samples = []
    monitoring = True

    def monitor_system():
        """Background monitoring thread to collect system metrics."""
        while monitoring:
            cpu, mem = get_system_metrics()
            cpu_samples.append(cpu)
            memory_samples.append(mem)
            time.sleep(0.5)  # Sample every 500ms for peak detection

    # Start monitoring in background
    monitor_thread = threading.Thread(target=monitor_system)
    monitor_thread.start()

    # Run the task
    start_time = time.time()
    primes_found = cpu_intensive_task()
    execution_time = time.time() - start_time

    # Stop monitoring
    monitoring = False
    monitor_thread.join()

    print(f"Found {primes_found} primes in {execution_time:.2f} seconds")

    return {
        'execution_time': execution_time,
        'primes_found': primes_found,
        'average_cpu': statistics.mean(cpu_samples),
        'peak_cpu': max(cpu_samples),
        'average_memory': statistics.mean(memory_samples),
        'peak_memory': max(memory_samples),
        'cpu_samples': cpu_samples,
        'memory_samples': memory_samples
    }


def print_results(idle_metrics: dict, load_metrics: dict):
    """Print formatted results."""
    print("\n" + "="*60)
    print("SYSTEM PERFORMANCE BASELINE RESULTS")
    print("="*60)

    print("\nIDLE BASELINE (10 seconds):")
    print(f"Average CPU Usage: {idle_metrics['average_cpu']:.2f}%")
    print(f"Peak CPU Usage: {idle_metrics['peak_cpu']:.2f}%")
    print(f"Average Memory Usage: {idle_metrics['average_memory']:.2f}%")
    print(f"Peak Memory Usage: {idle_metrics['peak_memory']:.2f}%")

    print("\nLOAD TEST RESULTS:")
    print(f"Execution Time: {load_metrics['execution_time']:.2f} seconds")
    print(f"Average CPU Usage: {load_metrics['average_cpu']:.2f}%")
    print(f"Peak CPU Usage: {load_metrics['peak_cpu']:.2f}%")
    print(f"Average Memory Usage: {load_metrics['average_memory']:.2f}%")
    print(f"Peak Memory Usage: {load_metrics['peak_memory']:.2f}%")

    print("\nPERFORMANCE IMPACT:")
    cpu_increase = load_metrics['average_cpu'] - idle_metrics['average_cpu']
    memory_increase = load_metrics['average_memory'] - idle_metrics['average_memory']
    print(f"CPU Usage Increase: {cpu_increase:.2f}%")
    print(f"Memory Usage Increase: {memory_increase:.2f}%")

    print("\nREPRODUCIBILITY NOTES:")
    print("- CPU task: Prime calculation up to 200,000")
    print("- Idle measurement: 10 seconds with 1s intervals")
    print("- Load monitoring: 500ms intervals during execution")
    print("- All measurements use system-wide metrics")

    print("\nEXPLANATION:")
    print("- Idle baseline shows normal system usage when not under load")
    print("- Load test demonstrates system response to CPU-intensive work")
    print("- Peak values capture maximum resource usage during execution")
    print("- Performance impact shows the difference between idle and loaded states")
    print("- Low memory impact is expected for CPU-bound tasks like prime calculation")


def save_results_to_file(idle_metrics: dict, load_metrics: dict):
    """Save results to a timestamped log file in results folder."""
    # Create results directory if it doesn't exist
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)

    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"performance_baseline_{timestamp}.txt"
    filepath = os.path.join(results_dir, filename)

    # Get system specifications
    system_specs = get_system_specs()

    with open(filepath, 'w') as f:
        f.write("SYSTEM PERFORMANCE BASELINE RESULTS\n")
        f.write("="*60 + "\n\n")

        f.write("SYSTEM SPECIFICATIONS\n")
        f.write("-"*30 + "\n")
        if "error" in system_specs:
            f.write(f"Error getting specs: {system_specs['error']}\n")
        else:
            f.write(f"Operating System: {system_specs.get('os', 'N/A')}\n")
            f.write(f"Platform: {system_specs.get('platform', 'N/A')}\n")
            f.write(f"CPU Cores (Logical): {system_specs.get('cpu_count', 'N/A')}\n")
            f.write(f"CPU Cores (Physical): {system_specs.get('cpu_count_physical', 'N/A')}\n")
            f.write(f"CPU Frequency (Current): {system_specs.get('cpu_freq_current', 'N/A')}\n")
            f.write(f"CPU Frequency (Max): {system_specs.get('cpu_freq_max', 'N/A')}\n")
            f.write(f"Memory (Total): {system_specs.get('memory_total', 'N/A')}\n")
            f.write(f"Python Version: {system_specs.get('python_version', 'N/A')}\n")
            f.write(f"psutil Version: {system_specs.get('psutil_version', 'N/A')}\n")
        f.write("\n")

        f.write("TIMESTAMP: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")

        f.write("IDLE BASELINE (10 seconds):\n")
        f.write(f"Average CPU Usage: {idle_metrics['average_cpu']:.2f}%\n")
        f.write(f"Peak CPU Usage: {idle_metrics['peak_cpu']:.2f}%\n")
        f.write(f"Average Memory Usage: {idle_metrics['average_memory']:.2f}%\n")
        f.write(f"Peak Memory Usage: {idle_metrics['peak_memory']:.2f}%\n\n")

        f.write("LOAD TEST RESULTS:\n")
        f.write(f"Execution Time: {load_metrics['execution_time']:.2f} seconds\n")
        f.write(f"Primes Found: {load_metrics['primes_found']}\n")
        f.write(f"Average CPU Usage: {load_metrics['average_cpu']:.2f}%\n")
        f.write(f"Peak CPU Usage: {load_metrics['peak_cpu']:.2f}%\n")
        f.write(f"Average Memory Usage: {load_metrics['average_memory']:.2f}%\n")
        f.write(f"Peak Memory Usage: {load_metrics['peak_memory']:.2f}%\n\n")

        cpu_increase = load_metrics['average_cpu'] - idle_metrics['average_cpu']
        memory_increase = load_metrics['average_memory'] - idle_metrics['average_memory']
        f.write("PERFORMANCE IMPACT:\n")
        f.write(f"CPU Usage Increase: {cpu_increase:.2f}%\n")
        f.write(f"Memory Usage Increase: {memory_increase:.2f}%\n\n")

        f.write("REPRODUCIBILITY NOTES:\n")
        f.write("- CPU task: Prime calculation up to 200,000\n")
        f.write("- Idle measurement: 10 seconds with 1s intervals\n")
        f.write("- Load monitoring: 500ms intervals during execution\n")
        f.write("- All measurements use system-wide metrics\n\n")

        f.write("RAW DATA:\n")
        f.write(f"Idle CPU Samples: {idle_metrics['cpu_samples']}\n")
        f.write(f"Idle Memory Samples: {idle_metrics['memory_samples']}\n")
        f.write(f"Load CPU Samples: {load_metrics['cpu_samples']}\n")
        f.write(f"Load Memory Samples: {load_metrics['memory_samples']}\n")

    print(f"\nResults saved to: {filepath}")


def main():
    """Main function to run the performance measurement."""
    print("System Performance Baseline Measurement")
    print("=====================================")

    # Measure idle baseline
    idle_metrics = measure_idle_baseline()

    # Run load test
    load_metrics = run_load_test()

    # Print results
    print_results(idle_metrics, load_metrics)

    # Save results to file
    save_results_to_file(idle_metrics, load_metrics)

    print("\nMeasurement complete. Use these baselines for future benchmarking.")


if __name__ == "__main__":
    main()