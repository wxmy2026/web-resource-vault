# Verified upstream projects

Checked 2026-08-26. Prefer these upstreams over reposts or tutorial forks.

| Capability | Upstream | Default branch | License noted by GitHub/upstream | Role |
|---|---|---|---|---|
| iPad Unix terminal | https://github.com/holzschu/a-shell | master | BSD-3-Clause | Native/lightweight shell and automation |
| iPad Linux userland | https://github.com/ish-app/ish | master | upstream-specific / inspect before redistribution | Alpine/Linux compatibility |
| iPad local IDE | https://github.com/thebaselab/codeapp | main | MIT | Local coding, Git, languages, SSH |
| Browser VS Code | https://github.com/coder/code-server | main | MIT | Full remote development environment |
| iOS/iPadOS VMs | https://github.com/utmapp/UTM | main | Apache-2.0 plus bundled component licenses | Windows/Linux VM/emulation |
| Sideload + refresh | https://github.com/SideStore/SideStore | develop | AGPL-3.0 | IPA install and 7-day refresh workflow |
| Multi-app launcher | https://github.com/LiveContainer/LiveContainer | main | AGPL-3.0 | Reduce App-ID pressure / run guest apps |

## High-value upstream documents

- code-server iPad guide: `coder/code-server/docs/ipad.md`
- a-Shell README: sandbox/bookmarks, Shortcuts, languages, package model and WebAssembly limitations
- Code App README: supported local runtimes, Git, SSH and LSP
- SideStore README: signing/refresh architecture and 7-day development period
- LiveContainer README: installation model, multitasking, compatibility and entitlement/extension/push limitations
- UTM README: QEMU features and UTM SE/JIT tradeoff
- iSH README: x86 user-mode emulation/syscall translation and build model

## Trust rule

For future iPad system/sideloading questions, check the official upstream repository, current README/docs, releases and recent issues before relying on blog posts, videos, mirrors or repackaged builds.
