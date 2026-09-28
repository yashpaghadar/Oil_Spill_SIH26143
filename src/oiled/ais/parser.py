"""AIS track normalization, quality auditing, and trajectory parsing."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import pandas as pd

from oiled.data.contracts import VesselTrack


class AISParser:
    """Parser and quality auditor for historical vessel AIS position messages."""

    def __init__(
        self,
        max_speed_knots: float = 45.0,
        max_gap_hours: float = 2.0,
    ):
        self.max_speed_knots = max_speed_knots
        self.max_gap_hours = max_gap_hours

    def parse_records(
        self,
        records: List[Dict[str, Any]],
        source_name: str = "AIS Stream",
    ) -> Dict[str, VesselTrack]:
        """Parse raw records into validated VesselTrack objects indexed by MMSI.

        Required keys per record:
            - 'mmsi': str or int
            - 'timestamp_utc': datetime or ISO string
            - 'latitude': float
            - 'longitude': float
            - 'sog': float (Speed Over Ground in knots)
            - 'cog': float (Course Over Ground in degrees)
        """
        # Group by MMSI
        by_mmsi: Dict[str, List[Dict[str, Any]]] = {}
        for r in records:
            mmsi = str(r["mmsi"])
            by_mmsi.setdefault(mmsi, []).append(r)

        tracks: Dict[str, VesselTrack] = {}

        for mmsi, rows in by_mmsi.items():
            parsed_rows = []
            quality_flags = set()

            for row in rows:
                ts = row["timestamp_utc"]
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))

                lat = float(row["latitude"])
                lon = float(row["longitude"])
                sog = float(row.get("sog", row.get("sog_knots", 0.0)))
                cog = float(row.get("cog", row.get("cog_degrees", 0.0)))

                # Quality checks
                if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
                    quality_flags.add("OUT_OF_BOUNDS_COORDINATES")
                    continue  # drop corrupted coordinate

                if sog > self.max_speed_knots:
                    quality_flags.add("SPEED_ANOMALY")

                parsed_rows.append({
                    "timestamp": ts,
                    "lon": lon,
                    "lat": lat,
                    "sog": sog,
                    "cog": cog,
                })

            if not parsed_rows:
                continue

            # Sort chronologically
            parsed_rows.sort(key=lambda x: x["timestamp"])

            # Check for temporal gaps
            for i in range(len(parsed_rows) - 1):
                delta_h = (parsed_rows[i + 1]["timestamp"] - parsed_rows[i]["timestamp"]).total_seconds() / 3600.0
                if delta_h > self.max_gap_hours:
                    quality_flags.add(f"LONG_GAP_{delta_h:.1f}H")

            names = [str(r.get("vessel_name") or r.get("name") or "") for r in rows]
            types = [str(r.get("vessel_type") or r.get("ship_type") or "") for r in rows]
            vessel_name = next((n for n in names if n and n != "nan"), "")
            vessel_type = next((t for t in types if t and t != "nan"), "")

            track = VesselTrack(
                mmsi=mmsi,
                timestamps_utc=[r["timestamp"] for r in parsed_rows],
                positions=[(r["lon"], r["lat"]) for r in parsed_rows],
                sog_knots=[r["sog"] for r in parsed_rows],
                cog_degrees=[r["cog"] for r in parsed_rows],
                source=source_name,
                quality_flags=sorted(list(quality_flags)),
                vessel_name=vessel_name.replace("_", " "),
                vessel_type=vessel_type,
            )
            tracks[mmsi] = track

        return tracks

    def parse_csv(self, csv_path: str, source_name: str = "CSV") -> Dict[str, VesselTrack]:
        """Convenience loader for tabular AIS CSV files."""
        df = pd.read_csv(csv_path)
        records = df.to_dict(orient="records")
        return self.parse_records(records, source_name=source_name)
