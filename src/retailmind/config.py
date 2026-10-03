"""Project configuration and path resolution."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "configs" / "project.yaml"


@dataclass(frozen=True)
class ProjectConfig:
    root: Path
    workbook: Path
    processed_dir: Path
    reports_dir: Path
    excluded_stock_codes: frozenset[str]
    horizon_days: int
    k: int
    validation_cutoff: datetime
    test_cutoff: datetime

    def cutoff(self, snapshot: str) -> datetime:
        if snapshot == "validation":
            return self.validation_cutoff
        if snapshot == "test":
            return self.test_cutoff
        raise ValueError(f"Unknown snapshot: {snapshot}")


def load_config(path: Path = DEFAULT_CONFIG) -> ProjectConfig:
    """Load the checked-in configuration without changing source timestamps."""
    path = Path(path).resolve()
    with path.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    root = path.parent.parent
    data = config["data"]
    evaluation = config["evaluation"]
    return ProjectConfig(
        root=root,
        workbook=root / data["workbook"],
        processed_dir=root / data["processed_dir"],
        reports_dir=root / data["reports_dir"],
        excluded_stock_codes=frozenset(data["excluded_stock_codes"]),
        horizon_days=int(evaluation["horizon_days"]),
        k=int(evaluation["k"]),
        validation_cutoff=datetime.fromisoformat(evaluation["validation_cutoff"]),
        test_cutoff=datetime.fromisoformat(evaluation["test_cutoff"]),
    )
