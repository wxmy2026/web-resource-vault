---
name: morning-music-butler
description: Run a low-friction morning music routine on macOS, skipping playback when the user is already active on iPad, learning from Apple Music favorites, and falling back to Spotify.
metadata:
  os: [darwin, ipadOS]
  category: personal-assistant
---

# Morning Music Butler

Use this skill for the user's morning music routine.

## Desired experience

- At 08:00, play gentle music only if the user has not already started using the iPad that morning.
- Prefer Apple Music and a calm mix derived from favorited tracks in the local Music library.
- If there are too few usable favorite tracks, use a known gentle Studio Ghibli solo-piano album.
- If Apple Music playback fails because of subscription, sign-in, or catalog availability, fall back to Spotify.
- Keep playback volume at 28%.
- Never start audio after 08:30.
- The routine is a seven-day block, renewable with one click.

## iPad activity gate

iPadOS Shortcuts does not expose a device-unlock trigger. The native low-friction approximation is an App-open personal automation on the iPad:

1. Select several apps the user commonly opens first after unlocking the iPad.
2. Run without asking.
3. Save/overwrite any small text value to `iCloud Drive/MorningMusicButler/ipad-active.txt`.

The Mac checks that file's modification timestamp before playback. If it was modified since local midnight, the user is treated as already active and the 08:00 music is skipped.

Do not claim this detects the passcode unlock event itself; it detects the first selected app open/switch after unlock.

## Personalization

`RefreshFavorites.applescript` rebuilds `Morning Music Butler • Favorites Mix` from tracks in the local Apple Music library that are marked `favorited` (or legacy `loved`). It keeps favorite tracks whose genre suggests a calm morning fit (ambient, classical, soundtrack, instrumental, easy listening, new age, piano, acoustic, jazz, folk and Chinese equivalents), or whose stored BPM is between 1 and 105.

The filtering is intentionally conservative. It is a starting point inferred from explicit favorites, not a claim that ChatGPT can directly read the user's private Apple Music account through the catalog connector.

The mix is refreshed on install and every time the user renews the routine for another week.

## Install

Run `scripts/install-morning-music-butler.command` on the Mac. The installer:

1. Compiles `MorningMusicButler.app` with a stable bundle identifier.
2. Compiles `Renew Morning Music Week.app` into `~/Applications`.
3. Copies the favorites refresh and week-renew scripts into `~/Library/Application Support/MorningMusicButler`.
4. Creates a seven-day 08:00 LaunchAgent schedule.
5. Creates the iCloud Drive folder used by the iPad activity marker.
6. Installs Spotify with Homebrew if Spotify is missing and Homebrew is available.
7. Opens the helper once so macOS can request Automation permission for Music and Spotify.

Expected human-only actions are macOS permission approval, music-service sign-in if needed, and the one-time iPad Shortcut personal-automation setup required by iPadOS.

## One-click repeat

`~/Applications/Renew Morning Music Week.app` is the repeat button. Clicking it:

1. Refreshes the favorites-derived morning mix.
2. Replaces the LaunchAgent schedule with the next seven 08:00 mornings.
3. Shows a completion notification.

No terminal work is required after initial installation.

## Playback order

At a scheduled run:

1. Reject runs outside 07:55–08:30.
2. Check the iCloud iPad activity marker; if it was touched today, stop with no audio.
3. Try `Morning Music Butler • Favorites Mix` when it contains at least five tracks.
4. Verify that Music reports `player state = playing`.
5. If needed, try `One Summer's Day: Studio Ghibli Favourites for Solo Piano by Joe Hisaishi` in Apple Music.
6. Verify playback again.
7. If Apple Music still fails, activate Spotify and play the configured gentle fallback album.
8. Never claim playback succeeded without player-state evidence.

## Safety and reliability

- Do not use UI click coordinates.
- Do not bypass DRM, authentication, subscriptions, or access controls.
- Do not store passwords, tokens, or cookies in the repository.
- macOS Automation permission must be granted to the compiled helper app.
- iPad unlock status is not directly exposed by iPadOS Shortcuts; use only documented event triggers.
