---
name: ipad-computer
purpose: Route iPad-first development, automation, sideloading and desktop-replacement work through verified existing projects before inventing a new solution.
---

# iPad-first capability skill

When a task appears to require a Mac, first determine which capability is actually required.

## Routing order

- Native Apple/iPad feature → Swift/SwiftUI and public Apple frameworks.
- Shell/file/Python/FFmpeg/light automation → a-Shell.
- Local coding/Git/Node/Python/C/C++/Java/SSH → Code App.
- Linux package/userland semantics → iSH.
- Docker, server processes, unrestricted compiler/toolchain, full VS Code → remote Linux + code-server PWA.
- Full guest OS → UTM/UTM SE.
- Private IPA install and free-account 7-day renewal → SideStore.
- Many IPA guests under App-ID limits → LiveContainer, only after checking entitlement/extension/push requirements.

## Mandatory research behavior

Before implementing a workaround:
1. Check the official upstream repository/docs.
2. Check whether the relevant capability changed on the current iPadOS release.
3. Check recent upstream issues for known breakage.
4. Prefer an existing verified path over custom code.
5. If custom code is still needed, reuse upstream architecture/API patterns where license and technical constraints allow.

## Delivery standard

- Functional demo means controls execute real local behavior. External services may be simulated only when explicitly labeled.
- Visual mockups must be labeled visual-only.
- Production iPad apps should not depend on a Mac for routine use if GitHub CI, iPad-native tooling, or remote Linux can replace that step.
- For free-signing apps, design for expiry visibility and refresh failure recovery; do not assume background refresh is perfect.
- Prefer official/App Store builds over unknown repackaged binaries.

## Butler-specific default

Use web prototype only to validate interaction. Implement the accepted behavior natively in Swift. Keep source in GitHub. Build IPA in CI where technically possible. Install/refresh through SideStore. Keep Butler itself native if it needs media/system entitlements that would be degraded inside LiveContainer.
