"""Command-line interface (CLI) for running offline Oiled incident case evaluations."""

import argparse
import sys
from pathlib import Path

from oiled.utils.dashboard_generator import generate_dashboard_html


def main():
    parser = argparse.ArgumentParser(
        description="Oiled — Offline Incident Intelligence & AIS Correlation CLI Runner"
    )
    parser.add_argument(
        "--case",
        type=str,
        required=True,
        help="Path to the case directory (e.g. cases/case-001)",
    )
    parser.add_argument(
        "--output-html",
        type=str,
        default=None,
        help="Custom path to save generated dashboard.html (default: <case_dir>/dashboard.html)",
    )

    args = parser.parse_args()
    case_dir = Path(args.case).resolve()

    if not case_dir.exists() or not case_dir.is_dir():
        print(f"Error: Case directory '{case_dir}' does not exist.")
        sys.exit(1)

    print(f"=== Oiled CLI — Evaluating Case: {case_dir.name} ===")

    # Check case manifest
    manifest_path = case_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"Error: Missing manifest.json in {case_dir}")
        sys.exit(1)

    # Determine HTML output path
    if args.output_html:
        html_path = Path(args.output_html).resolve()
    else:
        html_path = case_dir / "dashboard.html"

    # Generate dashboard
    res_path = generate_dashboard_html(case_dir, html_path)
    print(f"✓ Case evaluation complete!")
    print(f"✓ Dashboard generated: {res_path}")


if __name__ == "__main__":
    main()
