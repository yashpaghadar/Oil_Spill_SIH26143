"""Environmental forcing providers (wind and ocean currents) for drift simulation."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple
import numpy as np


class EnvironmentalProvider(ABC):
    """Abstract interface for querying wind and ocean current velocity fields."""

    @abstractmethod
    def get_wind(self, lon: float, lat: float, dt: datetime) -> Tuple[float, float]:
        """Return (u10, v10) 10m wind velocity in m/s (eastward, northward)."""
        pass

    @abstractmethod
    def get_current(self, lon: float, lat: float, dt: datetime) -> Tuple[float, float]:
        """Return (uo, vo) surface ocean current velocity in m/s (eastward, northward)."""
        pass


class ConstantEnvironmentalProvider(EnvironmentalProvider):
    """Provider returning constant uniform wind and current fields."""

    def __init__(
        self,
        u10: float = 5.0,
        v10: float = 3.0,
        uo: float = 0.25,
        vo: float = 0.15,
        provider_name: str = "Constant Uniform Field",
    ):
        self.u10 = u10
        self.v10 = v10
        self.uo = uo
        self.vo = vo
        self.provider_name = provider_name

    def get_wind(self, lon: float, lat: float, dt: datetime) -> Tuple[float, float]:
        return self.u10, self.v10

    def get_current(self, lon: float, lat: float, dt: datetime) -> Tuple[float, float]:
        return self.uo, self.vo


class SyntheticEnvironmentalProvider(EnvironmentalProvider):
    """Deterministic, smooth spatio-temporally varying environmental field.

    Useful for offline testing, benchmarks, and demo cases.
    """

    def __init__(
        self,
        base_wind_speed: float = 6.0,
        base_wind_dir_deg: float = 45.0,  # blowing towards NE
        base_current_speed: float = 0.30,
        base_current_dir_deg: float = 30.0,
    ):
        self.base_wind_speed = base_wind_speed
        self.base_wind_dir_deg = base_wind_dir_deg
        self.base_current_speed = base_current_speed
        self.base_current_dir_deg = base_current_dir_deg

    def _angle_to_uv(self, speed: float, dir_deg: float) -> Tuple[float, float]:
        rad = np.radians(dir_deg)
        u = speed * np.sin(rad)
        v = speed * np.cos(rad)
        return float(u), float(v)

    def get_wind(self, lon: float, lat: float, dt: datetime) -> Tuple[float, float]:
        # Spatial wave modulation + diurnal variation
        hour = dt.hour + dt.minute / 60.0
        time_factor = 1.0 + 0.15 * np.sin(2 * np.pi * hour / 24.0)
        spatial_factor = 1.0 + 0.05 * np.cos(np.radians(lon * 10 + lat * 10))
        speed = self.base_wind_speed * time_factor * spatial_factor
        return self._angle_to_uv(speed, self.base_wind_dir_deg)

    def get_current(self, lon: float, lat: float, dt: datetime) -> Tuple[float, float]:
        # Subtle spatial current variation
        spatial_factor = 1.0 + 0.08 * np.sin(np.radians(lat * 15))
        speed = self.base_current_speed * spatial_factor
        return self._angle_to_uv(speed, self.base_current_dir_deg)
