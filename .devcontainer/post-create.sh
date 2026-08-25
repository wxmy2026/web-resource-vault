#!/usr/bin/env bash
set -euo pipefail

mkdir -p "$HOME/.local/bin" "$HOME/workspace"

# Keep setup idempotent and fast. The universal Codespaces image already ships
# with Git, GitHub CLI, Python, Node, Java, Go, Rust and common build tools.
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y -qq ffmpeg jq ripgrep tree sqlite3 shellcheck >/dev/null
fi

python3 -m pip install --user --upgrade pip >/dev/null 2>&1 || true

cat > "$HOME/.local/bin/ipad-status" <<'EOF'
#!/usr/bin/env bash
printf 'iPad Workstation ready\n\n'
printf 'Git:      '; git --version | head -1
printf 'Python:   '; python3 --version
printf 'Node:     '; node --version
printf 'GitHub:   '; gh --version | head -1
printf 'Docker:   '; docker --version 2>/dev/null || echo 'starting / unavailable'
printf 'FFmpeg:   '; ffmpeg -version 2>/dev/null | head -1 || true
printf '\nRepo: %s\n' "$(pwd)"
EOF
chmod +x "$HOME/.local/bin/ipad-status"

grep -q 'HOME/.local/bin' "$HOME/.zshrc" 2>/dev/null || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"

echo
echo '=================================================='
echo ' iPad Workstation is ready.'
echo ' Run: ipad-status'
echo '=================================================='
