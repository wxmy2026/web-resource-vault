---
name: morning-music-butler
description: Control gentle morning music on macOS, preferring Apple Music and falling back to Spotify when Apple Music playback is unavailable.
metadata:
  os: [darwin]
  category: personal-assistant
---

# Morning Music Butler

Use this skill when the user asks the personal AI workbench to start, schedule, pause, or troubleshoot gentle morning music on their Mac.

## Current routine

- Time: 08:00 local Mac time.
- Duration: the installer creates seven morning calendar entries.
- Primary player: Apple Music.
- Primary target: `One Summer's Day: Studio Ghibli Favourites for Solo Piano by Joe Hisaishi`.
- Apple Music target: `https://music.apple.com/us/album/one-summers-day-studio-ghibli-favourites-for-solo-piano/1583121575`.
- Fallback player: Spotify desktop app.
- Spotify fallback target: `spotify:album:6PyXSCnrQoKNQWyrZl4GTs`.
- Playback volume: 28% inside the selected music app.
- Late-wake guard: do not start audio outside 07:55–08:30.

The Ghibli/solo-piano choice is intentionally calm, melodic, cinematic, and suitable for waking rather than acting as a harsh alarm.

## Install

Run `scripts/install-morning-music-butler.command` on the Mac. The installer:

1. Compiles `MorningMusicButler.applescript` into a local signed app bundle with a stable bundle identifier.
2. Installs Spotify with Homebrew when Spotify is missing and Homebrew is available.
3. Creates a per-user LaunchAgent with seven explicit 08:00 calendar entries.
4. Opens the helper once so macOS can ask for Automation permission to control Music and Spotify.

The only expected human action is approving macOS permission dialogs and signing in to a music service if that service is not already signed in.

## Playback behavior

At a scheduled run:

1. Hand the exact Apple Music album deep link to Music.
2. Set Music volume to 28% and attempt playback.
3. Verify that Music reports `player state = playing`.
4. If Apple Music does not start, activate Spotify, set volume to 28%, enable shuffle, and play the Spotify album URI.
5. Verify that Spotify reports `player state = playing`.
6. Never claim playback succeeded without player-state evidence.

This treats a missing/expired Apple Music subscription, sign-in problem, or failed catalog playback the same way: Apple Music is attempted first, and Spotify is the fallback.

## Safety and reliability

- Do not use UI click coordinates.
- Do not bypass DRM, authentication, subscriptions, or access controls.
- Do not store account passwords, tokens, or cookies in the repository.
- macOS Automation permission must be granted to the compiled `MorningMusicButler.app`; this is why the scheduled job uses an app bundle rather than a raw background shell script.
- If the Mac sleeps through 08:00, launchd may deliver the event after wake. The helper refuses to start audio after 08:30 to avoid surprising late playback.
