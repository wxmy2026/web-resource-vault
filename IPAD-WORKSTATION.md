# iPad Workstation

This repository is configured to become a browser-based Linux development workstation on iPad through GitHub Codespaces.

## One-click launch

Open:

https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=1346435472

Choose the smallest available machine unless a task needs more CPU/RAM. GitHub personal accounts include a monthly Codespaces allowance; the environment automatically stops when idle according to the account timeout.

## What is preconfigured

- Browser VS Code on iPad
- Linux terminal
- Git + GitHub CLI
- Python + Jupyter
- Node.js / JavaScript / TypeScript
- Java, Go, Rust and common build tools from the universal image
- Docker-in-Docker
- FFmpeg, jq, ripgrep, tree, sqlite3, shellcheck
- Forwarded preview ports: 3000, 5173, 8000, 8080
- Auto-save and iPad-friendly word wrap

After creation, run:

```bash
ipad-status
```

## iPad usage

Safari is sufficient. For a more app-like experience, add the Codespaces editor page to the iPad Home Screen. Keep the terminal inside VS Code when possible so iPadOS does not suspend a separate terminal app while switching windows.

## Division of labor

Use the iPad/Codespaces workstation first for Git, Python, Node, Docker, web development, file processing, automation, servers and general Linux work.

Use native iPad tools when they are better: Swift Playground for SwiftUI prototypes, a-Shell for quick local shell/file tasks, and iSH for a local Alpine-like shell.

Use SideStore/LiveContainer only for sideloading/private iOS app workflows. They do not turn iPadOS into macOS and should not be treated as a general Linux environment.

Use a Mac only when Apple specifically requires Xcode/macOS-only signing, frameworks, simulators or other capabilities that cannot be moved to GitHub Actions/Codespaces.
