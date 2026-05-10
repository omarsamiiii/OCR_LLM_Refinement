"""Risk calibration placeholder."""

from dataclasses import dataclass


@dataclass(slots=True)
class RiskCalibrator:
    """Simple scaling-based calibrator placeholder."""

    scale: float = 1.0

    def calibrate(self, score: float) -> float:
        scaled = score * self.scale
        return max(0.0, min(1.0, scaled))
