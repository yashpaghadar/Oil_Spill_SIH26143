"""Command-line interface for Oiled incident cases."""

from __future__ import annotations

import argparse
import http.server
import socketserver
import sys
from pathlib import Path

from oiled.pipeline import generate_all_cases
from oiled.utils.dashboard_generator import generate_dashboard_html

ROOT = Path(__file__).resolve().parents[2]


def cmd_dashboard(args) -> int:
    case_dir = Path(args.case).resolve()
    if not case_dir.exists():
        print(f"Error: case directory '{case_dir}' does not exist.")
        return 1
    if not (case_dir / "manifest.json").exists():
        print(f"Error: missing manifest.json in {case_dir}")
        return 1
    html_path = Path(args.output_html).resolve() if args.output_html else case_dir / "dashboard.html"
    res = generate_dashboard_html(case_dir, html_path)
    docs = ROOT / "docs" / "index.html"
    generate_dashboard_html(case_dir, docs)
    print(f"Dashboard: {res}")
    print(f"Docs copy: {docs}")
    return 0


def cmd_generate(args) -> int:
    cases_root = Path(args.cases_root).resolve() if args.cases_root else ROOT / "cases"
    payloads = generate_all_cases(cases_root)
    html = generate_dashboard_html(cases_root / "case-001", cases_root / "case-001" / "dashboard.html")
    generate_dashboard_html(cases_root / "case-001", ROOT / "docs" / "index.html")
    print(f"Generated {len(payloads)} cases -> {html}")
    for p in payloads:
        print(f"  {p['case_id']}: {p['verdict']} ({p['title']})")
    return 0


def cmd_serve(args) -> int:
    directory = Path(args.dir).resolve()
    handler = http.server.SimpleHTTPRequestHandler
    os_chdir = __import__("os").chdir
    os_chdir(directory)

    class Quiet(handler):
        def log_message(self, fmt, *rest):
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % rest))

    with socketserver.TCPServer(("127.0.0.1", args.port), Quiet) as httpd:
        print(f"Serving {directory} at http://127.0.0.1:{args.port}/")
        print(f"Open http://127.0.0.1:{args.port}/dashboard.html  (or docs/index.html)")
        httpd.serve_forever()
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Oiled — SAR detection, hindcast, AIS evidence")
    sub = parser.add_subparsers(dest="cmd")

    p_dash = sub.add_parser("dashboard", help="Render dashboard.html from an existing case")
    p_dash.add_argument("--case", required=True)
    p_dash.add_argument("--output-html", default=None)
    p_dash.set_defaults(func=cmd_dashboard)

    p_gen = sub.add_parser("generate", help="Regenerate SIM cases and dashboards")
    p_gen.add_argument("--cases-root", default=None)
    p_gen.set_defaults(func=cmd_generate)

    p_srv = sub.add_parser("serve", help="Serve a directory over HTTP")
    p_srv.add_argument("--dir", default=str(ROOT / "docs"))
    p_srv.add_argument("--port", type=int, default=8765)
    p_srv.set_defaults(func=cmd_serve)

    # Backward-compatible: `python -m oiled.cli --case ...`
    parser.add_argument("--case", default=None)
    parser.add_argument("--output-html", default=None)

    args = parser.parse_args(argv)
    if args.cmd:
        return args.func(args)
    if args.case:
        args.func = cmd_dashboard
        return cmd_dashboard(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
