# System Performance Scripter

A Python toolkit for establishing reliable system performance baselines and analyzing system state, focusing on CPU usage, memory consumption, and execution time.

## ⚠️ Privacy & Security Notice

**Important**: These scripts collect detailed system information. Result files contain sensitive data and are automatically excluded from git tracking. Never commit them to public repositories.

## Purpose

This toolkit helps you:
- Measure accurate system-level performance metrics
- Distinguish idle behavior from load-induced behavior
- Capture peak resource usage patterns
- Understand background processes affecting measurements
- Ensure reproducible and meaningful benchmarks

## Features

- **Cross-platform**: Windows, macOS, Linux
- **Reproducible**: Standardized workloads (prime calculation)
- **Comprehensive**: CPU, memory, execution time, process analysis
- **Privacy-conscious**: Multiple privacy modes and data controls
- **Result logging**: Automatic timestamped reports

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Measure performance baseline
python system_performance.py

# Inspect system state (before benchmarking)
python system_inspector.py --privacy
```

## Scripts Overview

### `system_performance.py` - Performance Baseline
- Measures CPU/memory usage during idle and load conditions
- Uses prime number calculation as reproducible workload
- Saves detailed results to `results/` directory

### `system_inspector.py` - System Inspector
- Analyzes current system state and resource consumption
- Identifies background processes affecting performance
- Provides privacy controls for sensitive environments
- Saves reports to `inspection_reports/` directory

## Usage Examples

### Performance Measurement
```bash
python system_performance.py
```

### System Inspection
```bash
# Full inspection
python system_inspector.py

# Privacy mode (excludes sensitive data)
python system_inspector.py --privacy

# Selective exclusion
python system_inspector.py --no-network --no-services
```

## Result Files

Results are automatically saved to timestamped files:

```
results/
├── performance_baseline_20260127_143052.txt
└── ...

inspection_reports/
├── system_inspection_20260127_143052.txt
└── ...
```

Each file contains:
- System specifications (hardware, OS, Python version)
- Measurement results and raw data
- Timestamp and reproducibility notes
- Performance analysis and recommendations

## Data Collection & Privacy

### What Gets Collected
- **Basic**: Hardware specs, OS info, resource usage
- **Sensitive**: Network connections, detailed process lists, user information

### Privacy Controls
- `--privacy`: Excludes network connections and limits process details
- `--no-network`: Excludes network connection information
- `--no-services`: Excludes background service information

### Security Notes
- Result directories are gitignored to prevent accidental commits
- Use privacy modes in sensitive environments
- Delete old reports when no longer needed

## Understanding Results

### Performance Metrics
- **Idle Baseline**: System behavior under normal conditions (10s measurement)
- **Load Test**: System response during CPU-intensive work
- **Performance Impact**: Difference between idle and loaded states

### Key Insights
- **CPU Usage**: Single-threaded workload shows low system-wide % on multi-core systems
- **Memory Usage**: CPU-bound tasks minimally impact memory
- **Peak vs Average**: Peaks capture maximum instantaneous usage
- **Background Impact**: Inspector helps quantify interference from other processes

### When to Use
- Compare performance across hardware configurations
- Detect performance regressions
- Set benchmarking expectations
- Identify unusual system behavior

## Methodology

### Idle Baseline
- Duration: 10 seconds
- Sampling: 1 second intervals
- Captures average system behavior

### Load Test
- Workload: Prime calculation up to 200,000
- Monitoring: 500ms intervals during execution
- Captures peak and sustained resource usage

### Metrics Tracked
- CPU usage (system-wide percentage)
- Memory usage (virtual memory percentage)
- Execution time (wall-clock)

## Dependencies

- Python 3.6+
- psutil: System and process utilities

## Contributing

Maintain:
- Cross-platform compatibility
- Measurement accuracy
- Reasonable computational intensity
- Clear documentation of methodology changes

## License

MIT License
