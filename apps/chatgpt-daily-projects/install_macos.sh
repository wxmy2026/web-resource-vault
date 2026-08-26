#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV="$ROOT/.venv"
PYTHON="${PYTHON:-python3}"
PLIST="$HOME/Library/LaunchAgents/com.tree.chatgpt-daily-projects.plist"
LOGDIR="$HOME/.chatgpt-daily-projects"

mkdir -p "$LOGDIR" "$HOME/Library/LaunchAgents"

"$PYTHON" -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/pip" install -r "$ROOT/requirements.txt"
"$VENV/bin/python" -m playwright install chromium

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.tree.chatgpt-daily-projects</string>
  <key>ProgramArguments</key>
  <array>
    <string>$VENV/bin/python</string>
    <string>$ROOT/runner.py</string>
    <string>--job</string>
    <string>all</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$ROOT</string>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>8</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>$LOGDIR/launchd.out.log</string>
  <key>StandardErrorPath</key>
  <string>$LOGDIR/launchd.err.log</string>
  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>
EOF

launchctl bootout "gui/$UID/com.tree.chatgpt-daily-projects" 2>/dev/null || true
launchctl bootstrap "gui/$UID" "$PLIST"
launchctl enable "gui/$UID/com.tree.chatgpt-daily-projects"

echo
echo "Installed. One final setup step will open a dedicated Chromium profile."
echo "Sign in to ChatGPT once; the login remains stored locally on this Mac."
"$VENV/bin/python" "$ROOT/runner.py" --login

echo
echo "Testing both jobs now (one fresh chat in each Project)..."
"$VENV/bin/python" "$ROOT/runner.py" --job all --force

echo
echo "Setup complete. macOS will run both jobs daily at 08:00 local Mac time."
echo "Logs: $LOGDIR/runner.log"
