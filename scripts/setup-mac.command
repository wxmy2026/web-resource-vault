#!/bin/bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This setup file is for macOS."
  exit 1
fi

project_dir="$(cd "$(dirname "$0")/.." && pwd)"
cd "$project_dir"

if ! command -v brew >/dev/null 2>&1; then
  echo "Installing Homebrew from its official installer..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [[ -x /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi
fi

echo "Installing the first-stage desktop apps..."
brew bundle --file "$project_dir/Brewfile"

python3 -m venv "$project_dir/.venv"
"$project_dir/.venv/bin/python" -m pip install --upgrade pip
"$project_dir/.venv/bin/python" -m pip install -r "$project_dir/requirements.txt"

vault_dir="$HOME/PersonalAI/Vault"
mkdir -p "$vault_dir"

echo
echo "Setup complete."
echo "Apps: Obsidian, Anki, Krita, AnythingLLM"
echo "Resource vault: $vault_dir"
echo "Project: $project_dir"
read -r -p "Press Return to close this window."

