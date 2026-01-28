# System Performance Scripter

A Python script to establish reliable baseline performance measurements for your system, focusing on CPU usage, memory consumption, and execution time.

## Purpose

This tool helps you:
- Measure accurate system-level performance metrics
- Distinguish idle behavior from load-induced behavior
- Capture peak resource usage rather than averages
- Ensure reproducible and meaningful measurements
- Ground future model benchmarking in trustworthy system metrics

## Features

- **Cross-platform**: Works on Windows, macOS, and Linux
- **Reproducible**: Uses standardized workloads (prime number calculation)
- **Comprehensive**: Measures CPU, memory, and execution time
- **Peak detection**: Captures maximum resource usage during loads
- **Idle baseline**: Establishes system behavior under no load
- **Result logging**: Automatically saves detailed results to timestamped files in `results/` folder

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Result Logging

Results are automatically saved to timestamped files in the `results/` folder:

```
results/
├── performance_baseline_20260127_143052.txt
├── performance_baseline_20260127_143105.txt
└── ...
```

Each log file contains:
- **System Specifications**: Hardware and software details (OS, CPU, memory, Python version)
- Full measurement results
- Timestamp of the run
- Raw data samples for further analysis
- All reproducibility notes

This allows you to:
- Track performance over time
- Compare results across different system configurations
- Maintain a historical record of your system's baseline performance
- Understand how hardware differences affect measurements

## Scripts Included

This repository contains two main scripts:

### 1. `system_performance.py` - Performance Baseline Measurement
Measures CPU usage, memory consumption, and execution time to establish reliable system performance baselines.

### 2. `system_inspector.py` - System State Inspector
Provides detailed information about the current system state, including running processes, background services, and resource usage. Use this before running performance tests to understand what might affect measurements.

## Usage

### Performance Baseline
```bash
python system_performance.py
```

### System Inspection
```bash
python system_inspector.py
```

The system inspector provides:
- **System Overview**: Hardware specs, OS version, resource usage
- **Resource Consumption Analysis**: Detailed breakdown of CPU/memory usage by process with contribution percentages
- **Performance Impact Assessment**: CPU/Memory load levels (LOW/MODERATE/HIGH) with specific recommendations
- **Top Processes**: Processes ranked by CPU and memory usage
- **Background Services**: Running system services and daemons
- **Network Connections**: Active network connections

Use this script before performance testing to:
- Identify resource-intensive background processes
- Quantify each process's contribution to total system load
- Get performance impact analysis and recommendations
- Understand why your performance measurements show certain results
- Justify overall system performance by measuring background resource consumption

Reports are automatically saved to `inspection_reports/` folder.

The script will:
1. Measure idle system performance for 10 seconds
2. Run a CPU-intensive prime calculation task
3. Monitor system metrics throughout the load
4. Display comprehensive results

## Understanding the Results

The script provides several key metrics:

- **Idle Baseline**: System behavior under normal conditions
- **Load Test Results**: System response during CPU-intensive work
- **Performance Impact**: Difference between idle and loaded states

### Interpreting CPU Usage

- **Low CPU during load**: The prime calculation is single-threaded, so on multi-core systems, system-wide CPU % appears low even under load
- **Peak vs Average**: Peaks show maximum instantaneous usage, averages show sustained load
- **Idle fluctuations**: Natural system activity (background processes, I/O) causes some variation

### Memory Usage

- **High baseline memory**: ~70% is normal for systems with many applications running
- **Minimal change during load**: CPU-bound tasks like prime calculation don't significantly increase memory usage

### Execution Time

- **Task duration**: 0.5-1 second provides enough time for meaningful monitoring
- **Reproducibility**: Same algorithm and input size ensure consistent results across runs

### When to Use These Baselines

Use these measurements to:
- Compare performance across different hardware configurations
- Detect performance regressions in your applications
- Set expectations for resource usage during benchmarking
- Identify systems with unusual idle behavior

## Methodology

### Idle Baseline Measurement
- Duration: 10 seconds
- Sampling interval: 1 second
- Captures average system behavior under normal conditions

### Load Test
- Workload: Prime number calculation up to 50,000
- Monitoring: Continuous sampling every 500ms during execution
- Captures peak and average resource usage under load

### Metrics
- **CPU Usage**: System-wide percentage
- **Memory Usage**: Virtual memory percentage
- **Execution Time**: Wall-clock time for the workload

## Reproducibility

To ensure consistent results across runs and systems:
- Use the same prime calculation limit (50,000)
- Run measurements at similar system states (close background applications)
- Avoid running during system maintenance or updates
- Use the same Python environment and psutil version

## Dependencies

- Python 3.6+
- psutil: System and process utilities

## Contributing

This script is designed to be simple, reliable, and reproducible. For enhancements:
- Maintain cross-platform compatibility
- Preserve measurement accuracy
- Keep workloads computationally intensive but reasonable
- Document any changes to methodology

## License

MIT License - feel free to use and modify for your benchmarking needs.# system_performance_scripter
