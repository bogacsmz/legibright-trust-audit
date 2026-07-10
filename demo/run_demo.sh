#!/usr/bin/env bash
# Legibright — reproducible demo driver. Runs the three on-camera beats from a clean state.
# Idempotent (deterministic entity keys), so it produces the SAME verdicts every run — record
# take 1, 2, or 3 and they match. Narrate over it; the script just drives the screen.
#
#   bash demo/run_demo.sh                 # run straight through (stability testing)
#   DEMO_PAUSE=1 bash demo/run_demo.sh    # pause between beats for narration
#   PY=/opt/anaconda3/bin/python3 DEMO_PAUSE=1 bash demo/run_demo.sh
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
export REVENUE_DB="${REVENUE_DB:-$HERE/data/revenue.db}"
PY="${PY:-python3}"

# indigo brand banner (Legibright #1E1B4B), white text — reads well on camera
banner() { printf '\n\033[48;5;17m\033[1;97m  %-64s\033[0m\n\n' "$1"; }
pause()  { if [ "${DEMO_PAUSE:-0}" = "1" ]; then printf '\033[2;37m   ⏵ Enter for the next beat…\033[0m'; read -r _; fi; }

banner "LEGIBRIGHT · make model trust legible"
echo "   python: $($PY -c 'import sys;print(sys.executable)')"
echo "   GMS:    $DATAHUB_GMS_URL"
if ! $PY -c "import trust_layer" 2>/dev/null; then
  echo "   ! trust_layer not importable — run: pip install -e '.[dev]'  (or set PY=)"; exit 1
fi
if [ ! -f "$MATCHES_DB" ] || [ ! -f "$REVENUE_DB" ]; then
  echo "   fetching public demo data (one-time)…"; $PY scripts/fetch_data.py
fi
$PY scripts/set_agent_avatar.py 2>/dev/null | head -1 || echo "   (avatar step skipped — GMS not ready?)"
pause

banner "BEAT 1 · a revenue model that looks GREAT → Legibright says NO"
$PY scripts/demo_revenue.py
pause

banner "BEAT 2 · an HONEST model → Legibright says YES  (it does not cry wolf)"
echo "   Same auditor, a genuinely clean model (Bike Sharing) and a leaky one (Titanic):"
echo "   — proof it discriminates, on public datasets unrelated to betting."
echo
$PY scripts/generality_check.py
pause

banner "BEAT 3 · the trust tool survives its OWN audit"
echo "   3-round adversarial self-audit + demo/UI hardening + delta audit → 15 real flaws fixed, 6 honest limits documented."
echo "   Nothing was loosened to go green. Run it yourself:"
echo
$PY -m pytest tests/ -q | tail -1
$PY scripts/verify_all.py | tail -3
echo
echo "   Full ledger: docs/VERIFICATION.md"
pause

banner "See it in the graph → $DATAHUB_GMS_URL  (UI: http://localhost:9002)"
echo "   main.revenue → Quality (2 assertions FAIL) · Incidents (ACTIVE) · Tags · Trust Score 28/100 · deprecation proposal"
echo "   Legibright — make model trust legible.   github.com/bogacsmz/legibright-trust-audit"
