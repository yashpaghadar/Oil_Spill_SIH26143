"""Unit tests for Oiled CLI runner and HTML dashboard generation."""

from pathlib import Path
import unittest
from oiled.utils.dashboard_generator import generate_dashboard_html

CASE_001_DIR = Path(__file__).resolve().parent.parent / "cases" / "case-001"


class TestCLIDashboard(unittest.TestCase):
    def test_dashboard_generation(self):
        output_html = CASE_001_DIR / "test_dashboard.html"
        res_path = generate_dashboard_html(CASE_001_DIR, output_html)

        self.assertTrue(res_path.exists())
        self.assertGreater(res_path.stat().st_size, 1000)

        with open(res_path) as f:
            content = f.read()

        self.assertIn("OILED", content)
        self.assertIn("MT AL-MARJAN", content)
        self.assertIn("Tactical Map Viewport", content)
        self.assertIn("Play Hindcast", content)

        # Cleanup test HTML
        if output_html.exists():
            output_html.unlink()


if __name__ == "__main__":
    unittest.main()
