"""Unit tests for particle drift simulation and origin backtracking."""

from datetime import datetime, timezone
import unittest
from oiled.drift.environment import ConstantEnvironmentalProvider, SyntheticEnvironmentalProvider
from oiled.drift.simulation import DriftSimulator


class TestDriftSimulation(unittest.TestCase):
    def setUp(self):
        self.obs_time = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)
        self.seed_slick = [(72.50, 18.50), (72.52, 18.51), (72.51, 18.52)]

    def test_backward_hindcast_direction(self):
        # Eastward current (uo=1.0, vo=0) & wind (u10=10.0, v10=0)
        # Particles drift EAST. In backward hindcast, origin should be to the WEST (lon < 72.50)
        env = ConstantEnvironmentalProvider(u10=10.0, v10=0.0, uo=1.0, vo=0.0)
        sim = DriftSimulator(environment=env, diffusion_coeff=0.0, seed=42)

        ensemble = sim.run_simulation(
            spill_event_id="test_spill",
            seed_coords=self.seed_slick,
            observation_utc=self.obs_time,
            duration_hours=6.0,
            direction="backward",
            particle_count=20,
        )

        centroid_lon, centroid_lat = ensemble.parameters["envelope_centroid"]
        self.assertLess(centroid_lon, 72.50, "Origin centroid must be west of observed slick")
        self.assertEqual(ensemble.direction, "backward")

    def test_uncertainty_widens_origin_envelope(self):
        """Acceptance check: Increasing uncertainty must widen origin region area."""
        env = SyntheticEnvironmentalProvider()

        # Low uncertainty simulator
        sim_low = DriftSimulator(
            environment=env,
            mean_windage=0.03,
            windage_std=0.001,
            diffusion_coeff=0.1,
            seed=42,
        )
        ens_low = sim_low.run_simulation(
            spill_event_id="spill_low",
            seed_coords=self.seed_slick,
            observation_utc=self.obs_time,
            duration_hours=8.0,
            particle_count=50,
        )

        # High uncertainty simulator
        sim_high = DriftSimulator(
            environment=env,
            mean_windage=0.03,
            windage_std=0.015,
            diffusion_coeff=10.0,
            seed=42,
        )
        ens_high = sim_high.run_simulation(
            spill_event_id="spill_high",
            seed_coords=self.seed_slick,
            observation_utc=self.obs_time,
            duration_hours=8.0,
            particle_count=50,
        )

        area_low = ens_low.parameters["envelope_area_km2"]
        area_high = ens_high.parameters["envelope_area_km2"]
        self.assertGreater(
            area_high,
            area_low,
            f"High uncertainty envelope ({area_high:.1f} km2) should be larger than low ({area_low:.1f} km2)",
        )


if __name__ == "__main__":
    unittest.main()
