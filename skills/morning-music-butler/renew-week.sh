#!/bin/bash
set -euo pipefail

app="$HOME/Applications/MorningMusicButler.app"
plist="$HOME/Library/LaunchAgents/com.wxmy2026.morning-music-butler.plist"
state_dir="$HOME/Library/Application Support/MorningMusicButler"
log_file="$state_dir/morning-music.log"
refresh_script="$state_dir/RefreshFavorites.applescript"

mkdir -p "$(dirname "$plist")" "$state_dir"

if [[ -f "$refresh_script" ]]; then
  /usr/bin/osascript "$refresh_script" >/dev/null 2>&1 || true
fi

now_hhmm=$(date '+%H%M')
start_offset=0
if ((10#$now_hhmm >= 800)); then
  start_offset=1
fi

calendar_entries=""
for i in 0 1 2 3 4 5 6; do
  offset=$((start_offset + i))
  month=$(date -v+"${offset}"d '+%m' | sed 's/^0//')
  day=$(date -v+"${offset}"d '+%d' | sed 's/^0//')
  calendar_entries+="    <dict><key>Month</key><integer>${month}</integer><key>Day</key><integer>${day}</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>\n"
done

cat > "$plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.wxmy2026.morning-music-butler</string>
  <key>ProgramArguments</key>
  <array><string>$app/Contents/MacOS/applet</string></array>
  <key>StartCalendarInterval</key>
  <array>
$(printf '%b' "$calendar_entries")  </array>
  <key>StandardOutPath</key><string>$log_file</string>
  <key>StandardErrorPath</key><string>$log_file</string>
</dict>
</plist>
PLIST

plutil -lint "$plist" >/dev/null
launchctl bootout "gui/$(id -u)" "$plist" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$plist"
launchctl enable "gui/$(id -u)/com.wxmy2026.morning-music-butler" || true
