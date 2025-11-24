"""
Master Profiling Script
=======================

This script runs all profiling tools:
1. Performance Profiling
2. Memory Profiling
3. Code Coverage Analysis

Author: Hussein Moukalled
Date: Fall 2025-2026
"""

import subprocess
import sys
import os
from datetime import datetime

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(" " * ((70 - len(title)) // 2) + title)
    print("="*70 + "\n")

def run_performance_profiling():
    """Run performance profiling."""
    print_header("STEP 1: PERFORMANCE PROFILING")
    print("Measuring API response times and throughput...\n")
    
    try:
        result = subprocess.run(
            [sys.executable, "profiling/performance_profiler.py"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running performance profiling: {e}")
        return False

def run_memory_profiling():
    """Run memory profiling."""
    print_header("STEP 2: MEMORY PROFILING")
    print("Analyzing memory usage...\n")
    
    try:
        result = subprocess.run(
            [sys.executable, "profiling/memory_profiler.py"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running memory profiling: {e}")
        return False

def run_coverage_analysis():
    """Run code coverage analysis."""
    print_header("STEP 3: CODE COVERAGE ANALYSIS")
    print("Measuring test coverage across all services...\n")
    
    try:
        result = subprocess.run(
            [sys.executable, "profiling/coverage_profiler.py"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running coverage analysis: {e}")
        return False

def generate_summary_report():
    """Generate a summary report of all profiling results."""
    print_header("PROFILING SUMMARY REPORT")
    
    summary = f"""
Profiling Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Files Generated:
----------------
1. Performance Report: profiling/performance_report.txt
2. Memory Report: Check console output above
3. Coverage Report: htmlcov/index.html (open in browser)
4. Coverage JSON: coverage.json

Next Steps:
-----------
1. Review performance_report.txt for API response times
2. Open htmlcov/index.html in your browser for detailed coverage
3. Check memory profiling output above for memory usage statistics

For your report, include:
- Screenshots of performance metrics
- Coverage percentage from htmlcov/index.html
- Memory usage statistics from the output above
"""
    print(summary)
    
    # Save summary
    with open("profiling/profiling_summary.txt", "w") as f:
        f.write(summary)
    
    print("Summary saved to: profiling/profiling_summary.txt\n")

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" " * 20 + "COMPREHENSIVE PROFILING SUITE")
    print(" " * 10 + "Hussein's Meeting Room Management System")
    print("="*70)
    
    print("\nPREREQUISITES:")
    print("  1. All Docker services must be running (docker-compose up)")
    print("  2. Services available at localhost:8001-8004")
    print("  3. Test database must be set up")
    print("\n" + "="*70)
    
    input("\nPress ENTER to start profiling...")
    
    results = {
        "performance": False,
        "memory": False,
        "coverage": False
    }
    
    # Run all profiling tools
    results["performance"] = run_performance_profiling()
    results["memory"] = run_memory_profiling()
    results["coverage"] = run_coverage_analysis()
    
    # Generate summary
    generate_summary_report()
    
    # Final status
    print_header("PROFILING COMPLETE")
    print("Status:")
    print(f"  Performance Profiling: {'PASSED' if results['performance'] else 'FAILED'}")
    print(f"  Memory Profiling:      {'PASSED' if results['memory'] else 'FAILED'}")
    print(f"  Coverage Analysis:      {'PASSED' if results['coverage'] else 'FAILED'}")
    print("\n" + "="*70 + "\n")

