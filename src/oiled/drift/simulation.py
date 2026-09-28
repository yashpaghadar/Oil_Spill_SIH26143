"""Physics-based particle ensemble drift modeling and origin backtracking."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from oiled.data.contracts import TrajectoryEnsemble
from oiled.drift.environment import EnvironmentalProvider
from oiled.drift.origin_field import estimate_origin_field
from oiled.utils.geometry import (
    compute_centroid,
    compute_convex_hull,
    compute_polygon_area_perimeter_km,
    meters_to_lat_lon_displacement,
    to_geojson_polygon,
)


@dataclass
class Particle:
    """Individual particle state in the ensemble."""
    particle_id: int
    current_lon: float
    current_lat: float
    windage_coeff: float  # Leeway factor (e.g. ~0.03)
    history: List[Tuple[datetime, float, float]] = field(default_factory=list)


class DriftSimulator:
    """Physics-based particle ensemble simulator supporting forward forecast and backward origin hindcast."""

    def __init__(
        self,
        environment: EnvironmentalProvider,
        mean_windage: float = 0.030,
        windage_std: float = 0.005,
        diffusion_coeff: float = 1.0,  # Horizontal eddy diffusivity (m^2/s)
        seed: Optional[int] = 42,
    ):
        self.environment = environment
        self.mean_windage = mean_windage
        self.windage_std = windage_std
        self.diffusion_coeff = diffusion_coeff
        self.rng = np.random.default_rng(seed)

    def initialize_particles(
        self,
        seed_coords: List[Tuple[float, float]],
        start_utc: datetime,
        particle_count: int = 100,
    ) -> List[Particle]:
        """Seed particles across the spill geometry with normally distributed windage."""
        particles = []
        n_seed_points = len(seed_coords)

        for i in range(particle_count):
            base_lon, base_lat = seed_coords[i % n_seed_points]
            # Small initial spatial jitter around seed points
            jitter_lon = float(self.rng.normal(0, 0.001))
            jitter_lat = float(self.rng.normal(0, 0.001))

            windage = float(
                np.clip(
                    self.rng.normal(self.mean_windage, self.windage_std),
                    0.015,
                    0.050,
                )
            )

            p = Particle(
                particle_id=i,
                current_lon=base_lon + jitter_lon,
                current_lat=base_lat + jitter_lat,
                windage_coeff=windage,
                history=[(start_utc, base_lon + jitter_lon, base_lat + jitter_lat)],
            )
            particles.append(p)

        return particles

    def run_simulation(
        self,
        spill_event_id: str,
        seed_coords: List[Tuple[float, float]],
        observation_utc: datetime,
        duration_hours: float = 12.0,
        step_minutes: float = 30.0,
        direction: str = "backward",  # 'backward' (origin hindcast) or 'forward' (forecast)
        particle_count: int = 100,
    ) -> TrajectoryEnsemble:
        """Run trajectory ensemble simulation.

        Args:
            spill_event_id: Detection or spill ID.
            seed_coords: List of (lon, lat) points defining the observed slick.
            observation_utc: UTC timestamp of the SAR image observation.
            duration_hours: Duration of drift simulation.
            step_minutes: Time step resolution.
            direction: 'backward' to backtrack origin, or 'forward' to forecast.
            particle_count: Number of particles in the ensemble.
        """
        particles = self.initialize_particles(seed_coords, observation_utc, particle_count)
        dt_seconds = step_minutes * 60.0
        n_steps = int(round((duration_hours * 3600.0) / dt_seconds))
        sign = -1.0 if direction == "backward" else 1.0

        current_time = observation_utc
        time_step = timedelta(seconds=sign * dt_seconds)

        # Standard deviation of diffusive displacement in meters: sigma = sqrt(2 * Kh * dt)
        diff_std_m = np.sqrt(2.0 * self.diffusion_coeff * dt_seconds)

        for _ in range(n_steps):
            next_time = current_time + time_step

            for p in particles:
                u_wind, v_wind = self.environment.get_wind(p.current_lon, p.current_lat, current_time)
                u_curr, v_curr = self.environment.get_current(p.current_lon, p.current_lat, current_time)

                # Total deterministic velocity in m/s: current + windage * wind
                u_total = u_curr + p.windage_coeff * u_wind
                v_total = v_curr + p.windage_coeff * v_wind

                # Turbulent diffusion perturbation
                u_diff = float(self.rng.normal(0, diff_std_m)) / dt_seconds
                v_diff = float(self.rng.normal(0, diff_std_m)) / dt_seconds

                # Displacements in meters
                dx_m = sign * (u_total + u_diff) * dt_seconds
                dy_m = sign * (v_total + v_diff) * dt_seconds

                dlon, dlat = meters_to_lat_lon_displacement(dx_m, dy_m, p.current_lat)
                p.current_lon += dlon
                p.current_lat += dlat
                p.history.append((next_time, p.current_lon, p.current_lat))

            current_time = next_time

        # Extract final particle positions (origin candidates if backward)
        final_coords = [(p.current_lon, p.current_lat) for p in particles]
        hull_coords = compute_convex_hull(final_coords)
        envelope_geojson = to_geojson_polygon(hull_coords)

        envelope_area_km2, _ = compute_polygon_area_perimeter_km(hull_coords)
        origin_field = estimate_origin_field(final_coords)
        time_window = (
            min(observation_utc, current_time),
            max(observation_utc, current_time),
        )

        # Keep a subsample of histories for the dashboard hindcast animation.
        stride = max(1, particle_count // 40)
        particle_paths = [p.history for p in particles[::stride]]

        return TrajectoryEnsemble(
            spill_event_id=spill_event_id,
            direction=direction,
            particle_count=particle_count,
            simulation_duration_hours=duration_hours,
            parameters={
                "mean_windage": self.mean_windage,
                "windage_std": self.windage_std,
                "diffusion_coeff_m2s": self.diffusion_coeff,
                "step_minutes": step_minutes,
                "envelope_area_km2": round(envelope_area_km2, 2),
                "envelope_centroid": compute_centroid(hull_coords),
                "origin_sigma_km": origin_field.sigma_km,
                "origin_area90_km2": origin_field.area90_km2,
                "origin_insufficient": origin_field.insufficient_evidence,
                "origin_insufficient_reason": origin_field.reason,
            },
            origin_envelope_geojson=envelope_geojson,
            time_window_utc=time_window,
            particle_paths=particle_paths,
        )
