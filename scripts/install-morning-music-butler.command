#!/bin/bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This installer is for macOS."
  exit 1
fi

project_dir="$(cd "$(dirname "$0")/.." && pwd)"
source_script="$project_dir/skills/morning-music-butler/MorningMusicButler.applescript"
app_dir="$HOME/Applications"
app="$app_dir/MorningMusicButler.app"
plist_dir="$HOME/Library/LaunchAgents"
plist="$plist_dir/com.wxmy2026.morning-music-butler.plist"
state_dir="$HOME/Library/Application Support/MorningMusicButler"
log_file="$state_dir/morning-music.log"

mkdir -p "$app_dir" "$plist_dir" "$state_dir"

if [[ ! -d /Applications/Spotify.app ]] && command -v brew >/dev/null 2>&1; then
  echo "Installing Spotify as the fallback player..."
  brew install --cask spotify || true
fi

rm -rf "$app"
osacompile -o "$app" "$source_script"
/usr/libexec/PlistBuddy -c 'Delete :CFBundleIdentifier' "$app/Contents/Info.plist" >/dev/null 2>&1 || true
/usr/libexec/PlistBuddy -c 'Add :CFBundleIdentifier string com.wxmy2026.MorningMusicButler' "$app/Contents/Info.plist"
codesign --force --deep --sign - "$app" >/dev/null

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
  <array>
    <string>$app/Contents/MacOS/applet</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
$(printf '%b' "$calendar_entries")  </array>
  <key>StandardOutPath</key>
  <string>$log_file</string>
  <key>StandardErrorPath</key>
  <string>$log_file</string>
</dict>
</plist>
PLIST

plutil -lint "$plist"
launchctl bootout "gui/$(id -u)" "$plist" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$plist"
launchctl enable "gui/$(id -u)/com.wxmy2026.morning-music-butler" || true

echo
echo "One-time permission step: macOS may ask whether MorningMusicButler can control Music/Spotify. Choose Allow."
if [[ -d /Applications/Spotify.app ]]; then
  open -a Spotify >/dev/null 2>&1 || true
  sleep 2
fi
open "$app"
sleep 4

echo
echo "Installed. It will run at 08:00 for the next seven mornings."
echo "Primary: Apple Music — One Summer's Day: Studio Ghibli Favourites for Solo Piano."
echo "Fallback: Spotify — the matching Studio Ghibli solo-piano album."
echo "Playback volume: 28%."
echo "If the Mac is asleep at 08:00, launchd may run on wake; the app refuses to start audio after 08:30."
echo
read -r -p "Press Return to close this window."
