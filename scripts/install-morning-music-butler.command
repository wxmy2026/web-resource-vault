#!/bin/bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This installer is for macOS."
  exit 1
fi

project_dir="$(cd "$(dirname "$0")/.." && pwd)"
skill_dir="$project_dir/skills/morning-music-butler"
source_script="$skill_dir/MorningMusicButler.applescript"
renew_app_source="$skill_dir/RenewMorningMusicWeek.applescript"
app_dir="$HOME/Applications"
app="$app_dir/MorningMusicButler.app"
renew_app="$app_dir/Renew Morning Music Week.app"
state_dir="$HOME/Library/Application Support/MorningMusicButler"
ipad_flag_dir="$HOME/Library/Mobile Documents/com~apple~CloudDocs/MorningMusicButler"

mkdir -p "$app_dir" "$state_dir" "$ipad_flag_dir"
cp "$skill_dir/RefreshFavorites.applescript" "$state_dir/RefreshFavorites.applescript"
cp "$skill_dir/renew-week.sh" "$state_dir/renew-week.sh"
chmod +x "$state_dir/renew-week.sh"

if [[ ! -d /Applications/Spotify.app ]] && command -v brew >/dev/null 2>&1; then
  echo "Installing Spotify as the fallback player..."
  brew install --cask spotify || true
fi

rm -rf "$app" "$renew_app"
osacompile -o "$app" "$source_script"
osacompile -o "$renew_app" "$renew_app_source"

/usr/libexec/PlistBuddy -c 'Delete :CFBundleIdentifier' "$app/Contents/Info.plist" >/dev/null 2>&1 || true
/usr/libexec/PlistBuddy -c 'Add :CFBundleIdentifier string com.wxmy2026.MorningMusicButler' "$app/Contents/Info.plist"
/usr/libexec/PlistBuddy -c 'Delete :CFBundleIdentifier' "$renew_app/Contents/Info.plist" >/dev/null 2>&1 || true
/usr/libexec/PlistBuddy -c 'Add :CFBundleIdentifier string com.wxmy2026.RenewMorningMusicWeek' "$renew_app/Contents/Info.plist"
codesign --force --deep --sign - "$app" >/dev/null
codesign --force --deep --sign - "$renew_app" >/dev/null

# Build the first seven-day schedule and refresh the calm mix from Apple Music favorites.
/bin/bash "$state_dir/renew-week.sh"

echo
echo "One-time permission step: macOS may ask whether MorningMusicButler can control Music/Spotify. Choose Allow."
if [[ -d /Applications/Spotify.app ]]; then
  open -a Spotify >/dev/null 2>&1 || true
  sleep 2
fi
open "$app"
sleep 4

echo
echo "Installed."
echo "• 08:00 for the next seven mornings."
echo "• If today's iPad activity marker exists in iCloud Drive, music is skipped."
echo "• Apple Music first: a gentle mix rebuilt from your favorited library tracks."
echo "• If the mix is too small, a Studio Ghibli solo-piano album is used."
echo "• If Apple Music cannot play, Spotify is the fallback."
echo "• Playback volume: 28%."
echo "• '$renew_app' is your one-click 'another week' button."
echo "• If the Mac wakes late, playback is blocked after 08:30."
echo
echo "One remaining iPadOS setup: create an App-open personal automation that overwrites"
echo "iCloud Drive/MorningMusicButler/ipad-active.txt whenever you start using a common app."
echo "Apple does not expose a device-unlock trigger, so this is the closest reliable native signal."
echo
open -R "$renew_app" >/dev/null 2>&1 || true
read -r -p "Press Return to close this window."
