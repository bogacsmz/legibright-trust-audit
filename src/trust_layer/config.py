"""Runtime config, loaded from environment (.env)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # dotenv optional at import time
    pass


@dataclass(frozen=True)
class Config:
    gms_url: str = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
    gms_token: str = os.getenv("DATAHUB_GMS_TOKEN", "")
    mutation_enabled: bool = os.getenv("TOOLS_IS_MUTATION_ENABLED", "true").lower() == "true"
    tjk_db: str = os.getenv("TJK_DB", "")
    tr_odds_db: str = os.getenv("TR_ODDS_DB", "")
    iddaa_db: str = os.getenv("IDDAA_DB", "")

    def require_gms(self) -> None:
        if not self.gms_url:
            raise RuntimeError("DATAHUB_GMS_URL not set — is the DataHub quickstart running?")


CONFIG = Config()
