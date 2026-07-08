#!/usr/bin/env bash
# Bring up local OSS DataHub (quickstart) + print MCP wiring.
# Docs: https://docs.datahub.com/docs/quickstart
set -euo pipefail

echo "==> Checking Docker daemon..."
if ! docker info >/dev/null 2>&1; then
  echo "Docker daemon not running. Start Docker Desktop:  open -a Docker"
  exit 1
fi

echo "==> Installing DataHub CLI (in a venv is fine)..."
python3 -m pip install --quiet 'acryl-datahub[datahub-rest]'

echo "==> Starting DataHub quickstart (this pulls images on first run)..."
datahub docker quickstart

cat <<'EOF'

==> DataHub should be at http://localhost:9002 (UI) / http://localhost:8080 (GMS)
    Default login: datahub / datahub

==> MCP server wiring (add to your Claude/Cursor MCP config):
    command: uvx
    args:    ["mcp-server-datahub@latest"]
    env:
      DATAHUB_GMS_URL=http://localhost:8080
      DATAHUB_GMS_TOKEN=<create in UI: Settings → Access Tokens>
      TOOLS_IS_MUTATION_ENABLED=true

==> Next: ingest a demo table:   python ingest/sqlite_to_datahub.py
    Then milestone 1:            python scripts/milestone1.py
EOF
