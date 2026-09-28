"""Unit tests for AIS track auditing, quality flagging, and candidate vessel correlation."""

from datetime import datetime, timedelta, timezone
import unittest
from oiled.ais.parser import AISParser
from oiled.ais.correlation import VesselCorrelator
from oiled.data.contracts import TrajectoryEnsemble
from oiled.utils.geometry import to_geojson_polygon


class TestAISAndCorrelation(unittest.TestCase):
    def setUp(self):
        self.parser = AISParser(max_speed_knots=45.0, max_gap_hours=2.0)
        self.correlator = VesselCorrelator(max_search_distance_km=30.0)

        # Baseline origin envelope centered near (72.0, 18.0)
        envelope_box = [(71.95, 17.95), (72.05, 17.95), (72.05, 18.05), (71.95, 18.05)]
        self.target_time = datetime(2026, 9, 25, 6, 0, tzinfo=timezone.utc)
        self.ensemble = TrajectoryEnsemble(
            spill_event_id="spill_test",
            direction="backward",
            particle_count=50,
            simulation_duration_hours=6.0,
            parameters={"envelope_centroid": (72.0, 18.0)},
            origin_envelope_geojson=to_geojson_polygon(envelope_box),
            time_window_utc=(self.target_time - timedelta(hours=2), self.target_time + timedelta(hours=2)),
        )

    def test_ais_parser_quality_flags(self):
        records = [
            # Normal ping
            {"mmsi": "111", "timestamp_utc": "2026-09-25T05:00:00Z", "latitude": 18.0, "longitude": 72.0, "sog": 12.0, "cog": 45.0},
            # Speed anomaly (65 knots)
            {"mmsi": "111", "timestamp_utc": "2026-09-25T05:30:00Z", "latitude": 18.05, "longitude": 72.05, "sog": 65.0, "cog": 45.0},
            # Out of bounds lat
            {"mmsi": "111", "timestamp_utc": "2026-09-25T06:00:00Z", "latitude": 195.0, "longitude": 72.1, "sog": 12.0, "cog": 45.0},
            # Long gap (4 hours later)
            {"mmsi": "111", "timestamp_utc": "2026-09-25T10:00:00Z", "latitude": 18.2, "longitude": 72.2, "sog": 12.0, "cog": 45.0},
        ]
        tracks = self.parser.parse_records(records)
        track = tracks["111"]

        self.assertIn("SPEED_ANOMALY", track.quality_flags)
        self.assertIn("OUT_OF_BOUNDS_COORDINATES", track.quality_flags)
        self.assertTrue(any("LONG_GAP" in f for f in track.quality_flags))
        self.assertEqual(len(track.positions), 3, "Out of bounds coordinate should be excluded from positions")

    def test_correlator_culprit_ranking_and_exclusions(self):
        """Culprit vessel crossing origin at release time must rank #1 above distractors."""
        # 1. Culprit: passes through (72.0, 18.0) at 06:00 UTC
        culprit_records = [
            {"mmsi": "CULPRIT_101", "timestamp_utc": "2026-09-25T05:30:00Z", "latitude": 17.95, "longitude": 71.95, "sog": 14.0, "cog": 45.0},
            {"mmsi": "CULPRIT_101", "timestamp_utc": "2026-09-25T06:00:00Z", "latitude": 18.00, "longitude": 72.00, "sog": 14.0, "cog": 45.0},
            {"mmsi": "CULPRIT_101", "timestamp_utc": "2026-09-25T06:30:00Z", "latitude": 18.05, "longitude": 72.05, "sog": 14.0, "cog": 45.0},
        ]

        # 2. Distractor Spatial: passes at 06:00 UTC, but 60 km away at lat 18.55
        distractor_spatial = [
            {"mmsi": "DISTRACTOR_FAR", "timestamp_utc": "2026-09-25T05:30:00Z", "latitude": 18.55, "longitude": 72.00, "sog": 12.0, "cog": 90.0},
            {"mmsi": "DISTRACTOR_FAR", "timestamp_utc": "2026-09-25T06:30:00Z", "latitude": 18.55, "longitude": 72.10, "sog": 12.0, "cog": 90.0},
        ]

        # 3. Distractor Temporal: passes through (72.0, 18.0), but 12 hours later
        distractor_temporal = [
            {"mmsi": "DISTRACTOR_LATE", "timestamp_utc": "2026-09-25T18:00:00Z", "latitude": 17.99, "longitude": 71.99, "sog": 12.0, "cog": 45.0},
            {"mmsi": "DISTRACTOR_LATE", "timestamp_utc": "2026-09-25T18:30:00Z", "latitude": 18.01, "longitude": 72.01, "sog": 12.0, "cog": 45.0},
        ]

        all_records = culprit_records + distractor_spatial + distractor_temporal
        tracks = self.parser.parse_records(all_records)

        rankings = self.correlator.correlate(
            ensemble=self.ensemble,
            tracks=tracks,
            spill_orientation_deg=45.0,
        )

        self.assertEqual(len(rankings), 3)

        # Culprit should be rank 1
        culprit_cand = rankings[0]
        self.assertEqual(culprit_cand.vessel_id, "CULPRIT_101")
        self.assertEqual(culprit_cand.rank, 1)
        self.assertGreater(culprit_cand.total_score, 0.55)
        self.assertEqual(len(culprit_cand.exclusions), 0)
        self.assertIn("drift", culprit_cand.evidence_components)

        # Distractor Spatial should be excluded with spatial mismatch
        dist_spatial = next(r for r in rankings if r.vessel_id == "DISTRACTOR_FAR")
        self.assertEqual(dist_spatial.rank, -1)
        self.assertTrue(any("spatial_mismatch" in ex for ex in dist_spatial.exclusions))

        # Distractor Temporal should be excluded with temporal mismatch
        dist_temporal = next(r for r in rankings if r.vessel_id == "DISTRACTOR_LATE")
        self.assertEqual(dist_temporal.rank, -1)
    def test_correlator_refuses_closed_wind_gate(self):
        records = [
            {"mmsi": "CULPRIT_101", "timestamp_utc": "2026-09-25T05:30:00Z", "latitude": 17.95, "longitude": 71.95, "sog": 14.0, "cog": 45.0},
            {"mmsi": "CULPRIT_101", "timestamp_utc": "2026-09-25T06:00:00Z", "latitude": 18.00, "longitude": 72.00, "sog": 14.0, "cog": 45.0},
            {"mmsi": "CULPRIT_101", "timestamp_utc": "2026-09-25T06:30:00Z", "latitude": 18.05, "longitude": 72.05, "sog": 14.0, "cog": 45.0},
        ]
        tracks = self.parser.parse_records(records)
        rankings = self.correlator.correlate(
            ensemble=self.ensemble,
            tracks=tracks,
            spill_orientation_deg=45.0,
            wind_gate_multiplier=0.0,
        )
        self.assertTrue(all(r.verdict == "insufficient_evidence" for r in rankings))
        self.assertTrue(all(r.rank == -1 for r in rankings))


if __name__ == "__main__":
    unittest.main()
