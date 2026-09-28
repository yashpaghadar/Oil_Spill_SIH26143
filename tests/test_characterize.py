"""Tests for Bragg wind gate, Fay age interval, and slick characterization."""

import math
import unittest

from oiled.models.characterize import (
    fay_surface_tension_hours,
    morphology_age_prior,
    wind_gate,
    characterize_slick,
)


class TestCharacterize(unittest.TestCase):
    def test_wind_gate_bragg_window(self):
        self.assertEqual(wind_gate(0.0), 0.0)
        self.assertEqual(wind_gate(2.0), 0.0)
        self.assertEqual(wind_gate(6.0), 1.0)
        self.assertEqual(wind_gate(13.0), 0.0)
        self.assertTrue(0.0 < wind_gate(2.1) < 0.1)

    def test_fay_age_is_an_interval(self):
        hours = fay_surface_tension_hours(640.0, 0.02)
        self.assertGreater(hours, 0)
        wider = fay_surface_tension_hours(1280.0, 0.02)
        self.assertAlmostEqual(wider / hours, 2 ** (4 / 3), places=5)
        prior = morphology_age_prior(800.0)
        self.assertLess(prior.low_hours, prior.best_hours)
        self.assertLess(prior.best_hours, prior.high_hours)
        self.assertEqual(prior.method, "fay_surface_tension")

    def test_slick_characterization(self):
        ring = [(72.32, 18.78), (72.39, 18.83), (72.395, 18.828), (72.325, 18.778)]
        # ~6.5 m/s towards NE
        u, v = 4.6, 4.6
        c = characterize_slick(ring, u, v)
        self.assertGreater(c.area_km2, 0)
        self.assertGreater(c.length_km, c.width_km)
        self.assertGreater(c.wind_gate_multiplier, 0.5)
        self.assertIn("low_hours", c.age.__dict__)
        calm = characterize_slick(ring, 0.5, 0.5)
        self.assertLess(calm.wind_gate_multiplier, 0.15)
