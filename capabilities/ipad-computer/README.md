# iPad Computer Capability Library

Purpose: make iPad the primary workstation and reduce Mac dependency. This folder is the persistent capability index for future Butler/iPad work.

## Default routing

1. **Native iPad app / Apple frameworks** → Swift / SwiftUI. Prototype behavior first, then build IPA in GitHub Actions where practical.
2. **Shell, Python, file processing, FFmpeg, lightweight automation** → a-Shell first.
3. **Local code editing + Git + Node/Python/C/C++/Java/SSH** → Code App.
4. **Linux userland compatibility** → iSH.
5. **Full VS Code / Docker / unrestricted Linux toolchain** → code-server on a remote Linux host; iPad is the client/PWA.
6. **Run Windows/Linux locally on iPad** → UTM/UTM SE; use only when a VM is genuinely needed because iPadOS JIT restrictions can reduce performance.
7. **Private IPA installation / 7-day free-development signing** → SideStore. Treat refresh as the primary renewal path, but design Butler to surface expiry/refresh failures rather than assuming background refresh is infallible.
8. **Many sideloaded apps under limited App IDs** → evaluate LiveContainer. Do not use it for Butler features that depend on guest entitlements, app extensions, or remote push.

## Upstreams studied

- `holzschu/a-shell` — Unix-like terminal on iOS/iPadOS; Python, Lua, JS, C/C++ via WebAssembly, TeX, file bookmarks, Shortcuts integration. Important limits: iOS sandbox; WebAssembly has no normal fork/socket support; Python packages with native extensions are constrained.
- `thebaselab/codeapp` — iPad code editor with Git, terminal, local Node/PHP, Python, C/C++ WebAssembly, Java, SSH and LSP.
- `ish-app/ish` — Alpine/Linux shell through user-mode x86 emulation and syscall translation. Useful when Linux userland/package semantics matter more than native iPad integration.
- `coder/code-server` — VS Code in a browser. Official project has a dedicated iPad guide and recommends using it as a Home Screen PWA. Best route when Docker/server tooling or a full Linux environment is required.
- `utmapp/UTM` — QEMU-based system emulator/VM host. UTM SE avoids JIT requirements but is slower.
- `SideStore/SideStore` — untethered-oriented sideloading. Uses a personal development certificate and periodically refreshes apps to prevent the normal 7-day development period expiring.
- `LiveContainer/LiveContainer` — launcher that can run multiple iOS apps inside one host app/App ID. Useful for App-ID pressure; guest entitlements/extensions/remote push have limitations.

## Butler architecture decision

Butler should remain a normal native iPad app when it needs system/media capabilities. Web prototypes are for interaction validation only. The production pipeline should prefer:

`interactive web prototype → native Swift implementation → GitHub-hosted source → CI build where feasible → IPA → SideStore → automatic refresh + expiry guard`

The prototype must clearly distinguish real behavior from simulated external-account integrations.

## What not to do by default

- Do not require Mac just because a traditional tutorial uses Xcode on Mac; first check iPad-native, GitHub Actions, and remote-Linux paths.
- Do not jailbreak or depend on version-specific exploits unless there is a concrete capability that cannot be achieved safely another way.
- Do not present a visual-only mockup as a functional demo.
- Do not vendor random third-party IPA builds when an official upstream or App Store build exists.

See `UPSTREAMS.md` for source locations and `bootstrap.sh` for a one-command source checkout on a machine/iPad environment that has Git and network access.
