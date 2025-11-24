"""
Code Coverage Profiling Script
===============================

This script runs pytest with coverage to measure code coverage across all services.

Author: Hussein Moukalled
Date: Fall 2025-2026
"""

import subprocess
import sys
import os

def run_coverage_analysis():
    """Run pytest with coverage analysis."""
    print("\n" + "="*60)
    print("CODE COVERAGE ANALYSIS")
    print("="*60 + "\n")
    
    # Run pytest with coverage
    print("Running pytest with coverage analysis...")
    print("This may take a few minutes...\n")
    
    try:
        # Run coverage
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "tests/",
                "--cov=users_service",
                "--cov=rooms_service",
                "--cov=bookings_service",
                "--cov=reviews_service",
                "--cov=shared",
                "--cov-report=html",
                "--cov-report=term",
                "--cov-report=json",
                "-v"
            ],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
        
        print("\n" + "="*60)
        print("Coverage report generated!")
        print("="*60)
        print("\nHTML report: htmlcov/index.html")
        print("JSON report: coverage.json")
        print("Terminal report shown above")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running coverage: {e}")
        return False

def generate_coverage_summary():
    """Generate a summary of coverage results."""
    try:
        import json
        
        if os.path.exists("coverage.json"):
            with open("coverage.json", "r") as f:
                coverage_data = json.load(f)
            
            print("\n" + "="*60)
            print("COVERAGE SUMMARY")
            print("="*60 + "\n")
            
            totals = coverage_data.get("totals", {})
            print(f"Total Coverage: {totals.get('percent_covered', 0):.2f}%")
            print(f"Total Lines: {totals.get('num_statements', 0)}")
            print(f"Lines Covered: {totals.get('covered_lines', 0)}")
            print(f"Lines Missing: {totals.get('missing_lines', 0)}")
            
            print("\nCoverage by Service:")
            files = coverage_data.get("files", {})
            
            services = {
                "users_service": "Users Service",
                "rooms_service": "Rooms Service",
                "bookings_service": "Bookings Service",
                "reviews_service": "Reviews Service",
                "shared": "Shared Module"
            }
            
            for service_key, service_name in services.items():
                service_coverage = 0
                service_files = 0
                
                for file_path, file_data in files.items():
                    if service_key in file_path:
                        service_files += 1
                        file_totals = file_data.get("summary", {})
                        service_coverage += file_totals.get("percent_covered", 0)
                
                if service_files > 0:
                    avg_coverage = service_coverage / service_files
                    print(f"  {service_name}: {avg_coverage:.2f}%")
            
    except Exception as e:
        print(f"Error generating summary: {e}")

if __name__ == "__main__":
    print("Starting Code Coverage Analysis...")
    print("Make sure all dependencies are installed:")
    print("  pip install pytest pytest-cov coverage\n")
    
    success = run_coverage_analysis()
    
    if success:
        generate_coverage_summary()
    
    sys.exit(0 if success else 1)

