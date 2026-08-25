# Butler for iPad

Private, local-first iPad companion for the Personal AI Workbench.

## Goal

One private app on the user's iPad acts as the control surface for personal automations and skills. It is not intended for App Store distribution.

## Architecture

- **Butler iPad app**: SwiftUI UI, local settings, local skill registry, MusicKit authorization/playback, quiet-day controls, and future Apple-platform integrations.
- **Skill registry**: small Codable definitions stored locally. Most new Butler features should be added as skills/configuration rather than separate apps.
- **iPad-first execution**: prefer iPad-native frameworks and local rules. Do not require a Mac for normal Butler use.
- **GitHub cloud build**: GitHub Actions generates the Xcode project and builds an unsigned device IPA on a hosted macOS/Xcode runner.
- **SideStore path**: the unsigned IPA is intended to be signed/refreshed on-device with the user's free Apple development certificate after SideStore's one-time bootstrap.
- **Mac Butler Agent (optional)**: only for macOS-specific automation or Apple platform capabilities that cannot be reproduced on iPad/cloud infrastructure.
- **Cloud/ChatGPT (optional)**: used only for reasoning, recommendation generation, or downloading updated skill definitions. Existing local rules should remain usable without it.

## First skill

`Morning Music`:

- default time: 08:00
- one-tap enable/disable
- one-tap "Quiet today"
- one-tap "Run another week"
- Apple Music personalization through MusicKit after user authorization
- Spotify fallback will use Spotify's official iOS App Remote flow after explicit authorization

## iPadOS boundary

The app must not pretend it can globally observe device unlocks or arbitrary activity in other apps. iPadOS sandboxing does not expose a general "device unlocked" event to third-party apps. When an action needs privileges iPadOS doesn't provide, Butler should use an allowed signal or explain the limitation rather than fake detection.

## Build

`project.yml` is the reproducible XcodeGen project definition. `.github/workflows/build-butler-ipa.yml` builds a real unsigned iPad IPA in GitHub Actions whenever Butler source changes, and also supports manual dispatch.

Build output: `Butler-unsigned-ipa` artifact containing `Butler-unsigned.ipa` plus its SHA-256 checksum.

## Installation direction

The target flow is: test the interactive web demo -> approve the UX -> GitHub builds `Butler-unsigned.ipa` -> SideStore signs/installs it on iPad -> SideStore periodically refreshes the free 7-day certificate. A Mac is not part of the normal development/build loop; it may still be needed once for SideStore bootstrap depending on the current SideStore installation path and iPadOS version.
