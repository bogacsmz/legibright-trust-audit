#!/usr/bin/env bash
# Legibright — one-command demo-catalog reset. Run this BEFORE recording (and before every
# retake) so the DataHub catalog always starts from the exact same clean state: no stale/
# duplicate incidents, correct agent profile, and fresh verdicts on all 3 demo datasets.
# Silent and fast — no banners, no pauses. For the on-camera driver, use `run_demo.sh`.
#
#   bash demo/reset_demo.sh
#
# Prereqs: DataHub quickstart up (localhost:8080/9002) and `python scripts/fetch_data.py` once.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE"
export PYTHONPATH="$HERE/src"
export DATAHUB_GMS_URL="${DATAHUB_GMS_URL:-http://localhost:8080}"
export DATAHUB_GMS_TOKEN="${DATAHUB_GMS_TOKEN:-}"
export MATCHES_DB="${MATCHES_DB:-$HERE/data/matches.db}"
export GENERALITY_DB="${GENERALITY_DB:-$HERE/data/generality.db}"
PY="${PY:-python3}"

echo "Legibright demo reset"
echo "  python: $($PY -c 'import sys;print(sys.executable)')"
echo "  GMS:    $DATAHUB_GMS_URL"

if ! $PY -c "import trust_layer" 2>/dev/null; then
  echo "  ! trust_layer not importable — run: pip install -e '.[dev]'  (or set PY=)"; exit 1
fi
if [ ! -f "$MATCHES_DB" ]; then
  echo "  fetching public demo data (one-time)…"; $PY scripts/fetch_data.py
fi

echo; echo "1/4 — wiping stale/duplicate incidents on the 3 demo datasets..."
$PY scripts/cleanup_incidents.py

echo; echo "2/4 — resetting agent profile (Legibright / Trust Auditor + avatar)..."
$PY scripts/set_agent_avatar.py | head -1

echo; echo "3/4 — rebuilding fresh verdicts..."
$PY scripts/demo_writeback.py >/dev/null
echo "  matches: audited"
$PY scripts/generality_check.py >/dev/null
echo "  titanic + bikeshare: audited"

sleep 3   # let DataHub's relationship index catch up before reading it back

echo; echo "4/4 — verifying the clean state..."
$PY - <<'PYEOF'
from trust_layer.config import CONFIG
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig, RelationshipDirection
from datahub.metadata import schema_classes as S

g = DataHubGraph(DataHubGraphConfig(server=CONFIG.gms_url, token=CONFIG.gms_token))
EXPECTED = {"matches": 28, "titanic": 25, "bikeshare": 100}
ok = True
for name, want in EXPECTED.items():
    urn = f"urn:li:dataset:(urn:li:dataPlatform:sqlite,main.{name},PROD)"
    sp = g.get_aspect(urn, S.StructuredPropertiesClass)
    raw = next((v.values[0] for v in (sp.properties if sp else []) if "trust_score" in v.propertyUrn), None)
    got = int(raw) if raw is not None else None
    incs = len(list(g.get_related_entities(urn, ["IncidentOn"], RelationshipDirection.INCOMING)))
    mark = "OK" if got == want else "MISMATCH"
    if got != want:
        ok = False
    print(f"  {name:10s} Trust Score {got} (want {want}) [{mark}] · {incs} incident(s)")

owner_of = 0
for name in EXPECTED:
    urn = f"urn:li:dataset:(urn:li:dataPlatform:sqlite,main.{name},PROD)"
    own = g.get_aspect(urn, S.OwnershipClass)
    if own and any(o.owner == "urn:li:corpuser:trust-layer-agent" for o in own.owners):
        owner_of += 1
print(f"  agent owns {owner_of}/3 datasets")
print()
print("READY TO RECORD" if ok and owner_of == 3 else "NOT CLEAN — see mismatches above")
PYEOF
