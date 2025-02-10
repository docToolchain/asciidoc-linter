# run_tests_html.py - Test runner script with HTML report
"""
Script to run all tests for the AsciiDoc linter and generate HTML reports
Requires: pytest-html, pytest-cov (install with: pip install pytest-html pytest-cov)
"""

import subprocess
import sys
import shutil
from pathlib import Path
from datetime import datetime


def ensure_dir_exists(path: Path):
    """Create directory if it doesn't exist"""
    path.mkdir(parents=True, exist_ok=True)


def copy_reports(temp_test_report: Path, docs_dir: Path):
    """Copy reports to docs directory"""
    ensure_dir_exists(docs_dir)

    # Define target files
    final_test_report = docs_dir / "test-report.html"
    final_cov_dir = docs_dir / "coverage"

    # Remove old coverage directory if it exists
    if final_cov_dir.exists():
        shutil.rmtree(final_cov_dir)

    # Copy new reports
    shutil.copy2(temp_test_report, final_test_report)

    # Copy coverage report if it exists
    temp_cov = Path("htmlcov")
    if temp_cov.exists():
        shutil.copytree(temp_cov, final_cov_dir)
        shutil.rmtree(temp_cov)  # Clean up temporary coverage directory

    return final_test_report, final_cov_dir


if __name__ == "__main__":
    print("Starting test execution...")

    # Create reports directory
    reports_dir = Path("test-reports")
    print(f"Creating reports directory: {reports_dir}")
    ensure_dir_exists(reports_dir)

    # Generate timestamp for unique report name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_report = reports_dir / f"test_report_{timestamp}.html"

    # Construct pytest command with HTML report and coverage arguments
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        f"--html={test_report}",
        "--self-contained-html",
        "--cov=asciidoc_linter",
        "--cov-report=html",
        "--cov-report=term",
        "--cov-config=.coveragerc",
    ]

    print(f"Executing command: {' '.join(cmd)}")

    # Run pytest as a subprocess
    try:
        result = subprocess.run(cmd, check=False)

        # If tests were successful, copy reports to docs
        if result.returncode == 0:
            try:
                docs_dir = Path(
                    "build/microsite/output/test-results"
                )  # Changed path to match project structure
                final_test, final_cov = copy_reports(test_report, docs_dir)
                print("\nReports copied to docs:")
                print(f"Test report: {final_test}")
                print(f"Coverage report: {final_cov}/index.html")
            except Exception as e:
                print(f"\nError copying reports: {e}")
                sys.exit(1)
        else:
            print("\nTests failed - reports were generated but not copied to docs")

        # Clean up temporary reports
        shutil.rmtree(reports_dir)

        # Exit with test result code
        sys.exit(result.returncode)

    except Exception as e:
        print(f"Error executing tests: {e}")
        sys.exit(1)
