#!/usr/bin/env bash
#
# Generate /etc/systemd/system/ncc.service from the location of this project
# (the directory containing ncc.py) and the Python interpreter that runs it.
#
# Usage:
#   ./install_service.sh          # install the unit (uses sudo)
#   ./install_service.sh --print  # print the unit and exit (no sudo)
#
set -euo pipefail

# Directory containing ncc.py, i.e. the absolute path of the project as it
# exists on disk -- independent of the directory the script was invoked from.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
NCC_PATH="$SCRIPT_DIR/ncc.py"

if [[ ! -f "$NCC_PATH" ]]; then
    echo "Error: ncc.py not found next to this script ($NCC_PATH)" >&2
    exit 1
fi

# Prefer the active virtualenv (or the first python on PATH) so the service
# uses the same interpreter/dependencies that ran the bot.
PYTHON_BIN="${PYTHON_BIN:-$(command -v python || command -v python3)}"
# Resolve to an absolute path, but keep the venv symlink intact (do not
# follow it to the base interpreter, or the venv's packages would be lost).
PYTHON_BIN="$(realpath -s -- "$PYTHON_BIN")"

SERVICE_NAME="ncc.service"
UNIT_PATH="/etc/systemd/system/$SERVICE_NAME"
TMP_UNIT="$(mktemp)"
trap 'rm -f "$TMP_UNIT"' EXIT

cat > "$TMP_UNIT" <<EOF
[Unit]
Description=NCC Discord Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$(id -un)
Group=$(id -gn)
WorkingDirectory=$SCRIPT_DIR
EnvironmentFile=-$SCRIPT_DIR/.env
Environment=PYTHONUNBUFFERED=1
ExecStart=$PYTHON_BIN $NCC_PATH
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

if [[ "${1:-}" == "--print" ]]; then
    cat "$TMP_UNIT"
    exit 0
fi

sudo install -m 0644 "$TMP_UNIT" "$UNIT_PATH"
sudo systemctl daemon-reload

echo "Wrote $UNIT_PATH"
echo "  WorkingDirectory: $SCRIPT_DIR"
echo "  ExecStart:        $PYTHON_BIN $NCC_PATH"
echo
echo "Enable and start it with:"
echo "  sudo systemctl enable --now $SERVICE_NAME"
