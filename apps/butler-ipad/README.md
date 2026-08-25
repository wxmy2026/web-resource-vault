# Butler for iPad

Private, local-first iPad companion for the Personal AI Workbench.

## Goal

One private app on the user's iPad acts as the control surface for personal automations and skills. It is not intended for App Store distribution.

## Architecture

- **Butler iPad app**: SwiftUI UI, local settings, local skill registry, MusicKit authorization/playback, quiet-day controls, and future Apple-platform integrations.
- **Skill registry**: small Codable definitions stored locally. Most new Butler features should be added as skills/configuration rather than separate apps.
- **Mac Butler Agent (optional but important)**: performs actions iPadOS cannot reliably do in the background, including exact-time desktop automation and cross-app scripting.
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

The app must not pretend it can globally observe device unlocks or arbitrary activity in other apps. iPadOS sandboxing does not expose a general "device unlocked" event to third-party apps. When an action needs privileges iPadOS doesn't provide, the app should show the limitation and hand the action to the Mac Butler Agent when available.

## Installation

Source can be prepared and updated in GitHub while the Mac is unavailable. Final private installation onto the iPad requires an Apple-supported signing path. The intended path is Xcode on the user's Mac with the user's Apple ID; no App Store listing is required.
