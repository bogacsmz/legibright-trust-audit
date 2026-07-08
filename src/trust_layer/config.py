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

# repo-local public data built by scripts/fetch_data.py (reproducible defaults)
_DATA = Path(__file__).resolve().parents[2] / "data"


@dataclass(frozen=True)
class Config:
    gms_url: str = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
    gms_token: str = os.getenv("DATAHUB_GMS_TOKEN", "")
    mutation_enabled: bool = os.getenv("TOOLS_IS_MUTATION_ENABLED", "true").lower() == "true"
    # public, reproducible demo data (fetch_data.py); override via env for other sources
    matches_db: str = os.getenv("MATCHES_DB", str(_DATA / "matches.db"))
    generality_db: str = os.getenv("GENERALITY_DB", str(_DATA / "generality.db"))
    # optional author-private sources (not needed for any demo)
    tr_odds_db: str = os.getenv("TR_ODDS_DB", "")
    iddaa_db: str = os.getenv("IDDAA_DB", "")

    def require_gms(self) -> None:
        if not self.gms_url:
            raise RuntimeError("DATAHUB_GMS_URL not set — is the DataHub quickstart running?")
        import urllib.request

        try:  # fail fast with a friendly message instead of a deep SDK traceback
            urllib.request.urlopen(self.gms_url.rstrip("/") + "/health", timeout=3)
        except Exception:
            raise RuntimeError(
                f"DataHub GMS not reachable at {self.gms_url}. Start it with "
                f"`bash scripts/quickstart_up.sh` (or set DATAHUB_GMS_URL)."
            )

    @property
    def odds_db(self) -> str:
        """The odds DB the demos read: private TR_ODDS_DB if set, else public matches.db."""
        return self.tr_odds_db or self.matches_db


CONFIG = Config()
