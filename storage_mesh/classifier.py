# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class Sensitivity(StrEnum):
    UNCLASSIFIED = "UNCLASSIFIED"
    SENSITIVE = "SENSITIVE"
    CLASSIFIED = "CLASSIFIED"
    TOP_SECRET = "TOP_SECRET"


@dataclass(frozen=True)
class AssetProfile:
    sensitivity: Sensitivity
    asset_type: str
    crypto_posture: str
    retention_days: int
    storage_ring: str


class AssetClassifier:
    EXTENSIONS = {
        ".log": ("telemetry", Sensitivity.SENSITIVE, 30),
        ".json": ("structured-data", Sensitivity.SENSITIVE, 90),
        ".yaml": ("configuration", Sensitivity.SENSITIVE, 365),
        ".yml": ("configuration", Sensitivity.SENSITIVE, 365),
        ".model": ("model-artifact", Sensitivity.CLASSIFIED, 365),
        ".safetensors": ("model-artifact", Sensitivity.CLASSIFIED, 365),
        ".vault": ("sealed-vault", Sensitivity.TOP_SECRET, 3650),
    }

    def classify(self, path: str | Path, content: bytes = b"") -> AssetProfile:
        suffix = Path(path).suffix.lower()
        asset_type, sensitivity, retention = self.EXTENSIONS.get(
            suffix, ("unknown", Sensitivity.SENSITIVE, 90)
        )

        if b"TOP_SECRET" in content or b"TS_SCI" in content:
            sensitivity, retention = Sensitivity.TOP_SECRET, 3650

        ring = {
            Sensitivity.UNCLASSIFIED: "hot",
            Sensitivity.SENSITIVE: "warm",
            Sensitivity.CLASSIFIED: "cold",
            Sensitivity.TOP_SECRET: "airgap",
        }[sensitivity]

        return AssetProfile(
            sensitivity=sensitivity,
            asset_type=asset_type,
            crypto_posture="ML-KEM-1024-envelope-required",
            retention_days=retention,
            storage_ring=ring,
        )