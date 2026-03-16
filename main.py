"""
main.py - Entry point for Interactive Geospatial Explorer
=========================================================

Thin-controller module that only orchestrates calls to:
    - operations.py for workflow execution
    - display.py for presentation formatting
"""

from display import format_header, format_run_report
from operations import run_core_flow


def main() -> None:
    """Run one complete geospatial exploration cycle."""
    print(format_header())
    run_summary = run_core_flow()
    print(format_run_report(run_summary))


if __name__ == "__main__":
    # Guard keeps imports side-effect free for tests and reuse.
    main()
